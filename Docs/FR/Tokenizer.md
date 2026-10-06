# Encoder et reconstruire du texte byte-level

`AI.Tokenizer` charge un alphabet byte-level immuable, encode du texte UTF-8
en IDs `int[]` et reconstruit les octets ou le texte normalisé. Les modèles
BPE byte-level offrent la normalisation `identity` (par défaut), NFC ou NFKC,
et la pré-tokenisation `none` (par défaut) ou `gpt2`. Le couple vocabulaire/règles
est validé une fois au chargement ; aucun fichier n’est relu durant l’encodage.

## Charger, encoder et décoder

Fournissez `vocab.json` et `merges.txt` dans le répertoire courant à l’exécution.
Le vocabulaire est un objet JSON associant les symboles de l’alphabet byte-level
GPT-2 à des IDs entiers uniques non négatifs. Il couvre les 256 octets ; son
fichier de fusions contient des paires de symboles ordonnées, éventuellement
précédées de `#version: 0.2` ; un fichier vide conserve un token par octet.
Ce programme traite un modèle fourni par l’application :

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.load_bpe("vocab.json", "merges.txt") else error {
        panic(error.detail)
    }
    let encoding = try tokenizer.encode("Bonjour é 世界 👩‍💻") else error {
        panic(error.detail)
    }
    let decoded = try tokenizer.decode(encoding.ids()) else error {
        panic(error.detail)
    }
    print(decoded)
    print("$(encoding.count()) tokens")
}
```

La sortie contient `Bonjour é 世界 👩‍💻`, puis `29 tokens`. Sans fusion,
un token représente un octet ; un caractère multioctet produit donc plusieurs
IDs. Les tokens du modèle peuvent également désigner plusieurs octets au
décodage, même s’ils ne sont pas émis par ce premier encodeur.

Un [consommateur exécutable](../../Tests/TokenizerConsumer/Example.sx) fournit
le même parcours avec un alphabet miniature versionné. Depuis la racine du
workspace de développement, en liant les candidats AI/STD/JSON à ce workspace :

```sh
silex run Packages/AI/Tests/TokenizerConsumer/Example.sx
silex test Packages/AI/Tests/TokenizerConsumer
```

La qualification de développement utilise les candidats AI et STD. Les nouveaux
appels `Dictionary.find`, `Text.UTF8.byte_count` et les nouvelles capacités Regex
doivent être disponibles dans
la version de STD choisie lors de la publication ; cette surface ne prétend pas
être installable depuis le tag AI 0.1.0 déjà existant.

## Charger un modèle incorporé en mémoire

`Tokenizer.parse_bpe(vocabulary_json, merges_text, options)` analyse les mêmes
formats et applique les mêmes limites que `load_bpe`, sans ouvrir de fichiers.
Il convient à un modèle incorporé avec `embed_text` ou à un contenu déjà lu par
l’application. `LoadError.path` est absent pour cette entrée en mémoire et
présent lorsqu’un fichier est concerné.

Le [parcours en mémoire](../../Tests/TokenizerConsumer/InMemoryRoundTrip.sx)
incorpore le même alphabet et vérifie IDs, spans, 256 octets et décodage strict.
La qualification compare sa sortie dans l’interpréteur de référence et dans les
binaires Debug/Release ; le chargement depuis le système de fichiers reste natif.

## Choisir la normalisation et le découpage du modèle

Les champs `LoadOptions.normalization` et `pre_tokenizer` fixent les choix à la
création du modèle ; ils restent immuables durant ses encodages. Gardez la
configuration employée lors de l’entraînement du modèle. NFC compose les
équivalents canoniques ; NFKC transforme aussi les formes de compatibilité,
par exemple `ﬁ` en `fi`, `Ａ` en `A` et `¼` en `1⁄4`. Le décodage restitue le
texte normalisé ; ces transformations ne permettent pas de retrouver la forme
originale. Les tables proviennent de `STD.Text`, Unicode 17.0.0.

Ce [programme exécutable](../../Tests/TokenizerConsumer/TextPipelineExample.sx)
normalise puis inspecte les frontières du profil GPT-2 :

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.parse_bpe(embed_text("Fixtures/vocab.json"), "",
        Tokenizer.LoadOptions(normalization:Tokenizer.Normalization.nfkc,
            pre_tokenizer:Tokenizer.PreTokenizer.gpt2)) else error { panic(error.detail) }
    let encoding = try tokenizer.encode("ﬁ  世界") else error { panic(error.detail) }
    print(encoding.normalized_text())
    for segment in encoding.segments() { print("$(segment.start):$(segment.end)") }
}
```

Sortie :

```text
fi  世界
0:2
2:3
3:10
```

`encoding.segments()` rend une liste détachée de `Span`, couvrant le texte
normalisé de manière contiguë. `none` produit un segment sur toute l’entrée
non vide ; `gpt2` produit les frontières ci-dessous. Une entrée vide n’a aucun
segment. Sans fusion, chaque octet reste un token, quel que soit ce découpage.

### Profil GPT-2 exact

Le motif ordonné, sensible à la casse, vient de
[Transformers 2.10.0](https://huggingface.co/transformers/v2.10.0/_modules/transformers/tokenization_gpt2.html) :

```text
's|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+
```

`L` et `N` désignent les catégories Unicode complètes ; `N` inclut les nombres
non décimaux. `\s` suit `White_Space` Unicode 17.0.0, et `\S` son complément.
L’espace optionnel avant mots, nombres ou symboles est uniquement U+0020.
Aucun espace initial n’est ajouté et aucun espace n’est supprimé. Ainsi
`we're  ici` produit `we`, `'re`, ` ` et ` ici` ; les contractions en majuscules
ne sont pas reconnues par les alternatives minuscules.

Le motif est compilé une fois lors du chargement par `STD.Regex`. L’assertion
négative `(?!\S)` est évaluée exactement sur le scalaire suivant. Les 25
caractères `White_Space`, NUL, marques combinantes et emoji/ZWJ font partie des
fixtures ; FEFF et 001C ne sont pas des blancs Unicode. La référence de fixtures
indépendante Node utilise Unicode 16.0 sur des caractères stables sélectionnés :
elle qualifie ce corpus, pas le tokenizer GPT-2 complet ni toute Unicode 17.

## Appliquer les fusions du modèle

L’ordre des lignes de `merges.txt` définit le rang. Parmi les paires actuellement
admissibles, le rang le plus bas gagne ; à rang égal, l’occurrence la plus à
gauche est fusionnée. Une fusion peut rendre une nouvelle paire admissible,
même si sa règle apparaît plus tôt. Aucune fusion ne traverse les frontières de
pré-tokenisation. Les doublons, références inconnues et résultats absents du
vocabulaire sont refusés au chargement.

Ce [programme exécutable](../../Tests/TokenizerConsumer/BPEExample.sx) charge
une fixture miniature où `a b` produit l’ID 256 et `ab c` l’ID 258 :

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.parse_bpe(embed_text("Fixtures/bpe-vocab.json"),
        "a b\nab c\n") else error { panic(error.detail) }
    let encoding = try tokenizer.encode("abc") else error { panic(error.detail) }
    for piece in encoding.pieces() {
        print(piece.id)
        print("$(piece.span!.start):$(piece.span!.end)")
    }
    print(try tokenizer.decode(encoding.ids()) else error { panic(error.detail) })
}
```

Sortie :

```text
258
0:3
abc
```

Le modèle sans règle conserve un token par octet. Avec des fusions,
`maximum_tokens` borne le nombre final de tokens ; deux octets fusionnés peuvent
ainsi tenir dans une limite d’un token. Les octets d’un morceau fusionné et son
span couvrent exactement les morceaux contigus remplacés. Un morceau peut
encore couper un scalaire UTF-8 ; inspectez ses octets ou décodez toute la séquence.
Les tables et candidats de fusion restent privés, sans cache global mutable.

## Inspecter l’encodage

`encoding.ids()` rend une liste détachée utilisable par une frontière de modèle.
`encoding.pieces()` rend des valeurs `Piece` avec `id`, `bytes` et `span` ;
`encoding.count()` compte les tokens. `normalized_text()` donne le texte auquel
les spans se rapportent, après la normalisation choisie.

Un `Span` est un intervalle `[start, end)` en **octets UTF-8**, pas en scalaires,
UTF-16 ou graphèmes. Par exemple, `é` produit deux morceaux d’un octet, de spans
`[0, 1)` et `[1, 2)`. Les octets de chacun ne forment pas séparément du UTF-8
valide. Les contrôles présents dans le texte ont un span ; BOS/EOS ajoutés
n’en ont pas. `Piece.special` identifie le rôle du contrôle, ou reste absent
pour un morceau ordinaire. `tokenizer.special_tokens()` fournit les descriptions
configurées dans une liste détachée.

`decode_bytes(ids)` préserve les octets. `decode(ids)` les valide strictement :
un ID inconnu ou une séquence UTF-8 invalide rend un `DecodeError`, sans
remplacement silencieux. Sa `position` est l’indice d’ID pour un ID inconnu ou
une limite de sortie, et l’offset d’octet pour une erreur UTF-8.

Le tokenizer conserve son modèle et n’emprunte pas les chemins ou l’entrée.
Le partager ne modifie aucun état ; les listes rendues et les encodages ont
leur propre sémantique de valeur. Aucune opération du sous-module ne requiert
Tensor, GFX, GPU ou Python ; les dépendances des autres modules AI demeurent.

## Fixer les limites et traiter les erreurs

`Tokenizer.load_bpe` retourne `Result<Tokenizer, LoadError>`. `kind`, `path` et
`detail` distinguent I/O, options invalides, JSON, vocabulaire, alphabet incomplet,
règles ou contrôles invalides et limite dépassée.
Les IDs fractionnaires, hors plage ou dupliqués, tokens vides/hors alphabet,
fusions inconnues ou dupliquées sont refusés avant usage.

`LoadOptions` borne chaque fichier à 16 MiB, la profondeur JSON à 32, les entrées
et règles à 100 000, et chaque token à 4 096 octets. Les contrôles sont bornés à 256 descriptions
et 65 536 octets de surfaces cumulées (`maximum_special_tokens`,
`maximum_special_bytes`) ; la limite par token s’applique aussi à leur surface.
Les champs sont configurables.
La lecture est bornée même si un fichier grandit ; les limites d’entrées sont
contrôlées après l’analyse JSON, déjà bornée par taille et profondeur.

`EncodeOptions` borne les octets d’entrée et du texte normalisé à 16 MiB chacun
(`maximum_input_bytes`, `maximum_normalized_bytes`), et les tokens à 16 Mi par
défaut ; `DecodeOptions` borne les octets de sortie à 16 MiB. Les limites
négatives renvoient une erreur d’options. Les appels sans options gardent ces
valeurs par défaut. La taille brute est vérifiée avant la normalisation, puis la
taille normalisée
avant le découpage et les tokens. La normalisation peut créer ses résultats
intermédiaires avant ce second contrôle ; le volume reste borné par l’entrée
et les tables Unicode. Le décodage vérifie la capacité restante avant d’ajouter un
token.

## Configurer et autoriser les contrôles

`LoadOptions.special_tokens` associe chaque surface non vide à un ID non négatif
et au rôle `bos`, `eos`, `padding`, `unknown` ou `control("nom")`. IDs, surfaces
et rôles sont uniques ; les collisions avec IDs, symboles ou octets ordinaires
sont refusées. Un rôle nommé exige un nom non vide. Les surfaces doivent déjà
être stables sous la normalisation du modèle. Les contrôles sont reconnus dans
le texte normalisé, avant son découpage ; la surface la plus longue gagne,
puis l’ordre du modèle. Une surface identique ne peut pas être configurée deux fois.

`EncodeOptions.special_input` vaut `SpecialInput.reject` par défaut : une surface
littérale reconnue rend `forbidden_special`. `SpecialInput.allow([ids])` autorise
uniquement les contrôles listés ; les IDs inconnus ou répétés rendent une erreur
d’options. `SpecialInput.ordinary_text` traite toutes ces surfaces comme du texte
ordinaire. Aucune politique n’injecte automatiquement BOS/EOS.

`boundary_tokens` choisit `BoundaryTokens.none`, `bos`, `eos` ou `bos_and_eos`.
Un rôle demandé mais absent rend une erreur d’options, même sur entrée vide.
Les contrôles ajoutés comptent dans la limite de tokens et n’ont pas de span.
`DecodeOptions.special_tokens` choisit `DecodeSpecialTokens.include` (défaut)
ou `skip` ; seuls les IDs configurés sont ignorés, jamais les IDs inconnus.
Les rôles padding/unknown décrivent des contrôles ; ils n’activent ni padding
ni remplacement d’octets inconnus.

Ce [programme exécutable](../../Tests/TokenizerConsumer/SpecialExample.sx)
ajoute explicitement BOS/EOS puis reconstruit uniquement le texte :

```sx
use AI.Tokenizer

func main() {
    var tokenizer = try Tokenizer.parse_bpe(embed_text("Fixtures/bpe-vocab.json"), "a b\nab c\n",
        Tokenizer.LoadOptions(special_tokens:[
            Tokenizer.SpecialToken(surface:"<bos>", id:1000, role:Tokenizer.SpecialRole.bos),
            Tokenizer.SpecialToken(surface:"<eos>", id:1001, role:Tokenizer.SpecialRole.eos)
        ])) else error { panic(error.detail) }
    let encoding = try tokenizer.encode("abc", Tokenizer.EncodeOptions(
        boundary_tokens:Tokenizer.BoundaryTokens.bos_and_eos)) else error { panic(error.detail) }
    for piece in encoding.pieces() { print(piece.id) }
    print(try tokenizer.decode(encoding.ids(), Tokenizer.DecodeOptions(
        special_tokens:Tokenizer.DecodeSpecialTokens.skip)) else error { panic(error.detail) })
}
```

Sortie : `1000`, `258`, `1001`, puis `abc`.

## Compatibilité vérifiée

L’[oracle épinglé](../../Tests/TokenizerConsumer/Fixtures/Oracle/README.md)
Tokenizers **0.22.1** vérifie 594 cas du modèle synthétique : identité/NFC/NFKC,
ByteLevel avec ou sans regex, sans préfixe automatique, contrôles normalisés et
template BOS/EOS explicite. IDs, octets des morceaux et décodages inclus/ignorés
sont comparés. Les offsets UTF-8 normalisés sont prouvés localement, sans reprendre
l’unité de l’oracle. La compatibilité reste limitée à ce modèle et ces options ;
les outils Python servent uniquement à régénérer les fixtures de développement.
Aucun entraînement, téléchargement de modèle, padding, batching ou conversion
tensorielle n’est fourni. Les modèles restent des fichiers appartenant à
l’application.

[Revenir à l’index AI](README.md)

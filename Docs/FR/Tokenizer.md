# Encoder et reconstruire du texte byte-level

`AI.Tokenizer` charge un alphabet byte-level immuable, encode du texte UTF-8
en IDs `int[]` et reconstruit les octets ou le texte exact. Cette première
surface prend en charge les modèles **sans règle de fusion**, la normalisation
`identity` et aucun pré-découpage. Un modèle contenant des fusions est refusé
avec `LoadErrorKind.unsupported_model` : ses règles ne sont jamais ignorées.

## Charger, encoder et décoder

Fournissez `vocab.json` et `merges.txt` dans le répertoire courant à l’exécution.
Le vocabulaire est un objet JSON associant les symboles de l’alphabet byte-level
GPT-2 à des IDs entiers uniques non négatifs. Il couvre les 256 octets ; son
fichier de fusions est vide ou contient seulement `#version: 0.2`.
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
appels `Dictionary.find` et `Text.UTF8.byte_count` doivent être disponibles dans
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

## Inspecter l’encodage

`encoding.ids()` rend une liste détachée utilisable par une frontière de modèle.
`encoding.pieces()` rend des valeurs `Piece` avec `id`, `bytes` et `span` ;
`encoding.count()` compte les tokens. `normalized_text()` donne le texte auquel
les spans se rapportent, ici exactement l’entrée.

Un `Span` est un intervalle `[start, end)` en **octets UTF-8**, pas en scalaires,
UTF-16 ou graphèmes. Par exemple, `é` produit deux morceaux d’un octet, de spans
`[0, 1)` et `[1, 2)`. Les octets de chacun ne forment pas séparément du UTF-8
valide. Le type optionnel du span réserve l’absence de source aux futurs tokens
injectés ; tous les morceaux de cette première surface ont un span.

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
règles invalides, limite dépassée et modèle non encore pris en charge.
Les IDs fractionnaires, hors plage ou dupliqués, tokens vides/hors alphabet,
fusions inconnues ou dupliquées sont refusés avant usage.

`LoadOptions` borne chaque fichier à 16 MiB, la profondeur JSON à 32, les entrées
et règles à 100 000, et chaque token à 4 096 octets. Les champs sont configurables.
La lecture est bornée même si un fichier grandit ; les limites d’entrées sont
contrôlées après l’analyse JSON, déjà bornée par taille et profondeur.

`EncodeOptions` borne les octets d’entrée à 16 MiB et le nombre de tokens à 16 Mi
par défaut ; `DecodeOptions` borne les octets de sortie à 16 MiB. Les limites
négatives renvoient une erreur d’options. Les appels sans options gardent ces
valeurs par défaut. L’encodage compte les octets avant de matérialiser les listes,
et le décodage vérifie la capacité restante avant d’ajouter un token.

## Compatibilité de cette première surface

NFC/NFKC, pré-tokenisation GPT-2, fusions BPE, tokens spéciaux et BOS/EOS ne sont
pas encore disponibles. Le nom byte-level décrit l’alphabet et l’aller-retour ;
il ne constitue pas une qualification différentielle du pipeline GPT-2 complet.
Aucun entraînement, téléchargement de modèle, padding, batching ou conversion
tensorielle n’est fourni. Les modèles restent des fichiers appartenant à
l’application.

[Revenir à l’index AI](README.md)

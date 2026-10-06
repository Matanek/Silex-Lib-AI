# Oracle différentiel du tokenizer

Oracle indépendant **Hugging Face Tokenizers 0.22.1**, modèle synthétique sans
entraînement ni téléchargement. `model.json` épingle le vocabulaire par SHA-256,
les fusions et les six contrôles. `cases.json` conserve IDs, tokens, octets et
décodages pour 33 entrées, six profils et trois politiques : **594 cas**.

Les profils combinent identité/NFC/NFKC avec ByteLevel `use_regex=false/true`,
sans préfixe automatique et sans cache BPE. Les contrôles sont des AddedToken
normalisés, sans single_word, lstrip ou rstrip ; le template demandé ajoute
uniquement BOS puis EOS. Le traitement ordinaire utilise l’oracle sans
AddedToken. La normalisation des surfaces configurées reste stable.

Le corpus couvre anglais, français, contractions, nombres Unicode, ponctuation,
blancs, CR/LF, NUL, CJK, arabe, emoji/ZWJ, texte décomposé, répétitions et contrôles
chevauchants. Les morceaux ordinaires de l’oracle sont reconvertis par l’alphabet
byte-level bijectif ; ceux des contrôles sont leurs surfaces UTF-8. Les offsets de
l’oracle ne sont pas comparés : les tests locaux vérifient spans contigus,
frontières de segments et absence de span pour les contrôles ajoutés.

`Tests/Oracle.sx` et `OracleParity*.sx` sont générés depuis cet oracle, avec
assertions d’IDs, octets et décodage inclus/ignoré. Les tests ordinaires et
l’application n’appellent aucun outil Python. Les outils présents ici sont
réservés au développement et ne font pas partie du module installable.

Depuis ce répertoire de fixtures, dans un environnement temporaire :

```sh
python3 -m venv /tmp/ai-tokenizer-oracle
/tmp/ai-tokenizer-oracle/bin/python -m pip install -r requirements.txt
PYTHONDONTWRITEBYTECODE=1 /tmp/ai-tokenizer-oracle/bin/python Generate.py
```

Vérifier ensuite l’absence de diff sur les fixtures et sources générées, puis
exécuter depuis la racine du workspace :

```sh
silex test Packages/AI/Tests/TokenizerConsumer
python3 Packages/AI/Tests/TokenizerConsumer/Fixtures/Oracle/CheckInterpreter.py
silex run Packages/AI/Tests/TokenizerConsumer/OracleParityIdentityNone.sx --release --nocache
```

Cette preuve porte sur ce modèle et ces options. Elle ne qualifie ni tous les
modèles Tokenizers, ni toutes les propriétés Unicode d’une autre version.

Répéter la commande native pour les six fichiers `OracleParity*.sx`.
`CheckInterpreter.py` n’exige que la bibliothèque standard Python et exécute
les 594 appels gelés dans des processus séparés. Cette qualification facultative
borne l’arène conservée par l’interpréteur de référence ; une exécution groupée
de certains profils dépasse cette arène. Les tests ordinaires natifs restent
autonomes et n’appellent pas ce script. Utiliser `--silex /chemin/absolu/silex`
pour une toolchain candidate, et `--evidence /chemin/absolu/resultats.json`
pour conserver les sorties.

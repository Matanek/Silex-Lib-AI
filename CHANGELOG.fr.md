# Historique des changements

## [Unreleased]

- Adopte la déclaration `Result` unique : l’appel ordinaire rend la valeur
  ou arrête le programme sur erreur ; `try appel()` conserve le `Result`. Les
  anciens appels stockant un résultat et propagations deviennent explicites.
  Cette révision requiert la toolchain de développement avec cette sémantique
  de `try` ; sa publication doit coordonner les versions du compilateur et des
  packages.

- Ajouter `AI.Tokenizer` : modèles BPE byte-level immuables chargés depuis
  fichiers ou mémoire, normalisation identity/NFC/NFKC et découpage none/GPT-2,
  IDs portables, morceaux et spans UTF-8 possédés, décodage octets ou UTF-8 strict.
- Appliquer les fusions par rang puis occurrence gauche, dans les frontières
  de pré-tokenisation ; erreurs structurées et limites configurables contrôlent
  modèles externes, entrées et sorties. Le budget total comprend les contrôles
  et BOS/EOS, après fusion lorsque nécessaire, avant les morceaux finaux.
- Configurer des contrôles immuables avec rôles, autorisation explicite, ajout
  BOS/EOS et décodage inclus/ignoré. L’oracle Tokenizers 0.22.1 épinglé qualifie
  594 cas du modèle synthétique ; Python reste réservé aux outils de développement.
- Fournir le consommateur public, les guides FR/EN et une campagne native
  reproductible avec exécutions séquentielles bornées. Le tokenizer utilise STD
  et JSON ; les autres modules conservent leurs dépendances.
- Ajouter `AI.Evolution` pour classer et sélectionner des génomes applicatifs,
  conserver les élites et composer croisement/mutation déterministes.
- Ajouter `AI.NeuroEvolution.FixedStructure` pour faire évoluer les paramètres
  de `Tensor.Neural`, puis `AI.NeuroEvolution.EvolvingStructure` pour suivre
  innovations, mutations structurelles, croisement et spéciation feed-forward.
  Le nom FixedStructure explicite la frontière de l’adaptateur.

Le tokenizer reste une surface de développement : AI 0.1.0 publié ne le contient
pas et STD 0.22.0 publié ne fournit pas toutes les API requises. La prochaine
version AI sera au minimum 0.2.0, après qualification de ses prérequis publiés ;
aucun tag existant n’acquiert rétroactivement ces ajouts.

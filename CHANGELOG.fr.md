# Historique des changements

## [Unreleased]

- Ajouter `AI.Tokenizer` pour charger un alphabet byte-level complet sans fusion,
  analyser aussi un modèle en mémoire, encoder en IDs portables et décoder les
  octets ou du UTF-8 strict. Encodages
  possédés avec spans UTF-8, erreurs structurées et limites configurables.
- Valider vocabulaire et fusions ; refuser explicitement les modèles contenant
  des fusions tant que leur encodage n’est pas qualifié. Normalisation Unicode,
  pré-tokenisation et contrôles restent hors de cette première surface.
- Ajouter un consommateur public et un guide FR/EN. Les nouveaux appels STD
  requis seront pris en compte lors de la préparation de version ; aucun tag
  existant n’acquiert rétroactivement le tokenizer.

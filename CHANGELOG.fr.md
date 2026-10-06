# Historique des changements

## [Unreleased]

- Vérifier le budget total comprenant contrôles et BOS/EOS avant les morceaux
  finaux, après fusion lorsque nécessaire ; qualifier les seuils exacts et
  entrées hostiles.

- Ajout des contrôles immuables avec rôles, politiques explicites, BOS/EOS et décodage inclus/ignoré ; oracle Tokenizers 0.22.1 épinglé sur 594 cas multilingues et adversariaux, sans dépendance Python dans les appels ou tests ordinaires.

- Appliquer les fusions BPE par rang puis occurrence gauche, en conservant les
  frontières et spans ; borner les tokens après fusion, sans rescannage global.

- Ajouter les choix immuables `identity`/NFC/NFKC et `none`/GPT-2 au chargement ;
  exposer les spans de segments du texte normalisé et borner sa taille séparément.

- Ajouter `AI.Tokenizer` pour charger un alphabet byte-level complet,
  analyser aussi un modèle en mémoire, encoder en IDs portables et décoder les
  octets ou du UTF-8 strict. Encodages
  possédés avec spans UTF-8, erreurs structurées et limites configurables.
- Valider vocabulaire et fusions ; refuser explicitement les modèles contenant
  des fusions tant que leur encodage n’est pas qualifié. Normalisation Unicode,
  pré-tokenisation et contrôles restent hors de cette première surface.
- Ajouter un consommateur public et un guide FR/EN. Les nouveaux appels STD
  requis seront pris en compte lors de la préparation de version ; aucun tag
  existant n’acquiert rétroactivement le tokenizer.

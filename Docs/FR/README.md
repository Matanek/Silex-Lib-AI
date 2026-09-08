# AI

`AI` possède le namespace des capacités d’intelligence artificielle de Silex.
Cette première version établit uniquement la frontière du package : elle ne
présente encore aucun algorithme comme disponible.

Les capacités futures resteront séparées selon leur intention. Un outil de
comportement ne dépendra donc pas artificiellement d’un moteur de tenseurs, et
une intégration ECS appartiendra à une couche optionnelle plutôt qu’au noyau.

[Read this documentation in English.](../EN/README.md)

## Développement

Depuis la racine du workspace :

```text
silex link Packages/AI
silex link Packages/AI --workspace Packages/AI/Tests/Consumer
silex test Packages/AI/Tests/Consumer
```

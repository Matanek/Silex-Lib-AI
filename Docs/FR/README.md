# AI

`AI` rassemble des capacités d’intelligence artificielle modulaires. Les
mécaniques de comportement et d’évolution restent indépendantes du domaine ;
une intégration explicite relie les génomes aux modèles `Tensor.Neural`.

## Capacités

- [Construire et exécuter un Behaviour Tree](BehaviourTree.md)
- [Faire évoluer une population](Evolution.md)
- [Faire évoluer les paramètres d’un réseau à structure fixe](NeuroEvolution-FixedStructure.md)
- [Faire évoluer la structure d’un réseau](NeuroEvolution-EvolvingStructure.md)

[Read this documentation in English.](../EN/README.md)

## Développement

Depuis la racine du workspace :

```text
silex link Packages/AI
silex link Packages/AI --workspace Packages/AI/Tests/Consumer
silex test Packages/AI/Tests/Consumer
```

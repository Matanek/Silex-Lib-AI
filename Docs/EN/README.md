# AI

`AI` gathers modular artificial-intelligence capabilities. Behaviour and
evolution mechanics remain domain-independent; one explicit integration links
genomes to `Tensor.Neural` models.

## Capabilities

- [Build and run a Behaviour Tree](BehaviourTree.md)
- [Evolve a population](Evolution.md)
- [Evolve Tensor network parameters](Neuroevolution.md)

[Lire cette documentation en français.](../FR/README.md)

## Development

From the workspace root:

```text
silex link Packages/AI
silex link Packages/AI --workspace Packages/AI/Tests/Consumer
silex test Packages/AI/Tests/Consumer
```

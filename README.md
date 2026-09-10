# AI

`AI` provides modular Silex capabilities for autonomous agents.
`AI.BehaviourTree` builds typed behaviour definitions and independent execution
instances. `AI.Evolution` supplies deterministic ranking, elitism and tournament
selection around application-defined genomes, fitness, crossover and mutation.
`AI.NeuroEvolution.FixedStructure` adapts that generic engine to
`Tensor.Neural` parameter genomes while preserving the network structure.
`AI.NeuroEvolution.EvolvingStructure` provides direct, NEAT-inspired
feed-forward neuroevolution with innovation tracking, structural mutation,
crossover, and speciation.

Loading the root `AI` module also contributes the shared definition, the
per-agent instance, and the empty readiness marker as
`GFX.Resources.Behaviour`, `GFX.Components.Behaviour`, and
`GFX.Components.BehaviourReady`. Scheduling and context adaptation remain
application-owned; AI installs no GFX plugin.

```text
silex install AI
```

## Documentation

- [French documentation](Docs/FR/README.md)
- [English documentation](Docs/EN/README.md)

The package requires Silex 0.44.1 or newer.

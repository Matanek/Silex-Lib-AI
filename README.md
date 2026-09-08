# AI

`AI` provides modular Silex capabilities for autonomous agents. Its
`AI.BehaviourTree` module builds typed behaviour definitions and runs
independent execution instances while keeping the core separate from graphics
engines, ECS implementations, and numerical-computing engines.

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

The package requires Silex 0.44.0 or newer.

# AI

`AI` owns the namespace for Silex artificial-intelligence capabilities. This
first version establishes only the package boundary: it does not present any
algorithm as available yet.

Future capabilities will remain separated by intent. A behavior tool will not
artificially depend on a tensor engine, and ECS integration will belong to an
optional layer rather than the core.

[Lire cette documentation en français.](../FR/README.md)

## Development

From the workspace root:

```text
silex link Packages/AI
silex link Packages/AI --workspace Packages/AI/Tests/Consumer
silex test Packages/AI/Tests/Consumer
```

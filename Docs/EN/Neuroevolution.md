# Evolve neural-network parameters

`AI.Neuroevolution` connects the generic evolutionary engine to fixed-topology
`Tensor.Neural` models. `Genome.capture(model)` records named parameters and
`genome.apply(model)` injects them after complete name, shape, and count
validation.

```sx
use AI.Neuroevolution
use STD.Randomizer

let parent_a = Neuroevolution.Genome.capture(model_a)
let parent_b = Neuroevolution.Genome.capture(model_b)
var randomizer = Randomizer(42)
var child = Neuroevolution.uniform_crossover(parent_a, parent_b, randomizer)
Neuroevolution.gaussian_mutation(child, randomizer, probability:0.05)
child.apply(model_a)
```

Genomes deliberately remain on the CPU so randomness, inspection, and
transfers stay explicit. Call `model.cpu()` and release gradients with
`parameter.zero_grad()` on every parameter before capture or application, then
`model.to(device)` after application to evaluate on the GPU. Uniform crossover
chooses every scalar from either parent; Gaussian mutation adds noise with an
independent probability for every scalar.

This first surface evolves the values of an existing network. It does not
evolve topology and implements neither speciation nor NEAT-style innovation
markers.

[Back to the AI index](README.md)

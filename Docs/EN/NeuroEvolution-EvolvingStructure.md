# Evolve a network's structure

`AI.NeuroEvolution.EvolvingStructure` provides direct neuroevolution inspired
by NEAT. A population starts with minimal networks connecting the inputs and a
bias to the outputs, then evolves both their weights and graph.

```sx
use AI.NeuroEvolution.EvolvingStructure
use STD.Math

func fitness(genome:@EvolvingStructure.Genome) float {
    let output = genome.forward([0.25, -0.5])
    return -Math.abs(output[0] - 0.75)
}

let configuration = EvolvingStructure.Configuration(
    hidden_activation:EvolvingStructure.Activation.tanh,
    output_activation:EvolvingStructure.Activation.linear,
    add_connection_probability:0.05,
    add_node_probability:0.03
)
var population = EvolvingStructure.Population(2, 1, 100, 42, configuration)

while population.generation() < 100 {
    let evaluated = population.advance(fitness)
    print(evaluated.best().fitness())
}

let final_generation = population.evaluate(fitness)
let winner = final_generation.best()
let prediction = winner.genome().forward([0.25, -0.5])
```

## What evolves

Each `Genome` contains `NodeGene` and `ConnectionGene` values. Connections carry
an innovation identifier that remains stable within the population. This
history aligns homologous genes during crossover and identifies disjoint and
excess genes in the compatibility distance.

Two structural mutations complexify the network:

- adding a connection chooses a missing edge without introducing a cycle;
- adding a node disables one connection, inserts a hidden node, preserves the
  old weight on the outgoing connection, and gives the incoming connection a
  weight of `1.0`.

`Population.evaluate(score)` evaluates and ranks the current generation without
changing it. `Population.advance(score)` returns that evaluation, preserves the
best individual in every species, builds the next generation through
within-species tournaments and crossover, then applies mutations. Select the
score direction with `AI.Evolution.Goal.maximize` or `minimize`.

## Speciation and limits

The compatibility distance combines excess genes, disjoint genes, and the mean
weight difference between homologous genes. Its threshold and coefficients are
configurable. Species identifiers belong to one evaluation and are not stable
identities across generations.

This surface executes acyclic feed-forward graphs only. It does not yet support
recurrent connections, species age or stagnation, or indirect
Hypercube/HyperNEAT encoding. The latter belongs to the separate future
`AI.NeuroEvolution.Hypercube` surface.

The design follows the foundational mechanisms described in
[Evolving Neural Networks through Augmenting Topologies](https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf),
without claiming to reproduce every feature of a full NEAT implementation.

[Back to the AI index](README.md)

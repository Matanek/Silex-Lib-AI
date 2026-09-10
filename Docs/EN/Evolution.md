# Evolve a population

`AI.Evolution` provides generic genetic-algorithm mechanics without imposing a
genome representation or fitness function. A population ranks individuals,
preserves its elites, selects parents by tournament, then delegates crossover
and mutation to two synchronous callbacks.

```sx
use AI.Evolution
use STD.Randomizer

struct Genome { var value:float }

func fitness(genome:@Genome) float { return -genome.value * genome.value }
func crossover(left:@Genome, right:@Genome, randomizer:Randomizer) Genome {
    if randomizer.get_bool() { return left }
    return right
}
func mutate(genome:&Genome, randomizer:Randomizer) {
    genome.value += randomizer.get_float(-0.1, 0.1)
}

var initial:Genome[] = [Genome(value:-1.0), Genome(value:0.5)]
let configuration = Evolution.Configuration(elite_count:1, tournament_size:2)
var population = Evolution.Population<Genome>(initial, 42, configuration)
let evaluated = population.advance(fitness, crossover, mutate)
print(evaluated.best().fitness())
```

The population owns its seed: the same initial population, seed, and call
sequence reproduce the same selections. Callbacks may capture an evaluation
environment because they are used only during the call. Every fitness must be
finite. `Goal.minimize` reverses ranking; individuals returned by
`Generation.individuals()` always remain ordered from best to worst.

The genome must have safe value semantics: crossover produces a new child and
mutation changes only that child. The library does not guess domain
constraints, repair, or termination; consumers express them around `evaluate`
and `advance`.

[Back to the AI index](README.md)

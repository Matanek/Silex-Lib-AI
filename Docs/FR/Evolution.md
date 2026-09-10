# Faire évoluer une population

`AI.Evolution` fournit la mécanique générique d’un algorithme génétique sans
imposer la représentation du génome ni la fonction de fitness. Une population
classe les individus, conserve ses élites, sélectionne les parents par tournoi,
puis délègue le croisement et la mutation à deux callbacks synchrones.

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

La seed appartient à la population : une population initiale, une seed et la
même suite d’appels reproduisent les mêmes sélections. Les callbacks peuvent
capturer un environnement d’évaluation, car ils ne sont utilisés que pendant
l’appel. Toute fitness doit être finie. `Goal.minimize` inverse le classement ;
les individus rendus par `Generation.individuals()` restent toujours ordonnés
du meilleur au moins bon.

Le génome doit posséder une sémantique de valeur sûre : le croisement produit
un nouvel enfant et la mutation ne modifie que cet enfant. La bibliothèque ne
devine ni les contraintes du domaine, ni sa réparation, ni sa condition
d’arrêt ; le consommateur les exprime autour de `evaluate` et `advance`.

[Revenir à l’index AI](README.md)

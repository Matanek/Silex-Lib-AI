# Faire évoluer la structure d’un réseau

`AI.NeuroEvolution.EvolvingStructure` fournit une neuroévolution directe
inspirée de NEAT. Une population commence avec des réseaux minimaux reliant les
entrées et un biais aux sorties, puis peut faire évoluer leurs poids et leur
graphe.

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

## Ce qui évolue

Chaque `Genome` contient des `NodeGene` et des `ConnectionGene`. Les connexions
portent un identifiant d’innovation stable dans la population. Cet historique
permet d’aligner les gènes homologues pendant le croisement et de distinguer les
gènes disjoints ou excédentaires dans la distance de compatibilité.

Deux mutations structurelles complexifient le réseau :

- l’ajout d’une connexion choisit une arête absente sans créer de cycle ;
- l’ajout d’un nœud désactive une connexion, insère un nœud caché, conserve son
  poids sur la connexion sortante et donne le poids `1.0` à la connexion
  entrante.

`Population.evaluate(score)` évalue et classe la génération courante sans la
modifier. `Population.advance(score)` renvoie cette même évaluation, conserve
le meilleur individu de chaque espèce, produit la génération suivante par
tournoi et croisement au sein des espèces, puis applique les mutations. Le sens
du score se choisit avec `AI.Evolution.Goal.maximize` ou `minimize`.

## Spéciation et limites

La distance de compatibilité combine les gènes excédentaires, les gènes
disjoints et l’écart moyen des poids homologues. Le seuil et les coefficients
sont configurables. Les identifiants d’espèce sont propres à une évaluation et
ne constituent pas des identités persistantes entre générations.

Cette surface exécute uniquement des graphes feed-forward acycliques. Elle ne
prend pas encore en charge les connexions récurrentes, l’âge ou la stagnation
des espèces, ni l’encodage indirect Hypercube/HyperNEAT. Ce dernier appartient
à la future surface distincte `AI.NeuroEvolution.Hypercube`.

L’architecture reprend les mécanismes fondateurs décrits dans l’article
[Evolving Neural Networks through Augmenting Topologies](https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf),
sans prétendre reproduire toutes les variantes d’une implémentation NEAT
complète.

[Revenir à l’index AI](README.md)

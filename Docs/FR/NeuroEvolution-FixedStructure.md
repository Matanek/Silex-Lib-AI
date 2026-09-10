# Faire évoluer un réseau à structure fixe

`AI.NeuroEvolution.FixedStructure` relie le moteur génétique générique aux
modèles `Tensor.Neural` dont la structure reste fixe. `Genome.capture(model)`
relève les paramètres nommés et `genome.apply(model)` les réinjecte après
validation complète des noms, formes et compteurs.

```sx
use AI.NeuroEvolution.FixedStructure
use STD.Randomizer

let parent_a = FixedStructure.Genome.capture(model_a)
let parent_b = FixedStructure.Genome.capture(model_b)
var randomizer = Randomizer(42)
var child = FixedStructure.uniform_crossover(parent_a, parent_b, randomizer)
FixedStructure.gaussian_mutation(child, randomizer, probability:0.05)
child.apply(model_a)
```

Les génomes sont volontairement conservés sur CPU afin que la génération
aléatoire, l’inspection et les transferts restent explicites. Appelez
`model.cpu()` et libérez les gradients avec `parameter.zero_grad()` sur chaque
paramètre avant une capture ou une application, puis `model.to(device)` après
application pour évaluer sur GPU. Un croisement choisit chaque scalaire chez
l’un des deux parents ; la mutation ajoute un bruit gaussien selon une
probabilité indépendante par scalaire.

Cette première surface fait évoluer les valeurs d’un réseau existant. Elle ne
fait pas évoluer sa topologie et n’implémente ni spéciation ni marqueurs
d’innovation de type NEAT.

[Revenir à l’index AI](README.md)

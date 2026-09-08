# Construire et exécuter un Behaviour Tree

`AI.BehaviourTree` sépare une définition partagée de l’état propre à chaque
agent. Une définition décrit les conditions, actions et composites ; chaque
appel à `instantiate()` crée une instance d’exécution indépendante.

## Décrire un arbre

Une condition lit le contexte et retourne un booléen. Une action peut modifier
ce contexte et retourne `success`, `failure` ou `running`.

```sx
use AI.BehaviourTree

struct Creature {
    var hungry:bool
    var meals:int
}

func is_hungry(creature:@Creature) bool {
    return creature.hungry
}

func eat(creature:&Creature) BehaviourTree.Status {
    creature.hungry = false
    creature.meals++
    return BehaviourTree.Status.success
}

func create_behaviour() Result<BehaviourTree.Definition<Creature>, BehaviourTree.BuildError> {
    var builder = BehaviourTree.Builder<Creature>()
    builder.begin_sequence("eat when hungry")
    builder.condition("is hungry", is_hungry)
    builder.action("eat", eat)
    builder.end()
    return builder.build()
}
```

Une définition possède exactement une racine. `build()` retourne un
`BuildError` avant toute exécution lorsque la racine manque, qu’un composite
est vide ou mal fermé, qu’un `end()` est superflu, ou qu’un second nœud se
retrouve hors de la racine.

Les fonctions de condition et d’action sont conservées dans la définition.
Elles doivent donc être des fonctions nommées ou des fonctions anonymes non
capturantes. Leur état mutable appartient au `Context` fourni à l’évaluation ;
la définition ne conserve jamais ce contexte.

## Instancier et évaluer

```sx
var definition:BehaviourTree.Definition<Creature>? = null
match create_behaviour() {
    success(value) => { definition = value }
    failure(_) => { panic("invalid creature behaviour") }
}

var creature = Creature(hungry:true, meals:0)
var execution = definition!.instantiate()
let status = execution.evaluate(creature)

assert(status == BehaviourTree.Status.success)
assert(execution.status() == BehaviourTree.Status.success)
execution.reset()
assert(execution.status() == null)
```

Une séquence s’arrête au premier enfant `failure` ou `running` et réussit si
tous ses enfants réussissent. Un sélecteur s’arrête au premier enfant
`success` ou `running` et échoue si tous ses enfants échouent.

Plusieurs instances peuvent partager la même définition. Leur statut
d’exécution reste indépendant ; seul le contexte explicitement fourni à une
évaluation est modifié.

## Reprendre et interrompre une action

Lorsqu’une action retourne `running`, l’instance conserve cette feuille et le
chemin de composites qui y conduit. L’appel suivant à `evaluate` reprend
directement l’action : les conditions déjà résolues et les frères précédents ne
sont pas reparcourus.

Une action longue peut déclarer un hook d’abandon avec la surcharge à trois
arguments de `action`. Dans ce fragment, `Creature` possède un champ mutable
`patrol_reserved` et `patrol` désigne l’action longue :

```sx
func abandon_patrol(creature:&Creature) {
    creature.patrol_reserved = false
}

builder.action("patrol", patrol, abandon_patrol)
```

`execution.interrupt(creature)` appelle ce hook au plus une fois pour l’action
active, efface le chemin conservé et force la prochaine évaluation à repartir
de la racine. `reset(creature)` possède la même garantie d’abandon et remet
l’instance à son état initial. La forme `reset()` sans contexte convient à une
instance inactive ou terminale ; une action `running` exige la forme qui reçoit
le contexte afin que son hook puisse nettoyer son travail.

Le package ne choisit pas le moment de la reprise. Une boucle peut rappeler
l’instance à la frame suivante, tandis qu’un ordonnanceur peut attendre un
événement ou une échéance sans aucun travail intermédiaire dans l’arbre.

## Composer avec les catalogues GFX

Le module racine `AI` publie trois rôles dans les catalogues ouverts de GFX :

- `GFX.Resources.Behaviour<Context>` est exactement
  `AI.BehaviourTree.Definition<Context>` ;
- `GFX.Components.Behaviour<Context>` est exactement
  `AI.BehaviourTree.Instance<Context>` ;
- `GFX.Components.BehaviourReady` est exactement `AI.BehaviourReady`.

Ces noms décrivent le placement, sans envelopper ni dupliquer les objets. Une
application ECS peut donc conserver une seule définition en ressource, une
instance mutable par entité et le contexte de gameplay dans un composant
séparé. Le marqueur `BehaviourReady` ne contient aucune donnée métier : un
système de timer, de perception ou d’événement l’ajoute seulement aux agents
qui doivent reprendre, puis le système d’arbre le retire après l’évaluation.

```sx
use AI
use GFX.Components
use GFX.ECS
use GFX.Resources

var shared:@Resources.Behaviour<Creature> = resources.get<
    Resources.Behaviour<Creature>
>()

let entity = world.spawn(ECS.EntityRecipe()
    ..with(shared.instantiate())
    ..with(Components.BehaviourReady())
)

assert(world.has<Components.Behaviour<Creature>>(entity))
```

`AI` ne contribue aucun plugin : le package ne peut pas choisir comment
adapter un `World` à `Context`, ordonner les systèmes ni décider quelles
échéances réveillent un agent. Ces responsabilités restent dans
l’application. Un danger prioritaire peut, par exemple, cibler une entité,
appeler explicitement `interrupt(context)`, puis ajouter `BehaviourReady` pour
forcer la prochaine évaluation à repartir de la racine.

Le cœur reste utilisable directement avec `use AI.BehaviourTree` et son API ne
mentionne ni entité ni World. La dépendance de package `AI -> GFX` sert
uniquement à autoriser ces contributions aux catalogues publics.

## Borner le travail d’un appel

`advance(context, budget)` limite le nombre de nouveaux nœuds visités pendant
l’appel et rend l’épuisement explicite :

```sx
match execution.advance(creature, 8) {
    status(_) => { print("tree completed") }
    budget_exhausted => { print("resume later") }
}
```

`budget_exhausted` conserve la progression et ne constitue pas un
`Status.running` produit par une action. `evaluate` emploie automatiquement un
budget dérivé du nombre de nœuds préparés ; pour un arbre statique valide, ce
budget couvre un parcours ou une reprise ordinaire.

La définition aplatie et la profondeur maximale sont calculées une seule fois
par `build()`. `instantiate()` réserve ensuite le chemin nécessaire à l’agent :
les évaluations, reprises, interruptions et remises à zéro ordinaires ne font
pas croître ce stockage.

## Observer un parcours

La surcharge d’`evaluate` qui reçoit un callback signale `entered` lorsqu’un
nœud est visité puis `exited(Status)` lorsque sa progression produit un statut.
Le callback reçoit le nom public du nœud, jamais un indice interne. Une reprise
ne signale donc pas les conditions ni les frères déjà résolus ; seuls la
feuille active et les composites nécessaires à la suite peuvent produire de
nouvelles transitions.

```sx
var trace = ""
let status = execution.evaluate(creature, func(name:@str, transition:BehaviourTree.Transition) {
    match transition {
        entered => { trace += ">" + name + " " }
        exited(_) => { trace += "<" + name + " " }
    }
})
```

Cet observateur est synchrone et n’est pas conservé. Il peut donc capturer une
variable locale telle que `trace`. Sans observateur, `evaluate(context)` suit
exactement le même ordre et produit le même statut.

[Revenir à l’index AI](README.md)

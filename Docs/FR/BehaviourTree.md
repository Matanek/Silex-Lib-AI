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

## Observer un parcours

La surcharge d’`evaluate` qui reçoit un callback signale `entered` avant un
nœud puis `exited(Status)` lorsque l’appel du nœud rend son statut. Le callback
reçoit le nom public du nœud, jamais un indice interne.

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

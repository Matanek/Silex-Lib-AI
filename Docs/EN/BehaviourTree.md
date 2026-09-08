# Build and run a Behaviour Tree

`AI.BehaviourTree` separates a shared definition from the state owned by each
agent. A definition describes conditions, actions, and composites; every call
to `instantiate()` creates an independent execution instance.

## Describe a tree

A condition reads the context and returns a boolean. An action may mutate that
context and returns `success`, `failure`, or `running`.

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

A definition has exactly one root. `build()` returns a `BuildError` before any
execution when the root is missing, a composite is empty or left open, an
`end()` call is superfluous, or a second node is placed outside the root.

Condition and action functions are retained by the definition. They must
therefore be named functions or non-capturing anonymous functions. Their
mutable state belongs to the `Context` passed to evaluation; the definition
never retains that context.

## Instantiate and evaluate

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

A sequence stops at the first `failure` or `running` child and succeeds when
all children succeed. A selector stops at the first `success` or `running`
child and fails when all children fail.

Several instances may share the same definition. Their execution status
remains independent; only the context explicitly passed to an evaluation is
mutated.

## Observe a traversal

The `evaluate` overload that receives a callback reports `entered` before a
node and `exited(Status)` when that node call returns its status. The callback
receives the public node name, never an internal index.

```sx
var trace = ""
let status = execution.evaluate(creature, func(name:@str, transition:BehaviourTree.Transition) {
    match transition {
        entered => { trace += ">" + name + " " }
        exited(_) => { trace += "<" + name + " " }
    }
})
```

This observer is synchronous and is not retained. It may therefore capture a
local variable such as `trace`. Without an observer, `evaluate(context)` keeps
the same order and returns the same status.

[Back to the AI index](README.md)

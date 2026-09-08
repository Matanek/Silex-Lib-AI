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

## Resume and interrupt an action

When an action returns `running`, the instance retains that leaf and the
composite path leading to it. The next `evaluate` call resumes the action
directly: already resolved conditions and previous siblings are not traversed
again.

A long-running action may declare an abandonment hook through the three-
argument `action` overload. In this fragment, `Creature` has a mutable
`patrol_reserved` field and `patrol` denotes the long-running action:

```sx
func abandon_patrol(creature:&Creature) {
    creature.patrol_reserved = false
}

builder.action("patrol", patrol, abandon_patrol)
```

`execution.interrupt(creature)` invokes that hook at most once for the active
action, clears the retained path, and makes the next evaluation restart at the
root. `reset(creature)` provides the same abandonment guarantee and returns
the instance to its initial state. The context-free `reset()` form suits an
inactive or terminal instance; a `running` action requires the context form so
its hook can clean up its work.

The package does not choose when execution resumes. A loop may call the
instance on the next frame, while a scheduler may wait for an event or a
deadline without performing any intermediate tree work.

## Bound the work of one call

`advance(context, budget)` limits the number of new nodes visited during the
call and reports exhaustion explicitly:

```sx
match execution.advance(creature, 8) {
    status(_) => { print("tree completed") }
    budget_exhausted => { print("resume later") }
}
```

`budget_exhausted` retains progress and is not a `Status.running` returned by
an action. `evaluate` automatically uses a budget derived from the prepared
node count; for a valid static tree, it covers one ordinary traversal or
resume.

The flattened definition and maximum depth are computed once by `build()`.
`instantiate()` then reserves the path required by that agent: ordinary
evaluations, resumes, interruptions, and resets do not grow this storage.

## Observe a traversal

The `evaluate` overload that receives a callback reports `entered` when a node
is visited and `exited(Status)` when its progress produces a status. The
callback receives the public node name, never an internal index. A resume does
not report conditions or siblings that were already resolved; only the active
leaf and composites required to continue may produce new transitions.

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

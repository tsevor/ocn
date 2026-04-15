# Object Constructor Notation

OCN is a declarative, framework-agnostic data serialization
language optimized for dense, hierarchical data structures.
It replaces the verbosity of JSON and YAML with implicit,
schema-driven parsing, making it ideal for game engine levels,
UI layouts, and complex configuration files.

The core philosophy:
Shift the complexity to the parser so the human types less.

## Basics

### Primitive Types

- int: `32`, `-3`, `0xFF`, `0o033`, `0b00100101`
- float: `0.0014`, `12e9`, `32.`, `nan`, `inf`
- bool: `true`, `false`
- str: `"hello"`, `"\x1b[0m"`

### Comments and Whitespace

- Whitespace (spaces, tabs, newlines) is completely ignored
  outside of strings.
- Comments use `#`.

```ocn
# This is a comment
value = 10
```

## Globals and Expressions

### Globals

Constants defined at the root level. They are read-only and
restricted to literal primitives.

```ocn
$GRAVITY = 9.81;
$DEBUG = true;
$SYS_NAME = "CORE";
```

### Expressions `$(...)`

A parse-time calculator. Evaluates math and string
concatenation before the data is stored in memory.

- Allowed: Literals and $Globals.

```ocn
obj enemy(
	damage = $($GRAVITY * 2.5),
	name = $($SYS_NAME + "_Bot")
)
```

## Imports

OCN supports modularity through both direct and namespaced imports.
All imports must occur at the top of the file in the root scope.

- Direct Import: `import "file.ocn"` merges all schemas and
  globals directly into the current scope.

- Namespaced Import: `import "file.ocn" as ns` encapsulates
  imported data. Use dot-notation (`ns.type`) for access.

- Shadowing: If names collide, the last definition encountered
  (top-to-bottom) takes priority.

- Implicit Typing: Namespaced types are resolved implicitly
  during instantiation if the property is statically typed.

```ocn
import "math.ocn"
import "config.ocn" as cfg

obj player(
    loc: vec2,         # Found in direct import
    speed = cfg.$BASE  # Found in namespaced import
)
```

## Schemas

Everything in OCN is built from a schema defined at the root
level. There are two types:

### Objects (`obj`)

Defines a strict blueprint (an ordered dictionary/struct).

- No-Gap Rule: All required arguments (those without
  defaults) MUST be defined in a single contiguous block.

- Inheritance: *schema unpacks properties from a parent
  object. Bottom-overrides-top applies.

- Property Shorthand: Using a schema name like pos() expands
  to pos: pos = pos().

```ocn
obj vec2(x: float = 0.0, y: float = 0.0)

# 'id' and 'name' are contiguous required arguments
obj entity(
	id: int,
	name: string,
	active = true,
	vec2() # Shorthand sub-object
)
```

### Scenes (`scene`)

Defines an unordered population of instances (a canvas/array).

- Rule: Anonymous arrays [...] are strictly forbidden inside
  scenes.

```ocn
scene level_01 {
	# Objects go here
}
```

## Instantiation and Mapping

When placing an object or other scene into a scene, you
instantiate it.

### Named vs. Anonymous

- Named (`id: type()`): Gets hashed into the engine's O(1)
  access registry.

- Anonymous (`type()`): Added to the scene's object list but
  not added to the the access registry.

```ocn
scene world {
	player_1: entity(1, "James") # Named
	tree(x=10, y=20)             # Anonymous object
}
```

### Argument Mapping

When passing `()` to an `obj`, values map to the schema:

- Positional values map to the required contiguous block first.

- Excess values spill leftward into optionals, then rightward.

- Named Overrides: Bypass positioning entirely (active=false).

- Comma Skips: ,, skips a positional index, forcing its default.

```ocn
obj transform(x=0, y=0, z=0)

scene demo {
	# Skips x, sets y to 50, sets z to 10
	t1: transform(, 50, 10)
}
```

### Scene Path Assignments

When instantiating a scene, () acts as an override block
using dot-notation to alter its internal children.

```ocn
scene outpost {
	guard: entity(1, "Guard")
}

scene world {
	# Overrides the guard's name inside the outpost instance
	camp: outpost(guard.name = "Commander")
}
```

## Arrays

Arrays require strict type signatures during definition, but
use implicit typing during instantiation to drastically
reduce boilerplate.

### Array Signatures

When defining an array in an `obj` schema, use the format:

`Label: [Type(ElementDefault) ; Length] = [DefaultListItems...]`

- Dynamic Arrays: Omit the length. Elements can be added
  indefinitely.

- Fixed Arrays: Provide a length (`; N`).

- Element Defaults: Defining a default constructor (e.g.,
  `item(0)`) allows the parser to auto-fill missing data.

```ocn
obj item(
	id: int = 0,
	name: str = "empty",
)

obj chest(
	# Dynamic length. Explicit item definitions required.
	loot: [item] = [],
	
	# Fixed length of 5. Uses a default item.
	slots: [item(0, "empty") ; 6] = [] 
	
	# Dynamic length. Uses the original default for item.
	# Has default list contents, follows the same rules
	#   as instantiation, covered below
	hidden_compartment: [item()] = [
		item(10, "diamond"),
		item(11, "emerald")
	],
)
```

### Implicit Instantiation and Shortcuts

When instantiating an array, the parser uses the signature
to do the heavy lifting for you.

- Implicit Elements: Omit the schema name entirely. Just
  use `(args)`.

- Comma Shortcut: An empty comma `,` inserts exactly one
  instance of the default element. (except for a trailing
  comma when the array is dynamic; other cases don't apply)

- Auto-Fill: Fixed-length arrays automatically pad any
  unassigned trailing slots with the default element.

- Explicit Constructor: If the signature lacks an element
  default (the `()` in `items: [item(...)]`), then comma
  shortcuts and auto-filling are disabled. Every element
  must be explicitly defined using (args) or item(args).

```ocn
scene level_01 {
	treasure: chest(
		slots = [
			,             # Slot 0: Shortcut inserts default item(0, "empty")
			(1, "sword"), # Slot 1: Implicitly builds item(1, "sword")
			item(2),      # Slot 2: Uses the default to skip an argument
			# Slots 3-5: Engine auto-fills the remaining 3 slots
		]
	)
}
```

### The Addressibility Barrier

Arrays are "sealed." Bracket indexing (e.g., `slots[1].id = 5`)
is strictly forbidden within the file. If you need to address
or override a specific object from a scene path, it must be
a named logic node (`id:`), not an element inside an array.

ai generated for an idea on how to do it

OCN Python API Reference

The OCN Python API bridges the gap between the static declarative data file and your real-time game engine. It is designed to be idiomatic, mutable, and strictly optimized against common Python performance traps.
1. Core Engine Integration
ocn.load(filepath: str) -> OCNEnv
ocn.loads(data: str) -> OCNEnv

The primary entry points. The parser resolves all imports, evaluates all expressions, maps all anchors, and returns the fully materialized root environment.
2. OCNEnv (The Environment)

The root data container holding the parsed state of your files.
Property	Type	Description
.globals	dict	Read-only dictionary of evaluated primitive constants (e.g., env.globals["MAX_SPEED"]).
.namespaces	dict	Maps import aliases to mini-environments (e.g., env.namespaces["math"].schemas["vec2"]).
.schemas	dict	Maps schema names to OCNSchema blueprints.
.scenes	dict	Maps scene names to OCNScene world containers.
3. OCNSchema (The Blueprint Factory)

Represents an obj definition. Use this to spawn new instances of an object at runtime using the exact same defaults defined in the OCN file.

    .defaults: A dictionary containing the pre-evaluated default values.

    .spawn(**overrides) -> OCNObject:

        Deep-copies the .defaults dictionary.

        Applies any provided keyword arguments over the defaults.

        Returns a new, live OCNObject.

4. OCNObject (The Live Data Node)

The mutable data container representing an instantiated object.

    State Tracking:

        .schema: A reference to the parent OCNSchema (useful for type-checking).

        .id: The string ID (e.g., "player_1"), or None if it is an anonymous object.

        ._dead: A boolean flag used internally by the scene for high-performance deferred deletion.

    Data Access (Read/Write): Supports both dot-notation and dictionary access seamlessly.
    Python

    # Both are perfectly valid and update the same underlying data
    enemy.hp -= 10
    enemy["active"] = False

5. OCNScene (The High-Performance Canvas)

The manager for your live entities. It handles both spatial ordering (for the renderer) and O(1) Logic lookups (for gameplay scripting).
A. Data Structures

    .elements: A standard Python list containing all objects (named and anonymous) in their spawn/render order.

    .registry: A Python dict mapping ID strings directly to OCNObject references.

B. Standard Methods

    .get(id: str) -> OCNObject: Fetches an object directly from the registry. Returns None if not found.

    .add(obj: OCNObject, id: str = None):

        Appends the object to .elements.

        If an id is provided, sets obj.id and adds it to .registry.

C. The Deferred Deletion System (Performance Critical)

To prevent devastating O(N) memory shifts during gameplay, OCN uses deferred deletion.

    .remove(target): Accepts either an ID string or an OCNObject.

        It immediately removes the object from the .registry (an O(1) operation).

        It sets obj._dead = True.

        Crucial: It does not shift the .elements list.

    .sweep(): Rebuilds the .elements list in a single, fast C-level pass, dropping any object where _dead == True. You should call this exactly once at the end of your game loop's update step.

D. Mass Operations (Duck-Typing Safe)

When using lambdas, Python's try/except AttributeError is too slow for thousands of objects. You must use getattr(obj, 'prop', default) for lightning-fast, safe duck-typing.

    .filter(predicate) -> Generator[OCNObject]: Yields all matching, non-dead objects.

    .clear(predicate): Mass-removes objects. Flags all matches as _dead, deletes them from the registry, and automatically calls .sweep() to clean the array immediately.

Predicate Types:

    By Schema: scene.clear(env.schemas["particle"])

    By Lambda (Fast Duck-Typing):
    Python

    # Safely checks lifetime; if the object doesn't have 'lifetime', it defaults to 0.0
    scene.clear(lambda o: getattr(o, 'lifetime', 0.0) > 5.0)

6. OCNArray (The Sealed Container)

Represents an array defined within an obj signature.

    Inheritance: Inherits directly from Python's standard list. You can use .append(), .pop(), slicing, and standard iteration.

    Metadata: * .element_type: A reference to the OCNSchema defined in the file signature.

7. Standard Game Loop Example

Here is how the API is intended to be used in a standard Python game engine structure.
Python

import ocn

# 1. Load the world
env = ocn.load("level_01.ocn")
world = env.scenes["main_stage"]

def update(dt):
    # 2. Logic Updates via O(1) Registry
    player = world.get("hero")
    if player:
        player.pos.x += getattr(player, 'speed', 1.0) * dt

    # 3. Spawning Anonymous Objects (e.g., shooting)
    if button_pressed:
        bullet = env.schemas["projectile"].spawn(x=player.pos.x, y=player.pos.y)
        world.add(bullet)

    # 4. Duck-Typed Cleanup
    # Removes any object that has a lifetime exceeding 5 seconds.
    world.clear(lambda o: getattr(o, 'lifetime', 0.0) > 5.0)

    # 5. Sweep Dead Objects (If any manual .remove() calls were made)
    world.sweep()

def render():
    # 6. Ordered Spatial Rendering
    for entity in world.elements:
        if not entity._dead: # Safety check
            draw_sprite(entity)
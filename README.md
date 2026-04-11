# OBJECT SCENE MARKUP LANGUAGE

the purpose of this format is to have unorderd
jumbles of objects inside of scenes which can be
addressed and loaded separately.


# EXAMPLE USES

- this can be useful in any game where objects are mostly static
- \<more here\>


# TYPES

all automatic
- standard:
  - ints: `32`, `-3`, `0xFF`, `0o033`, `0b00100101`
  - floats: `0.0014`, `12e9`, `32.`, `nan`, `inf`
  - strings: `"hello"`, `"\x1b[0m"`
  - bools: `true`, `false`
  - other: `null`
- weird:
  - lists/arrays/vectors \(see [LIST OBJECT](#list-object)\)
  - meta \(see [META OBJECT](#meta-object)\)
  - dicts/maps: can be represented by objects

more info in [BUILT-IN OBJECTS](#built-in-objects) section

## COMMENTS
```osml
# comments are notated like this
```


# SYNTAX IN ROOT

- this is where definitions of names happen
- inside of a scene or an object, things are very different


# HEADER

## INCLUDES
syntax: `add <filename>.osml;`

this adds to current namespace:
```osml
add example_blank.osml;
```

to give it its own namespace:
```osml
add example_blank2.osml as example2;
```
address its components like this:
`example2.obj1`
`example2.scn1`

## META OBJECT

- the metadata itself is an object
- the only object allowed in root

in root:
```osml
meta (
  author "Trevor Abercrombie",
)
```
can be used in objects and scenes for docstrings, etc.

valid attributes:
- `author`
- `comment`
- `doc`

# GLOBALS

- preprocessed and replaced by everything between the `=` and `;`

```osml
$GLOBAL_INT = 73 ;
$GLOBAL_STR = "Apple!" ;
```

good for options or constants

```osml
$SCALE = 1.0 ;
$PI = 3.14159265359 ;
```

# OBJECTS

- definitions in root

to define:
```osml
example_obj ( # the name of the object
  a,                   # defining an attribute
  !b,                  # overpower overrides (1)
  c = 2,               # default value
  d[1 .. 5] = 3,       # min-max valid values [inclusive .. non-inclusive]
  e = "hello",         # dynamic typed string
  f:string = "world",  # static typed string
  g:int = $GLOBAL_INT, # using a global variable
)
```
*\(1: see [overrides](#overrides)\)*

### a few real ones that will be used in the other examples
```osml
obj (
  a = 1,
  b = 2,
  c = 3,
  d = 4,
)

rect (
  x = 0,
  y = 0,
  w = 10,
  h = 10,
)

color (
  r = 0,
  g = 0,
  b = 0,
)
```

# SCENES

to define:
```osml
scn { # this gives this scene the name `scn`
  # objects here
}
```

## SYNTAX IN SCENES

this is all within a scene

## scn1 {
  ### OBJECT USE:

  args in same order as definition:
  ```osml
  obj 10 10 50 50;
  ```
  multi-line:
  ```osml
  obj
    12
    32
    12
    3
  ;
  ```
  because of the semicolon

  defaults:
  ```osml
  obj 4 23;
  ```
  because of defaults, same as:
  ```osml
  obj 4 23 3 4;
  ```
  like python would have
  `obj(2, 4, d=12)`
  to skip c and set d,
  we have this:
  ```osml
  obj 2 4 d(12);
  ```
  it skips 3rd arg (c), leaving it default,
  but specifies d (4th arg) by name

  `.` in place of an argument keeps it default:
  ```osml
  obj 2 4 . 12;
  ```
  keeps 3rd arg (c) default

  also like python, you can't do a plain arg
  after specifying one by name:
  ```osml
  obj 12 2 c(7) 32;
  # bad syntax  ^
  ```

  values can be in parintheses with or without setting by name:
  ```osml
  obj (2) (34) c(3) d(23);
  ```
## }


## MORE SCENE DEFINITIONS

to reiterate, scenes are defined like:
```osml
scn2 {
  obj; # keeping all defaults
}
```
this gives this scene the name `scn2`

scens can contain copies of others:
```osml
scn3 {
  scn2;
}
```
i reiterate, COPIES.
modifying scn3.scn2 does not modify scn2

unpacks scn2's items into scn4:
```osml
scn4 {
  *scn2;
}
```
in the case above,
scn4 does non contain a copy of scn2 like scn3 does,
but instead contains copies of each of scn2's items

this allows there to be an in-place definition of a
scene inside another:
```osml
scn5 {
  subScn {
    # objects
  }
}
```
this does not make `subScn` a scene usable anywhere else,
but rather just makes a scene inside scn5 addressible
as `scn5.subScn`

this is bad syntax:
```osml
scn {
  {
    # objects
  }
}
```

the point of a scene is to be addressible by name
which gets us to this:

objects themselves are not addressible by any name.

if you want a single addressible object like a button
the best you can do is give the object an id
```osml
button (
  x = 0,
  y = 0,
  pushed = false,
  id = 0,
)
scn_button {
  button 0 0 . 2;
}
```
or put it in its own scene,
but that's against the point of this language.

then in the real code you can go through and based on the
object type and id, do things

the reason this is the case is because this language is
meant for cases where having things in order is not helpful


# MORE STUFF WITHIN SCENES

## scn6 {
  ### OVERRIDES
  to change all default values of a name within a scene
  after a certain point, follow this syntax:
  ```osml
  ! a(10) b(10);
  obj; # vals: 10 10 3 4
  ! b(23) d(44);
  obj; # vals: 10 23 3 44
  ```
  change values by a relative amount:
  ```osml
  ! a+(3) b-(4) c*(2) d/(4)
  obj; # vals: 13 19 6 11
  ```
  to set/change all values in an entire subscene when
  making an instance:
  ```osml
  scn2 ! x(0) y+(10);
  ```
  you can still unpack when doing this:
  ```osml
  *scn2 ! x(2) y+(4)
  ```

  - to make a value exempt from this, prefix it with `!` on definition
  - to overrule this when overriding, use `!!`
  - to make a value exempt from that, prefix it with `!!` on definition
  - and so on
  - the one with more more `!` is the value that is used
  - if they have the same amount then the original value is use
  
  overrides do affect subscenes

  ### FOR LOOPS

  let's say you want to make a 100 x 100 grid of squares
  you can't realistically do that by hand,
  so there are for loops:
  ```
  <var>(<start=0>;<stop>;<step=1>) {
    <objects>
  }
  ```
  ```osml
  i(0;10;1) {
    rect;
  }
  ```
  when a value is omitted, the default is used:
  ```osml
  i(;10;) { # same as above
	rect;
  }
  ```
  nested:
  ```osml
  i(;100;) j(;100;) {
    # parintheses allow expressions,
    # can be used any time,
    # but must be used when there are variables
    rect (i * 10) (j * 10) 10 10;
  }
  ```
  for loops automatically unpack

  ### IF STATEMENTS
  - only really useful in for loops
  ```
  ? (<expression>) {
    <objects>
  }
  ```
  - 0 evaluates to false
  - anything else is true
  - or just do bools
  - c-style expressions
  ```osml
  i(;100;) j(;100;) {
    ? (i % j) {
      rect (i) (j) 10 10;
    }
    ? (i == 0) {
      rect 20 (i) 5 5;
    }
    # if statements automatically unpack too
  }
  ```
## }

# ADVANCED OBJECTS

now that we understand how objects look in
scenes, we can expand on them

an object can have more advanced
properties by adding a sub-object as
a kind of namespace

for example:
```osml
obj2 (
  substuff (
    a = 0,
    b = 0,
  ),
  x = 0,
  y = 0,
)
```

the sub-object can be a copy of an existing one
- cannot be itself
```osml
obj3 (
  obj2,
)
```

## SUB OBJECT DEFAULTS + DEFINITIONS:

setting sub-object values in a scene:
```osml
scn7 {
  obj2 (1) 3 4;
}
```
this sets the values to to:
```
obj2 = (
  substuff = (
    a = 1,
    b = 0,
  )
  x = 3,
  y = 4,
)
```

and different defaults for the sub object is
## IN OBJECT DEFINITIONS:
```osml
obj4 (
  obj1 1 2,
  obj2 (3 7) 1 2,
  obj3 obj2(substuff(1 3) 5 7),
)
```

you can give a sub-object a new name within the object:
```osml
obj5 (
  sub:obj1,
)
```

you can inherit by unpacking an object:
```osml
rect_but_different (
  *rect,
  a = 0,
  b = 0,
)
```

a good example of both in action:
```osml
colored_rect (
  *rect,
  color,
)
```

finally, now that we have sub-objects, we can go over
# BUILT IN OBJECTS:
- cannot be unpacked
- for special cases
- often defy all syntax

## PLAIN TYPE OBJECTS:
rarely needed

- `int <value>`;
- `float <value>`;
- `string <value>`;
- `bool <value>`;

## LIST OBJECT:

- `list <len/. (for dynamic)> <object>`

you can also set the object's values

let's go with storage as an example
```osml
item (
  name = "",
  count = 0,
  in_chest = false,
)

storage_chest (
  owner = "",
  items:list 64 item(in_chest(true)),
)
```

dynamic length example
```osml
date (
  year = 0,
  month = 0,
  day = 0,
)
signature (
  name = "",
  date,
)
contract (
  signatures:list . signature,
)
```

why plain types?
- for static typing
- for lists of plain stuff
```osml
obj6 (
  list . int,
)
```

setting the values in a list:
```osml
obj7 (
  a:list 4 int = (
    1, 2, 3, 4,
  )
) # default values in list

obj8 (
  a:list 2 rect(w(1) h(1)) = (
    # default constructors for each rect
    (
      w = 1,
      h = 1
	),
    ., # use default for 2nd
    (
      w = 1,
      h = . # use default h for 3rd
    ),
  )
)
```

# HOOKS AND OBJECT TYPES:
these aren't real, but 
```osml
button2 (
  x = 0,
  y = 0,
  pressed = false;
  type = "interactive";
  hook = "buttonpress";
)
```
so when you go over it in the code,
you can check this and run the hooks
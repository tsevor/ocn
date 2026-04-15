#!venv/bin/python

import osml

with open("test.osml") as f:
    struct = osml.load(f)
    print(struct)

#!/usr/bin/env python3
import sys
print("HOLA DESDE PYTHON", file=sys.stdout, flush=True)
print("TEST 2", file=sys.stderr, flush=True)
sys.stdout.write("TEST 3\n")
sys.stdout.flush()

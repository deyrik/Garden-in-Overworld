import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(RAIZ, "..", "src", "server"))
sys.path.insert(0, os.path.join(RAIZ, "..", "src", "client"))

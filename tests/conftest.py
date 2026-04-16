import os
import sys

# Apunta a dunita_game/ que contiene el paquete src/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dunita_game'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 4_Solana.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from students.solana import view as sol_view

# Reload modules to reflect any changes during development
from importlib import reload
reload(sol_view)

sol_view.render_view()

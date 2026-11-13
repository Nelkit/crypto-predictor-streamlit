# 3_Bitcoin.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from students.bitcoin import view as btc_view

# Reload modules to reflect any changes during development
from importlib import reload
reload(btc_view)

btc_view.render_view()

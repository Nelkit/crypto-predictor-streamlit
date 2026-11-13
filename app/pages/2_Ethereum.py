# 2_Ethereum.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from students.ethereum import view as eth_view

# Reload modules to reflect any changes during development
from importlib import reload
reload(eth_view)

eth_view.render_view()

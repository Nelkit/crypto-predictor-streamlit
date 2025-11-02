import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from students.xrp import view as xrp_view

xrp_view.render_tab()

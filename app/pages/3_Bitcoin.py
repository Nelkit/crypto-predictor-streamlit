import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from students.bitcoin import view as btc_view

btc_view.render_tab()

# Helper wrapper to debug the app within PyCharm

from streamlit.web.bootstrap import run

real_script = "ice_age_app.py"
run(real_script, False, [], {})

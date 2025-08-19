# Helper wrapper to debug the app within PyCharm

from streamlit.web.bootstrap import run

real_script = 'streamlit_app.py'
run(real_script, False, [], {})

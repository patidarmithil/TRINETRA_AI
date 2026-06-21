import os
import sys

if "streamlit" in sys.modules:
    with open("dashboard/dashboard.py", "r", encoding="utf-8") as f:
        code = compile(f.read(), "dashboard/dashboard.py", 'exec')
        exec(code, globals())
else:
    os.system(f"{sys.executable} -m streamlit run dashboard/dashboard.py")
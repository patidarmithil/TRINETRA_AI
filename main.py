import os
import sys

# Hack for Streamlit Cloud to prevent libgthread errors
# Uninstall GUI-dependent OpenCV that gets forced by ultralytics
os.system(f"{sys.executable} -m pip uninstall -y opencv-python opencv-contrib-python")

if "streamlit" in sys.modules:
    with open("dashboard/dashboard.py", "r", encoding="utf-8") as f:
        code = compile(f.read(), "dashboard/dashboard.py", 'exec')
        exec(code, globals())
else:
    os.system(f"{sys.executable} -m streamlit run dashboard/dashboard.py")
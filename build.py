import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil

print("🚀 build.py started")

try:
    df = pd.read_csv("events_fixed.csv")
    print("✅ events_fixed.csv loaded")
except Exception as e:
    print("❌ CSV loading failed:", e)

try:
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("index.html.j2")
    print("🧩 Template loaded")
except Exception as e:
    print("❌ Template loading failed:", e)

try:
    os.makedirs("site", exist_ok=True)
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(template.render(events=df.to_dict(orient="records")))
    print("✅ index.html generated")
except Exception as e:
    print("❌ HTML generation failed:", e)

try:
    shutil.copy("templates/style.css", "site/style.css")
    print("✅ style.css copied")
except Exception as e:
    print("❌ CSS copy failed:", e)

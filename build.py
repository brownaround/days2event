import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil

print("🚀 build.py started")

# CSV 로딩 (이미 정리된 상태)
df = pd.read_csv("events_fixed.csv")
print("✅ events_fixed.csv loaded")

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("index.html.j2")
print("🧩 Template loaded")

os.makedirs("site", exist_ok=True)

# HTML 렌더링
with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(template.render(events=df.to_dict(orient="records")))

# CSS 복사
shutil.copy("templates/style.css", "site/style.css")

print("✅ HTML and CSS generated successfully")
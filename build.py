
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os
import shutil

print("🚀 build.py started")

def country_to_flag(country_name):
    code_map = {"USA": "US", "Belgium": "BE"}
    code = code_map.get(country_name.strip(), None)
    if not code:
        return ""
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)

def add_flag_to_location(location):
    parts = location.split(',')
    if len(parts) < 2:
        return location
    country = parts[-1].strip()
    flag = country_to_flag(country)
    return location + f" {flag}" if flag else location

df = pd.read_csv("events.csv")
print("✅ events.csv loaded")

df["location"] = df["location"].apply(add_flag_to_location)
df["dates"] = df["start_date"] + "–" + df["end_date"]

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("index.html.j2")
print("🧩 Template loaded")

os.makedirs("site", exist_ok=True)
index_path = "site/index.html"
with open(index_path, "w", encoding="utf-8") as f:
    f.write(template.render(events=df.to_dict(orient="records"), current_year=datetime.now().year))

shutil.copy("templates/style.css", "site/style.css")
print("📁 Files in site/:", os.listdir("site"))
print("📦 site/index.html exists:", os.path.exists("site/index.html"))
print("📦 site/style.css exists:", os.path.exists("site/style.css"))
print("✅ HTML and CSS generated successfully")
print("🎯 렌더링 결과:")
rendered = template.render(events=df.to_dict(orient="records"))
print(rendered[:500])  # 앞 500자 미리보기

with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(rendered)
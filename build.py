import pandas as pd
import jinja2
from datetime import datetime
import os

# site 폴더 자동 생성
os.makedirs("site", exist_ok=True)

# Load CSV
df = pd.read_csv("events.csv")

# Normalize column names
df.columns = df.columns.str.strip().str.title()

# Drop rows with missing required fields
df = df.dropna(subset=[
    "Event Name", "Start Date", "City", "Country", "Region", "Official Site"
])

# Convert date columns to datetime
df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')
df["End Date"] = pd.to_datetime(df["End Date"], errors='coerce')

# Format date for display
df["Start Date Str"] = df["Start Date"].dt.strftime('%b %d, %Y')
df["End Date Str"] = df["End Date"].dt.strftime('%b %d, %Y')

# Days until event
df["Days To Event"] = (df["Start Date"] - pd.Timestamp.now()).dt.days

# Load Jinja2 templates from 'templates' folder
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    autoescape=jinja2.select_autoescape(["html", "xml"])
)

template = env.get_template("index.html.j2")

# Render index.html to site/
output_html = template.render(events=df.to_dict(orient="records"))
with open("site/index.html", "w", encoding="utf-8") as f:
    f.write(output_html)

print("Build completed. Output is in 'site/' folder.")

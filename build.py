import pandas as pd
import jinja2
from datetime import datetime
import os

# Read the CSV
df = pd.read_csv("events.csv")

# Drop rows with missing key fields
df = df.dropna(subset=[
    "Event Name", "Start Date", "City", "Country", "Region", "Official Site"
])

# Convert date columns to datetime
df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')
df["End Date"] = pd.to_datetime(df["End Date"], errors='coerce')

# Format date for display
df["Start Date Str"] = df["Start Date"].dt.strftime('%b %d, %Y')
df["End Date Str"] = df["End Date"].dt.strftime('%b %d, %Y')

# Add location string
df["Location"] = df["City"] + ", " + df["Country"]

# Emoji for each country (basic example)
country_emojis = {
    "United States": "🇺🇸", "South Korea": "🇰🇷", "France": "🇫🇷", "Italy": "🇮🇹",
    "Spain": "🇪🇸", "England": "🇬🇧", "Canada": "🇨🇦", "Taiwan": "🇹🇼",
    "Singapore": "🇸🇬", "Thailand": "🇹🇭", "Indonesia": "🇮🇩", "Philippines": "🇵🇭"
}
df["Location"] = df.apply(lambda row: f"{row['City']}, {row['Country']} {country_emojis.get(row['Country'], '')}", axis=1)

# Timer target (Start Date)
df["Timer Date"] = df["Start Date"].dt.strftime('%Y-%m-%d')

# Group events by Region
regions = df["Region"].dropna().unique()
events_by_region = {
    region: df[df["Region"] == region].sort_values("Start Date")
    for region in regions
}

# Set up Jinja2 environment
env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
template = env.get_template("by-region.html")

# Output directory
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Render and save the page
html = template.render(
    regions=regions,
    events_by_region=events_by_region,
    selected_region="Asia",  # 기본값
    timer_script="timer.js"
)

with open(os.path.join(output_dir, "byregion.html"), "w", encoding="utf-8") as f:
    f.write(html)

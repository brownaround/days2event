import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

csv_path = "events.csv"
df = pd.read_csv(csv_path)

# 결측치 제거
df = df.dropna(subset=["Region", "City", "Country", "Event Name", "Official Site", "Date"])

# 날짜 처리
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])  # NaT 제거
df['Date'] = df['Date'].dt.strftime('%b %d, %Y')

# 국기 이모지
def get_flag_emoji(country):
    try:
        return ''.join([chr(127397 + ord(c.upper())) for c in country if c.isalpha()])
    except:
        return ''

CONTINENTS = sorted(df['Region'].dropna().unique())

events_by_region = {}
for _, row in df.iterrows():
    region = row['Region'].strip()
    event = {
        "name": row["Event Name"],
        "location": f"{row['City']}, {row['Country']} {get_flag_emoji(row['Country'])}",
        "date": row["Date"],
        "official_site": row["Official Site"],
    }
    if region not in events_by_region:
        events_by_region[region] = []
    events_by_region[region].append(event)

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("by-region.html")

region = CONTINENTS[0]
html = template.render(
    continents=CONTINENTS,
    events_by_region=events_by_region,
    selected_region=region,
    timer_script='timer.js'
)

os.makedirs("site", exist_ok=True)
with open("site/byregion.html", "w", encoding="utf-8") as f:
    f.write(html)

# 디버깅용 출력
print("✅ by-region 페이지 생성 완료!")
print("Regions:", list(events_by_region.keys()))
print("Event count:", sum(len(e) for e in events_by_region.values()))

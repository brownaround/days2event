import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# CSV 불러오기
csv_path = "events.csv"
df = pd.read_csv(csv_path)

# 날짜 포맷 정리
df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%b %d, %Y')

# 국가별 이모지 매핑
def get_flag_emoji(country):
    try:
        return ''.join([chr(127397 + ord(c.upper())) for c in country if c.isalpha()])
    except:
        return ''

# 지역 목록
CONTINENTS = sorted(df['Region'].dropna().unique())

# 지역별 정리
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

# Jinja2 템플릿 설정
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("by-region.html")

# 출력 HTML
region = CONTINENTS[0]
html = template.render(
    continents=CONTINENTS,
    events_by_region=events_by_region,
    selected_region=region,
    timer_script='timer.js'
)

# 결과 저장 경로
os.makedirs("site", exist_ok=True)
with open("site/byregion.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ by-region 페이지 생성 완료!")

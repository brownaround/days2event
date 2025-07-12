import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os

# 국가 이모지 매핑
country_to_emoji = {
    "United States": "🇺🇸",
    "Canada": "🇨🇦",
    "United Kingdom": "🇬🇧",
    "South Korea": "🇰🇷",
    "France": "🇫🇷",
    "Spain": "🇪🇸",
    "Germany": "🇩🇪",
    "Japan": "🇯🇵",
    "Thailand": "🇹🇭",
    "Singapore": "🇸🇬",
    "Taiwan": "🇹🇼",
    "Australia": "🇦🇺",
    "Italy": "🇮🇹",
    "Netherlands": "🇳🇱",
    "Belgium": "🇧🇪",
    "Brazil": "🇧🇷",
    "Mexico": "🇲🇽",
    "Argentina": "🇦🇷",
    "Philippines": "🇵🇭",
    # 필요한 국가 추가 가능
}

# CSV 불러오기
df = pd.read_csv("events.csv")

# 필요한 컬럼이 비어있는 행 제거
df = df.dropna(subset=[
    "Event Name", "Start Date", "City", "Country", "Region", "Official Site"
])

# 날짜 포맷 통일
df["Start Date"] = pd.to_datetime(df["Start Date"])
df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce")

# 국가 이모지 붙이기
df["Location"] = df.apply(
    lambda row: f"{row['City']}, {row['Country']} {country_to_emoji.get(row['Country'], '')}",
    axis=1
)

# 날짜 텍스트 구성 (Week 1, Week 2 등은 나중에 slug 기준 조건 처리로 확장 가능)
df["Date Range"] = df.apply(
    lambda row: f"{row['Start Date'].strftime('%b %d')} – {row['End Date'].strftime('%b %d')}" if pd.notnull(row["End Date"]) else row["Start Date"].strftime('%b %d'),
    axis=1
)

# 대륙별 이벤트 정리
events_by_region = {}
for region in df["Region"].unique():
    region_df = df[df["Region"] == region].sort_values("Start Date")
    events_by_region[region] = region_df.to_dict(orient="records")

# 템플릿 환경 설정
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("by-region.html")

# HTML 렌더링
html = template.render(
    continents=list(events_by_region.keys()),
    events_by_region=events_by_region,
    current_year=datetime.now().year,
    timer_script="timer.js"
)

# 출력 경로
output_path = os.path.join("output", "byregion.html")
os.makedirs("output", exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ byregion.html 파일 생성 완료!")

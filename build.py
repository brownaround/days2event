import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# CSV 파일 불러오기
df = pd.read_csv("events.csv")

# 필수 컬럼 누락 제거 (컬럼명은 CSV 기준)
df = df.dropna(subset=[
    "Festival Name", "Start Date", "City", "Country", "Region", "Link"
])

# 날짜 처리
df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')
df["End Date"] = pd.to_datetime(df["End Date"], errors='coerce')
df = df.dropna(subset=["Start Date"])  # 날짜 형식 오류 제거

# 나라 이모지 매핑
country_emoji = {
    "USA": "🇺🇸",
    "Canada": "🇨🇦",
    "UK": "🇬🇧",
    "France": "🇫🇷",
    "Germany": "🇩🇪",
    "Spain": "🇪🇸",
    "Italy": "🇮🇹",
    "South Korea": "🇰🇷",
    "Japan": "🇯🇵",
    "Taiwan": "🇹🇼",
    "Thailand": "🇹🇭",
    "Singapore": "🇸🇬",
    "Australia": "🇦🇺",
    "Mexico": "🇲🇽",
    "Brazil": "🇧🇷",
    "Argentina": "🇦🇷",
    # 필요시 더 추가
}

# 국가 + 이모지 조합
def format_location(city, country):
    emoji = country_emoji.get(country, "")
    if country == "United States":
        return f"{city}, {country} {emoji}"
    else:
        return f"{city}, {country} {emoji}"

df["Location"] = df.apply(lambda row: format_location(row["City"], row["Country"]), axis=1)

# Jinja2 템플릿 설정
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("by-region.html")

# 지역별 그룹핑
grouped = df.groupby("Region")

# 출력 디렉토리 생성
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# 모든 대륙 이름 수집
all_regions = sorted(df["Region"].unique().tolist())

# 지역별 HTML 생성
for region, group in grouped:
    region_slug = region.lower().replace(" ", "-")

    # 이벤트 정렬
    group = group.sort_values("Start Date")

    # HTML 렌더링
    html = template.render(
        events=group.to_dict(orient="records"),
        region_name=region,
        regions=all_regions,
        today=datetime.today().strftime("%Y-%m-%d"),
        timer_script="timer.js"
    )

    with open(f"{output_dir}/{region_slug}.html", "w", encoding="utf-8") as f:
        f.write(html)

# index.html 생성
index_template = env.get_template("index.html")
index_html = index_template.render(regions=all_regions)
with open(f"{output_dir}/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

import os
import pandas as pd
import jinja2
from datetime import datetime

def ensure_output_dir():
    os.makedirs("site", exist_ok=True)

def format_date_range(start, end):
    if pd.isnull(start):
        return ""
    if pd.isnull(end) or start == end:
        return start.strftime('%b %d, %Y')
    if start.year == end.year:
        if start.month == end.month:
            return f"{start.strftime('%b %d')}-{end.strftime('%d, %Y')}"
        return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
    return f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}"

def country_to_emoji(country):
    flags = {
        'Korea': '🇰🇷',
        'South Korea': '🇰🇷',
        'United States': '🇺🇸',
        'USA': '🇺🇸',
        'Japan': '🇯🇵',
        'China': '🇨🇳',
        'France': '🇫🇷',
        'Germany': '🇩🇪',
        'United Kingdom': '🇬🇧',
        'UK': '🇬🇧',
        'Canada': '🇨🇦',
        'Australia': '🇦🇺',
        'Brazil': '🇧🇷',
        'India': '🇮🇳',
        # 필요시 추가...
    }
    return flags.get(str(country), '')

# 중복 제거, 오직 이 함수만 사용!
def get_jinja_env():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml", "j2"])
    )
    env.filters['formatDateRange'] = format_date_range
    env.filters['countryToEmoji'] = country_to_emoji
    return env

def main():
    ensure_output_dir()
    df = pd.read_csv("events.csv")
    df.columns = df.columns.str.strip().str.title()
    df = df.dropna(subset=[
        "Event Name", "Start Date", "City", "Country", "Region", "Official Site"
    ])
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce')
    df["End Date"] = pd.to_datetime(df["End Date"], errors='coerce')
    df["Start Date Str"] = df["Start Date"].dt.strftime('%b %d, %Y')
    df["End Date Str"] = df["End Date"].dt.strftime('%b %d, %Y')
    df["Days To Event"] = (df["Start Date"] - pd.Timestamp.now()).dt.days

    env = get_jinja_env()
    # 템플릿 파일명 수정 (index.j2)
    template = env.get_template("index.j2")
    output_html = template.render(events=df.to_dict(orient="records"))
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(output_html)

    # style.css 복사 - 실제 경로 반영!
    src = "style.css"  # root 기준
    dst = os.path.join("site", "style.css")
    if os.path.exists(src):
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            fdst.write(fsrc.read())

    print("Build completed! Output is in 'site/' folder.")

if __name__ == "__main__":
    main()

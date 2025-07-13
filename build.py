import os
import pandas as pd
import jinja2
from datetime import datetime

# 1. site 폴더 자동 생성
def ensure_output_dir():
    os.makedirs("site", exist_ok=True)

# 2. 날짜 범위 커스텀 필터
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

# 3. 국가명을 이모지로 변환 (필요시 확장)
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

def get_jinja_env():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml"])
    )
    env.filters['formatDateRange'] = format_date_range
    env.globals['countryToEmoji'] = country_to_emoji  # <<== 필수!
    return env

# 4. Jinja2 환경 및 필터 등록
def get_jinja_env():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml"])
    )
    env.filters['formatDateRange'] = format_date_range
    env.filters['countryToEmoji'] = country_to_emoji
    return env

# 5. 빌드 실행
def main():
    ensure_output_dir()

    # CSV 로딩 및 컬럼 전처리
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
    # index.html 렌더
    template = env.get_template("index.html.j2")
    output_html = template.render(events=df.to_dict(orient="records"))
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(output_html)

    # CSS 등 정적 파일 복사 (선택)
    for static_file in ["style.css"]:
        src = os.path.join("templates", static_file)
        dst = os.path.join("site", static_file)
        if os.path.exists(src):
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                fdst.write(fsrc.read())

    print("Build completed! Output is in 'site/' folder.")

if __name__ == "__main__":
    main()

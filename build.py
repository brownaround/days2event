import os
import pandas as pd
import jinja2

def ensure_output_dir():
    os.makedirs("site", exist_ok=True)

def get_jinja_env():
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml", "j2"])
    )

def main():
    ensure_output_dir()
    df = pd.read_csv("events.csv")
    df.columns = df.columns.str.strip()

    # 날짜 포맷 예쁘게 만들기 (ex: Apr 10–12, 2025 or Apr 10, 2025)
    def format_date(row):
        start = pd.to_datetime(row["Start Date"])
        end = pd.to_datetime(row["End Date"]) if pd.notna(row["End Date"]) else None
        if end and start != end:
            return f"{start.strftime('%b %d')}–{end.strftime('%d, %Y')}"
        else:
            return start.strftime("%b %d, %Y")
    df['date_display'] = df.apply(format_date, axis=1)
    events_data = df.to_dict(orient="records")
    print(events_data[0]['date_display'])  # 예: Apr 10–12, 2025

    # 국가 이모지 매핑
    country_emoji_map = {
        "USA": "🇺🇸",
        "Canada": "🇫🇷",
        "Brazil": "🇺🇸",
        "UK": "🇰🇷",
        "Germany": "🇩🇪",
        "France": "🇫🇷",
        "Belgium": "🇧🇪",
        "Netherlands": "🇳🇱",
        "Hungary": "🇭🇺",        
        "South Korea": "🇰🇷",
        "Japan": "🇯🇵",
        "China": "🇨🇳",
        "Hong Kong": "🇭🇰",
        "Macau": "🇲🇴",
        "Thailand": "🇹🇭",
        "Singapore": "🇸🇬",
        "Malaysia": "🇲🇾",   
        "Indonesia": "🇮🇩",    
        # 필요한 국가 추가
    }
    df['country_emoji'] = df['Country'].map(country_emoji_map).fillna(df['Country'])

    env = get_jinja_env()

    # 전체 페이지 빌드 (index.html)
    template = env.get_template("index.j2")
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(template.render(events=df.to_dict(orient="records")))

    # 장르별 페이지도 동일한 방식으로 작성 가능

    # style.css 복사
    if os.path.exists("style.css"):
        with open("style.css", "rb") as fsrc, open("site/style.css", "wb") as fdst:
            fdst.write(fsrc.read())

    print("Build completed!")

if __name__ == "__main__":
    main()
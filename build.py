import os
import pandas as pd
import jinja2

def ensure_output_dir():
    os.makedirs("site", exist_ok=True)

def get_jinja_env():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml", "j2"])
    )
    return env

def format_event_date(row):
    start = pd.to_datetime(row['Start Date'])
    end = pd.to_datetime(row['End Date'])
    if start.month == end.month:
        return f"{start.day}-{end.day} {start.strftime('%b')}"
    else:
        return f"{start.day} {start.strftime('%b')} - {end.day} {end.strftime('%b')}"

def main():
    ensure_output_dir()
    df = pd.read_csv("events.csv")
    df.columns = df.columns.str.strip()

    # 날짜 포맷 컬럼 추가
    df['date_display'] = df.apply(format_event_date, axis=1)

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

    genres = [
        ("multi.html", "Multi-Genre"),
        ("edm.html", "EDM"),
        ("pop.html", "POP"),
        ("k-pop.html", "K-POP"),
        ("pride.html", "PRIDE"),
        ("by-region.html", "By Region")
    ]

    template = env.get_template("index.j2")
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(template.render(events=df.to_dict(orient="records")))

    for filename, genre in genres:
        template_name = filename.replace(".html", ".j2")
        filtered = df[df["Genre"].str.strip().str.lower() == genre.lower()]
        if not os.path.exists(os.path.join("templates", template_name)):
            continue
        with open(f"site/{filename}", "w", encoding="utf-8") as f:
            f.write(
                env.get_template(template_name).render(events=filtered.to_dict(orient="records"))
            )

    if os.path.exists("style.css"):
        with open("style.css", "rb") as fsrc, open("site/style.css", "wb") as fdst:
            fdst.write(fsrc.read())

    print("Build completed! All html files generated in /site.")

if __name__ == "__main__":
    main()

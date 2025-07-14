import os
import pandas as pd
import jinja2
from datetime import datetime

def ensure_output_dir():
    os.makedirs("site", exist_ok=True)

def get_jinja_env():
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates"),
        autoescape=jinja2.select_autoescape(["html", "xml", "j2"])
    )
    env.filters['strftime'] = format_date_filter
    env.globals['now'] = datetime.now
    return env


def format_date_filter(value, format='%Y-%m-%d'):
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    return value.strftime(format)

def format_date(row):
    start = row["Start Date"]
    end = pd.to_datetime(row["End Date"]) if pd.notna(row["End Date"]) else None
    if end and start != end:
        return f"{start.strftime('%b %d')}–{end.strftime('%d, %Y')}"
    else:
        return start.strftime("%b %d, %Y")

def main():
    ensure_output_dir()
    df = pd.read_csv("events.csv")
    df.columns = df.columns.str.strip()
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    df['End Date'] = pd.to_datetime(df['End Date'])
    df['date_display'] = df.apply(format_date, axis=1)
    df = df.sort_values('Start Date')

    # 국가 이모지 매핑
    country_emoji_map = {
        "USA": "🇺🇸",
        "Canada": "🇨🇦",
        "Brazil": "🇧🇷",
        "UK": "🇬🇧",
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
        "Macao": "🇲🇴",
        "Thailand": "🇹🇭",
        "Singapore": "🇸🇬",
        "Malaysia": "🇲🇾",
        "Indonesia": "🇮🇩",
        # 필요한 국가 추가
    }
    df['country_emoji'] = df['Country'].map(country_emoji_map).fillna(df['Country'])

    categories = {
        "multi": "Multi-Genre",
        "edm": "EDM",
        "pop": "POP",
        "k-pop": "K-POP",
        "pride": "PRIDE",
        "by-region": "By Region"
    }

    # Index (모든 이벤트)
    render_template(
        env,
        "index.j2",
        os.path.join("site", "index.html"),
        events=df.to_dict(orient="records"),
        category="All"
    )

    # 카테고리별 페이지
    for key, cat in categories.items():
        filtered = df[df["Category"] == cat]
        render_template(
            env,
            f"{key}.j2",
            os.path.join("site", f"{key}.html"),
            events=filtered.to_dict(orient="records"),
            category=cat,
        )

def render_template(env, template_name, output_path, **context):
    template = env.get_template(template_name)
    html = template.render(**context)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()

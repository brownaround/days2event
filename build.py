import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import sys
from datetime import datetime

def countryToEmoji(country):
    mapping = {
        "USA": "🇺🇸",
        "Canada": "🇨🇦",
        "Brazil": "🇧🇷",
        "UK": "🇬🇧",
        "France": "🇫🇷",
        "Belgium": "🇧🇪",
        "Netherlands": "🇳🇱",
        "Hungary": "🇭🇺",
        "South Korea": "🇰🇷",
        "Japan": "🇯🇵",
        "China": "🇨🇳",
        "Hong Kong": "🇭🇰",
        "Thailand": "🇹🇭",
        "Taiwan": "🇹🇼",
    }
    return mapping.get(country, country)

def formatDateRange(start_date, end_date):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if start.year == end.year:
            if start.month == end.month:
                return f"{start.strftime('%B')} {start.day}-{end.day}, {start.year}"
            else:
                return f"{start.strftime('%B')} {start.day} - {end.strftime('%B')} {end.day}, {start.year}"
        else:
            return f"{start.strftime('%B')} {start.day}, {start.year} - {end.strftime('%B')} {end.day}, {end.year}"
    except Exception:
        return f"{start_date} - {end_date}"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "site")
    csv_path = os.path.join(base_dir, "events.csv")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Failed to load CSV: {e}", file=sys.stderr)
        sys.exit(1)

    df.fillna('', inplace=True)

    multi_genre_events = df[df['Genre'] == "Multi-Genre"]

    genre_artists = {}
    for genre in ['POP', 'K-POP']:
        artists = sorted(df[df['Genre'] == genre]['Artist'].unique())
        genre_artists[genre] = [a for a in artists if a]

    region_groups = sorted(df['Region'].dropna().unique())

    env = Environment(loader=FileSystemLoader(template_dir))
    env.globals['countryToEmoji'] = countryToEmoji
    env.filters['formatDateRange'] = formatDateRange

    try:
        template = env.get_template("index.html.j2")
    except Exception as e:
        print(f"Failed to load template: {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    try:
        rendered_html = template.render(
            events=df.to_dict(orient="records"),
            multi_genre_events=multi_genre_events.to_dict(orient="records"),
            genre_artists=genre_artists,
            region_groups=region_groups,
            current_page='home',
            hero_title="🌟 Your Festival Countdown Starts Here!",
            hero_subtitle="From Coachella to Tomorrowland – track how many days are left until the music starts!"
        )
        with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(rendered_html)
    except Exception as e:
        print(f"Failed to render or write HTML: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        shutil.copy(os.path.join(template_dir, "style.css"), os.path.join(output_dir, "style.css"))
    except Exception as e:
        print(f"Failed to copy CSS: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

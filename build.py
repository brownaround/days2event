import pandas as pd
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os
import sys
import shutil

def countryToEmoji(country):
    mapping = {
        "USA": "🇺🇸",
        "Canada": "🇨🇦",
        "Brazil": "🇧🇷",
        "UK": "🇬🇧",
        "France": "🇫🇷",
        "Belgium": "🇧🇪",
        "Spain": "🇪🇸",
        "Italy": "🇮🇹",       
        "Netherlands": "🇳🇱",
        "Hungary": "🇭🇺",
        "South Korea": "🇰🇷",
        "Japan": "🇯🇵",
        "China": "🇨🇳",
        "Hong Kong": "🇭🇰",
        "Indonesia": "🇮🇩",
        "Philippines": "🇵🇭",
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

    df = pd.read_csv(csv_path)
    df.fillna('', inplace=True)
    df['Start Date Parsed'] = pd.to_datetime(df['Start Date'], errors='coerce')
    df = df.sort_values(by='Start Date Parsed')

    genre_artists = {}
    for genre in ['POP', 'K-POP']:
        artists = sorted(df[df['Genre'] == genre]['Artist'].unique())
        genre_artists[genre] = [a for a in artists if a]

    region_groups = sorted(df['Region'].dropna().unique())

    env = Environment(loader=FileSystemLoader(template_dir))
    env.globals['countryToEmoji'] = countryToEmoji
    env.filters['formatDateRange'] = formatDateRange

    template = env.get_template("index.html.j2")

    pages = [
        {'filename': 'index.html', 'current_page': 'home',
         'hero_title': "🌟 Your Festival Countdown Starts Here!",
         'hero_subtitle': "From Coachella to Tomorrowland – track how many days are left until the music starts!"},
        {'filename': 'multi-genre.html', 'current_page': 'multi-genre',
         'hero_title': "✨ Multi-Genre Festivals",
         'hero_subtitle': "Explore diverse music festivals worldwide."},
        {'filename': 'pop.html', 'current_page': 'pop',
         'hero_title': "🎶 POP Festival Highlights",
         'hero_subtitle': "Discover POP events and artists."},
        {'filename': 'k-pop.html', 'current_page': 'kpop',
         'hero_title': "🇰🇷🎵 K-POP Festival Highlights",
         'hero_subtitle': "Discover K-POP events and artists."},
        {'filename': 'edm.html', 'current_page': 'edm',
         'hero_title': "🪩 EDM Festival Highlights",
         'hero_subtitle': "Feel the beat at top EDM events."},
        {'filename': 'pride.html', 'current_page': 'pride',
         'hero_title': "🏳️‍🌈 PRIDE Festival Highlights",
         'hero_subtitle': "Celebrate diversity and love with PRIDE events."},
        {'filename': 'by-region.html', 'current_page': 'region',
         'hero_title': "📍 Explore Festivals by Region",
         'hero_subtitle': "Select your continent or region to find upcoming events nearby."}
    ]

    os.makedirs(output_dir, exist_ok=True)

    for page in pages:
        if page['current_page'] == 'home':
            events_filtered = df.to_dict(orient="records")
        elif page['current_page'] == 'multi-genre':
            events_filtered = df[df['Genre'] == 'Multi-Genre'].to_dict(orient="records")
        elif page['current_page'] == 'pop':
            events_filtered = df[df['Genre'] == 'POP'].to_dict(orient="records")
        elif page['current_page'] == 'kpop':
            events_filtered = df[df['Genre'] == 'K-POP'].to_dict(orient="records")
        elif page['current_page'] == 'edm':
            events_filtered = df[df['Genre'] == 'EDM'].to_dict(orient="records")
        elif page['current_page'] == 'pride':
            events_filtered = df[df['Genre'] == 'PRIDE'].to_dict(orient="records")
        elif page['current_page'] == 'region':
            events_filtered = df.to_dict(orient="records")
        else:
            events_filtered = df.to_dict(orient="records")

        rendered_html = template.render(
            events=events_filtered,
            genre_artists=genre_artists,
            region_groups=region_groups,
            current_page=page['current_page'],
            hero_title=page['hero_title'],
            hero_subtitle=page['hero_subtitle']
        )

        with open(os.path.join(output_dir, page['filename']), "w", encoding="utf-8") as f:
            f.write(rendered_html)

    shutil.copy(os.path.join(template_dir, "style.css"), os.path.join(output_dir, "style.css"))

if __name__ == "__main__":
    main()

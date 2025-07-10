import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import sys
import json

def generate_detail_pages(json_path, template_name, template_dir, output_dir):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            festivals = json.load(f)
    except Exception as e:
        print(f"Failed to load festivals JSON: {e}", file=sys.stderr)
        return

    try:
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
    except Exception as e:
        print(f"Failed to load detail page template: {e}", file=sys.stderr)
        return

    for fest in festivals:
        try:
            rendered = template.render(**fest)
            output_path = os.path.join(output_dir, f"{fest['slug']}.html")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(rendered)
        except Exception as e:
            print(f"Failed to render/write page for {fest.get('title', 'unknown')}: {e}", file=sys.stderr)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "site")
    csv_path = os.path.join(base_dir, "events.csv")
    json_path = os.path.join(base_dir, "festivals.json")

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Failed to load CSV: {e}", file=sys.stderr)
        sys.exit(1)

    df.fillna('', inplace=True)

    genres = sorted(df['Genre'].unique())
    genre_artists = {}
    for genre in ['POP', 'K-POP']:
        artists = sorted(df[df['Genre'] == genre]['Artist'].unique())
        genre_artists[genre] = [a for a in artists if a]

    continents = sorted(df['Continent'].unique())
    continent_regions = {}
    for cont in continents:
        regions = sorted(df[df['Continent'] == cont]['Region'].unique())
        continent_regions[cont] = [r for r in regions if r]

    env = Environment(loader=FileSystemLoader(template_dir))
    try:
        template = env.get_template("index.html.j2")
    except Exception as e:
        print(f"Failed to load template: {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    try:
        rendered_html = template.render(
            events=df.to_dict(orient="records"),
            genres=genres,
            genre_artists=genre_artists,
            continent_regions=continent_regions
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

    # ✅ 상세 페이지 생성 실행
    generate_detail_pages(json_path, "festival_template.html", template_dir, output_dir)

if __name__ == "__main__":
    main()

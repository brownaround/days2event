import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import shutil
import sys

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

    env = Environment(loader=FileSystemLoader(template_dir))
    try:
        template = env.get_template("index.html.j2")
    except Exception as e:
        print(f"Failed to load template: {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    try:
        rendered_html = template.render(events=df.to_dict(orient="records"))
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

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

def main():
    ensure_output_dir()
    df = pd.read_csv("events.csv")
    df.columns = df.columns.str.strip()

    env = get_jinja_env()

    # 메인(index.html): 전체 카드!
    template = env.get_template("index.j2")
    with open("site/index.html", "w", encoding="utf-8") as f:
        f.write(template.render(events=df.to_dict(orient="records")))

    # 장르별 페이지: 해당 장르 전체 카드!
    for filename, genre in genres:
        template_name = filename.replace(".html", ".j2")
        filtered = df[df["Genre"].str.strip().str.lower() == genre.lower()]
        if not os.path.exists(os.path.join("templates", template_name)):
            continue
        with open(f"site/{filename}", "w", encoding="utf-8") as f:
            f.write(
                env.get_template(template_name).render(events=filtered.to_dict(orient="records"))
            )

    # style.css 복사 (root -> site/)
    if os.path.exists("style.css"):
        with open("style.css", "rb") as fsrc, open("site/style.css", "wb") as fdst:
            fdst.write(fsrc.read())

    print("Build completed! All html files generated in /site.")

if __name__ == "__main__":
    main()

import os
import shutil
import markdown
import yaml

# =========================
# CONFIG
# =========================
#BASE_URL = "C:/Users/daehe/OneDrive/바탕 화면/Study/git_pages/dist"   # 🔥 반드시 repo 이름으로
BASE_URL = "/page"   # 🔥 반드시 repo 이름으로
POSTS_SRC = "posts"
TEMPLATE_DIR = "templates"
DIST_DIR = "dist"
POSTS_DIST = os.path.join(DIST_DIR, "posts")


# =========================
# UTILS
# =========================
def load_template(name):
    with open(os.path.join(TEMPLATE_DIR, name), encoding="utf-8") as f:
        return f.read()


def parse_markdown(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm)
    else:
        meta = {}
        body = raw

    html = markdown.markdown(
        body,
        extensions=["fenced_code", "tables"]
    )
    return meta, html


# =========================
# BUILD POSTS
# =========================
def build_posts(base_tpl, post_tpl):
    os.makedirs(POSTS_DIST, exist_ok=True)
    posts = []

    for file in sorted(os.listdir(POSTS_SRC)):
        if not file.endswith(".md"):
            continue

        meta, md_html = parse_markdown(os.path.join(POSTS_SRC, file))
        slug = file.replace(".md", "")
        out_rel = f"posts/{slug}.html"

        body_html = post_tpl.format(content=md_html)

        full_html = base_tpl.format(
            base_url=BASE_URL,
            title=meta.get("title", ""),
            content=body_html
        )

        with open(os.path.join(DIST_DIR, out_rel), "w", encoding="utf-8") as f:
            f.write(full_html)

        posts.append({
            "title": meta.get("title", ""),
            "url": f"{BASE_URL}/{out_rel}"
        })

    return posts


# =========================
# BUILD INDEX
# =========================
def build_index(base_tpl, index_tpl, posts):
    cards_html = "\n".join(
        f'<a class="card" href="{p["url"]}"><h2>{p["title"]}</h2></a>'
        for p in posts
    )

    body_html = index_tpl.format(cards=cards_html)

    full_html = base_tpl.format(
        base_url=BASE_URL,
        title="Daehee's Pages",
        content=body_html
    )

    with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(full_html)


# =========================
# COPY ASSETS
# =========================
def copy_assets():
    shutil.copy("style.css", os.path.join(DIST_DIR, "style.css"))


# =========================
# MAIN
# =========================
def main():
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)

    os.makedirs(DIST_DIR)

    base_tpl = load_template("base.html")
    index_tpl = load_template("index.html")
    post_tpl = load_template("post.html")

    posts = build_posts(base_tpl, post_tpl)
    build_index(base_tpl, index_tpl, posts)
    copy_assets()

    print("✔ build complete")


if __name__ == "__main__":
    main()

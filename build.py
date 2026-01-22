BASE_URL = "C:/Users/daehe/OneDrive/바탕 화면/Study/git_pages/dist"   # 🔥 반드시 repo 이름으로

import os
import re
import markdown
import yaml
import shutil

#BASE_URL = "/page"   # GitHub Pages project page
POSTS_DIR = "posts"
DIST_DIR = "dist"
TEMPLATE_DIR = "templates"

IMAGE_ZOOM_JS = """
<script>
document.addEventListener("DOMContentLoaded", function () {
  var images = document.querySelectorAll(".post-content img");
  var currentOverlay = null;

  function closeOverlay() {
    if (currentOverlay) {
      currentOverlay.remove();
      currentOverlay = null;
    }
  }

  images.forEach(function (img) {
    img.style.cursor = "zoom-in";

    img.addEventListener("click", function () {
      closeOverlay();

      var overlay = document.createElement("div");
      overlay.className = "image-overlay";

      var zoomedImg = document.createElement("img");
      zoomedImg.src = img.src;

      overlay.appendChild(zoomedImg);
      document.body.appendChild(overlay);

      currentOverlay = overlay;

      overlay.addEventListener("click", closeOverlay);
    });
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeOverlay();
    }
  });
});
</script>
"""


def copy_images():
    src = os.path.join(POSTS_DIR, "images")
    dst = os.path.join(DIST_DIR, "posts", "images")

    if os.path.exists(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def parse_markdown(md_text: str):
    """
    - markdown -> html
    - extract h1, h2
    - inject id into headings
    - generate TOC html
    """
    html = markdown.markdown(md_text, extensions=["fenced_code"])

    toc = []
    used_ids = set()

    def replace_heading(match):
        level = int(match.group(1))
        title = match.group(2)

        if level > 2:
            return match.group(0)

        base_id = slugify(title)
        hid = base_id
        i = 1
        while hid in used_ids:
            hid = f"{base_id}-{i}"
            i += 1
        used_ids.add(hid)

        toc.append((level, title, hid))
        return f'<h{level} id="{hid}">{title}</h{level}>'

    html = re.sub(r"<h([1-6])>(.*?)</h\1>", replace_heading, html)

    toc_html = build_toc_html(toc)
    return html, toc_html


def build_toc_html(toc):
    if not toc:
        return ""

    html = ['<nav class="toc"><h3>Contents</h3><ul>']
    prev_level = 1

    for level, title, hid in toc:
        if level == 1:
            if prev_level == 2:
                html.append("</ul></li>")
            html.append(
                f'<li><a href="#{hid}">{title}</a><ul>'
            )
        elif level == 2:
            html.append(
                f'<li class="toc-child"><a href="#{hid}">{title}</a></li>'
            )
        prev_level = level

    html.append("</ul></li></ul></nav>")
    return "\n".join(html)


def load_template(name):
    with open(os.path.join(TEMPLATE_DIR, name), encoding="utf-8") as f:
        return f.read()


def build():
    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "posts"), exist_ok=True)

    base_tpl = load_template("base.html")
    post_tpl = load_template("post.html")

    index_cards = []

    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith(".md"):
            continue

        path = os.path.join(POSTS_DIR, filename)
        with open(path, encoding="utf-8") as f:
            raw = f.read()

        fm, body = raw.split("---", 2)[1:]
        meta = yaml.safe_load(fm)

        html_body, toc_html = parse_markdown(body)

        post_html = post_tpl.format(
            title=meta["title"],
            content=html_body,
            toc=toc_html,
            extra_js=IMAGE_ZOOM_JS
        )

        full_html = base_tpl.format(
            title=meta["title"],
            content=post_html,
            base_url=BASE_URL
        )

        out_name = filename.replace(".md", ".html")
        out_path = os.path.join(DIST_DIR, "posts", out_name)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        index_cards.append(
            f'''
            <a class="card" href="{BASE_URL}/posts/{out_name}">
              <h2>{meta["title"]}</h2>
              <p>{meta.get("description", "")}</p>
            </a>
            '''
        )

    index_html = base_tpl.format(
        title="Home",
        base_url=BASE_URL,
        content=f'''
        <section class="card-list">
            {''.join(index_cards)}
        </section>
        '''
    )

    with open(os.path.join(DIST_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # copy css
    with open("style.css", encoding="utf-8") as src:
        with open(os.path.join(DIST_DIR, "style.css"), "w", encoding="utf-8") as dst:
            dst.write(src.read())


if __name__ == "__main__":
    copy_images()
    build()

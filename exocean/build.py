#!/usr/bin/env python3
"""
exocean — static site generator.

Reads the JSON files in content/ and writes plain HTML to the repo root.
No dependencies beyond the Python standard library.

    python3 build.py

Everything an editor would ever want to change lives in content/*.json.
Nothing in this file needs touching to add a person, a project or a news item.
"""

from __future__ import annotations

import json
import pathlib
import shutil
from html import escape

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT


def load(name: str) -> dict:
    with open(CONTENT / f"{name}.json", encoding="utf-8") as fh:
        return json.load(fh)


SITE = load("site")
TEAM = load("team")
PROJECTS = load("projects")
NEWS = load("news")

ALL_MEMBERS = {m["slug"]: m for g in TEAM["groups"] for m in g["members"]}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def rel(depth: int, path: str) -> str:
    """Resolve a root-relative path for a page nested `depth` levels down."""
    return ("../" * depth) + path


def asset(depth: int, filename: str) -> str:
    return rel(depth, f"assets/img/{filename}")


def email_span(user: str, domain: str, cls: str = "eml") -> str:
    """Write an address the way the original site does — assembled by JS, not
    sitting in the markup for harvesters."""
    return f'<span class="{cls}" data-u="{escape(user)}" data-d="{escape(domain)}"></span>'


def person_link(depth: int, slug: str, label: str | None = None) -> str:
    member = ALL_MEMBERS.get(slug)
    label = label or (member["name"] if member else slug)
    if member and member.get("bio"):
        return f'<a href="{rel(depth, "people/" + slug + ".html")}">{escape(label)}</a>'
    return escape(label)


def initials(name: str) -> str:
    parts = [p for p in name.replace("-", " ").split() if p and p[0].isalpha()]
    if not parts:
        return "?"
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


def bullets(items: list[str]) -> str:
    lis = "\n".join(f"      <li>{i}</li>" for i in items)
    return f'    <ul class="bullets">\n{lis}\n    </ul>'


# --------------------------------------------------------------------------
# page chrome
# --------------------------------------------------------------------------

def head(depth: int, title: str, description: str, active: str) -> str:
    full_title = SITE["name"] if title == SITE["name"] else f'{SITE["name"]} — {title}'
    nav_items = []
    for item in SITE["nav"]:
        current = ' aria-current="page"' if item["href"] == active else ""
        nav_items.append(
            f'        <li><a href="{rel(depth, item["href"])}"{current}>{escape(item["label"])}</a></li>'
        )
    nav = "\n".join(nav_items)
    hero = asset(depth, "hero-banner.webp")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(full_title)}</title>
<meta name="description" content="{escape(description)}">
<meta property="og:title" content="{escape(full_title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{hero}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{asset(depth, 'favicon.png')}">
<link rel="apple-touch-icon" href="{asset(depth, 'favicon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cabin:ital,wght@0,400;0,500;0,700;1,400&display=swap">
<link rel="stylesheet" href="{rel(depth, 'assets/css/style.css')}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="sheet">

  <header class="banner" style="background-image:url('{hero}')">
    <a href="{rel(depth, 'index.html')}" aria-label="{escape(SITE['name'])} — home">
      <span class="visually-hidden">{escape(SITE['name'])}</span>
    </a>
    <p class="tagline">{escape(SITE['tagline'])}</p>
  </header>

  <nav class="nav" aria-label="Main">
    <ul>
{nav}
    </ul>
  </nav>

  <main id="main">
"""


def foot(depth: int) -> str:
    links = "\n".join(
        f'        <li><a href="{rel(depth, i["href"])}">{escape(i["label"])}</a></li>'
        for i in SITE["nav"]
    )
    f = SITE["footer"]
    return f"""  </main>

  <footer class="site-footer">
    <img class="partners" src="{asset(depth, f['partners_image'])}" alt="{escape(f['partners_alt'])}" loading="lazy">
    <nav aria-label="Footer">
      <ul>
{links}
        <li><a href="{escape(SITE['bluesky'])}">Bluesky</a></li>
      </ul>
    </nav>
    <p class="colophon">
      {escape(SITE['name'])} · {escape(SITE['tagline'])} ·
      <a href="{escape(f['cerege_url'])}">CEREGE</a>,
      Technop&ocirc;le de l'Arbois-M&eacute;diterran&eacute;e, Aix-en-Provence, France
    </p>
  </footer>

</div>
<script src="{rel(depth, 'assets/js/main.js')}"></script>
</body>
</html>
"""


def write(path: str, depth: int, title: str, description: str, active: str, body: str) -> None:
    target = OUT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(head(depth, title, description, active) + body + foot(depth), encoding="utf-8")
    print(f"  {path}")


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def build_home() -> None:
    h = SITE["home"]
    d = 0
    founders = "\n".join(
        f'      <li><span class="who">{person_link(d, f["slug"], f["name"])},</span> {f["blurb"]}</li>'
        for f in h["founders"]
    )
    body = f"""    <section class="section">
      <div class="measure">
        <h1>{escape(h['title'])}</h1>
        <p class="lede">{escape(h['lede'])}</p>
        <hr class="rule">
        {"".join(f"<p>{p}</p>" for p in h["intro"])}

        <p class="btn-row"><a class="btn" href="expertise.html">Check our expertise</a></p>

        <figure>
          <img src="{asset(d, h['founders_photo'])}" alt="The three exocean founders in the laboratory" width="1400" height="778">
          <figcaption>{escape(h['founders_caption'])}</figcaption>
        </figure>

        <p>{escape(h['founders_intro'])}</p>
        <ul class="founder-list">
{founders}
        </ul>

        <p class="btn-row"><a class="btn" href="projects.html">Explore all our projects</a></p>

        <div class="callout">
          <p class="callout-title">{escape(h['questions_title'])}</p>
{bullets(h['questions'])}
        </div>

        <div class="btn-row two">
          <a class="btn" href="team.html">Meet the team</a>
          <a class="btn" href="contact.html">Collaborate with us</a>
        </div>

        <h2>{escape(h['where_title'])}</h2>
        <hr class="rule short">
        {"".join(f"<p>{p}</p>" for p in h["where"])}

        <figure>
          <img src="{asset(d, h['where_photo'])}" alt="Aerial view of the CEREGE campus on the plateau de l'Arbois" loading="lazy" width="1400" height="568">
          <figcaption>{escape(h['where_caption'])}</figcaption>
        </figure>

        <p class="btn-row"><a class="btn" href="{escape(SITE['footer']['cerege_url'])}">More about CEREGE</a></p>

        <div class="btn-row two">
          <a class="btn" href="expertise.html">Our Expertise</a>
          <a class="btn" href="news.html">News &amp; Highlights</a>
        </div>
        <div class="btn-row two">
          <a class="btn" href="projects.html">Deep dive in our projects</a>
          <a class="btn primary" href="contact.html">Want to be part of the adventure?</a>
        </div>
      </div>
    </section>
"""
    write("index.html", d, SITE["name"], SITE["description"], "index.html", body)


def build_expertise() -> None:
    e = SITE["expertise"]
    d = 0
    items = "\n".join(
        f"""        <article class="expertise-item">
          <h2>{escape(i['title'])}</h2>
          <p>{i['body']}</p>
        </article>"""
        for i in e["items"]
    )
    body = f"""    <section class="section">
      <div class="measure">
        <h1>{escape(e['title'])}</h1>
        <p class="lede">{escape(e['lede'])}</p>
        <hr class="rule">
        <figure>
          <img src="{asset(d, e['hero'])}" alt="Inside the exocean laboratory at CEREGE" width="1400" height="934">
        </figure>
{items}
        <div class="btn-row two">
          <a class="btn" href="projects.html">Explore our projects</a>
          <a class="btn" href="news.html">News &amp; Highlights</a>
        </div>
        <p class="btn-row"><a class="btn primary" href="contact.html">Let's connect</a></p>
      </div>
    </section>
"""
    write("expertise.html", d, e["title"],
          "Carbonate system measurements, chemical microprofiling, foraminifera cultures, pressurized and rotating disk reactors at the exocean laboratory, CEREGE.",
          "expertise.html", body)


def build_projects() -> None:
    d = 0
    cards = []
    for p in PROJECTS["projects"]:
        tag = '<span class="tag">Completed</span>' if p.get("completed") else ""
        name = p.get("short_name", p["name"])
        cards.append(f"""          <a class="card" href="projects/{p['slug']}.html">
            <div class="thumb"><img src="{asset(d, p['card_image'])}" alt="" loading="lazy"></div>
            <div class="body">
              {tag}
              <p class="name">{escape(name)}</p>
              <p class="blurb">{escape(p['card_text'])}</p>
            </div>
          </a>""")
    body = f"""    <section class="section">
      <div class="measure">
        <h1>{escape(PROJECTS['title'])}</h1>
        <p class="lede">{escape(PROJECTS['lede'])}</p>
        <hr class="rule">
        <div class="cards">
{chr(10).join(cards)}
        </div>
      </div>
    </section>
"""
    write("projects.html", d, PROJECTS["title"],
          "Deep-C, MANGO, DYNAMITE, ForCry and ASPERGE — the research projects running at the exocean laboratory, CEREGE.",
          "projects.html", body)

    for p in PROJECTS["projects"]:
        build_project(p)


def build_project(p: dict) -> None:
    d = 1
    parts = []

    if p.get("hero_image"):
        parts.append(f"""        <figure>
          <img src="{asset(d, p['hero_image'])}" alt="{escape(p['name'])}" loading="lazy">
        </figure>""")

    parts += [f"        <p>{t}</p>" for t in p["intro"]]

    for s in p["sections"]:
        parts.append('        <div class="callout">')
        parts.append(f'          <p class="callout-title">{escape(s["heading"])}</p>')
        if s.get("intro"):
            parts.append(f"          <p>{s['intro']}</p>")
        if s.get("body"):
            parts.append(f"          <p>{s['body']}</p>")
        if s.get("items"):
            parts.append(bullets(s["items"]))
        if s.get("outro"):
            parts.append(f"          <p>{s['outro']}</p>")
        parts.append("        </div>")

    # -- metadata block -----------------------------------------------------
    meta = []
    if p.get("keywords"):
        meta.append(f'          <dt>Keywords</dt><dd class="keywords">{escape(p["keywords"])}</dd>')

    def credit(entry: dict) -> str:
        if entry.get("slug"):
            txt = person_link(d, entry["slug"], entry["name"])
        elif entry.get("url"):
            txt = f'<a href="{escape(entry["url"])}">{escape(entry["name"])}</a>'
        else:
            txt = escape(entry["name"])
        if entry.get("email_user"):
            txt += " " + email_span(entry["email_user"], entry["email_domain"])
        return txt

    if p.get("lead"):
        meta.append(f'          <dt>{escape(p["lead"]["label"])}</dt><dd>{credit(p["lead"])}</dd>')
    if p.get("colead"):
        meta.append(f'          <dt>{escape(p["colead"]["label"])}</dt><dd>{credit(p["colead"])}</dd>')
    if p.get("participants"):
        names = ", ".join(credit(x) for x in p["participants"])
        meta.append(f"          <dt>CEREGE team</dt><dd>{names}</dd>")
    if p.get("former"):
        meta.append(f'          <dt>Former team members</dt><dd>{escape(", ".join(p["former"]))}</dd>')
    if p.get("external"):
        ext = "<br>".join(p["external"])
        meta.append(f"          <dt>External collaborators</dt><dd>{ext}</dd>")

    if meta:
        parts.append(f"""        <div class="meta">
          <h3>Who is on it</h3>
          <dl>
{chr(10).join(meta)}
          </dl>
        </div>""")

    if p.get("note"):
        parts.append(f'        <p class="keywords" style="margin-top:1.2rem">{escape(p["note"])}</p>')

    if p.get("funders"):
        imgs = "".join(
            f'<img src="{asset(d, f)}" alt="" loading="lazy">' for f in p["funders"]
        )
        parts.append(f"""        <p class="keywords" style="margin-top:1.6rem"><strong>Funded and hosted by</strong></p>
        <div class="funders">{imgs}</div>""")

    body = f"""    <section class="section">
      <div class="measure">
        <div class="proj-head">
          <span class="funder">{escape(p['funder'])}</span>
          <h1>{escape(p.get('short_name', p['name']))}</h1>
          <p class="subtitle">{escape(p['subtitle'])}</p>
        </div>
        <hr class="rule">
{chr(10).join(parts)}
        <div class="btn-row two">
          <a class="btn primary" href="{rel(d, 'contact.html')}">Contact us</a>
          <a class="btn" href="{rel(d, 'projects.html')}">Explore all our projects</a>
        </div>
        <a class="back-link" href="{rel(d, 'projects.html')}">All projects</a>
      </div>
    </section>
"""
    write(f"projects/{p['slug']}.html", d, p.get("short_name", p["name"]),
          p["subtitle"], "projects.html", body)


def build_team() -> None:
    d = 0
    groups = []
    for g in TEAM["groups"]:
        cards = []
        for m in g["members"]:
            if m.get("photo"):
                avatar = f'<div class="avatar"><img src="{asset(d, m["photo"])}" alt="{escape(m["name"])}" loading="lazy"></div>'
            else:
                avatar = f'<div class="avatar placeholder" aria-hidden="true">{escape(initials(m["name"]))}</div>'
            role = f'<span class="prole">{escape(m["role"])}</span>' if m.get("role") else ""
            inner = f"""{avatar}
              <span class="pname">{escape(m['name'])}</span>
              <span class="aff">{escape(m['affiliation'])}</span>
              {role}"""
            if m.get("bio"):
                cards.append(f'            <a class="person" href="people/{m["slug"]}.html">\n              {inner}\n            </a>')
            else:
                cards.append(f'            <div class="person">\n              {inner}\n            </div>')
        groups.append(f"""        <section class="team-group">
          <h2>{escape(g['heading'])}</h2>
          <div class="people">
{chr(10).join(cards)}
          </div>
        </section>""")

    body = f"""    <section class="section">
      <div class="measure">
        <h1>{escape(TEAM['title'])}</h1>
        <p class="lede">{escape(TEAM['lede'])}</p>
        <hr class="rule">
{chr(10).join(groups)}
        <p class="btn-row"><a class="btn primary" href="contact.html">Want to collaborate? Join the team!</a></p>
      </div>
    </section>
"""
    write("team.html", d, TEAM["title"],
          "The founders, scientific team and collaborators of the exocean laboratory at CEREGE, Aix-en-Provence.",
          "team.html", body)

    for g in TEAM["groups"]:
        for m in g["members"]:
            if m.get("bio"):
                build_person(m)


def build_person(m: dict) -> None:
    d = 1
    if m.get("photo"):
        avatar = f'<div class="avatar"><img src="{asset(d, m["photo"])}" alt="{escape(m["name"])}"></div>'
    else:
        avatar = f'<div class="avatar placeholder" aria-hidden="true">{escape(initials(m["name"]))}</div>'

    role = f'<p class="prole">{escape(m["role"])}</p>' if m.get("role") else ""
    greeting = f'<p class="greeting">{escape(m["greeting"])}</p>' if m.get("greeting") else ""
    paras = "\n".join(f"        <p>{escape(t)}</p>" for t in m["bio"])

    contact = ""
    if m.get("email_user"):
        contact = (f'        <p style="margin-top:1.2rem">You can contact me directly at '
                   f'{email_span(m["email_user"], m["email_domain"])}</p>')

    links = ""
    if m.get("links"):
        items = "".join(f'<li><a href="{escape(l["url"])}">{escape(l["label"])}</a></li>' for l in m["links"])
        links = f'        <p style="margin-top:1.4rem"><strong>Find more about my scientific work:</strong></p>\n        <ul class="links-list">{items}</ul>'

    body = f"""    <section class="section">
      <div class="measure">
        <div class="bio-head">
          {avatar}
          <div>
            <h1>{escape(m['name'])}</h1>
            <p class="aff">{escape(m['affiliation'])}</p>
            {role}
          </div>
        </div>
        <hr class="rule short">
{greeting}
{paras}
{contact}
{links}
        <a class="back-link" href="{rel(d, 'team.html')}">Meet the other team members</a>
      </div>
    </section>
"""
    write(f"people/{m['slug']}.html", d, m["name"],
          f"{m['name']} — {m['affiliation']}. Member of the exocean laboratory at CEREGE.",
          "team.html", body)


def build_news() -> None:
    d = 0
    items = []
    for n in NEWS["items"]:
        blocks = []
        for b in n["body"]:
            if b["type"] == "q":
                blocks.append(f'        <p class="qa">{escape(b["text"])}</p>')
            elif b["type"] == "callout":
                blocks.append(f'        <div class="callout"><p>{b["text"]}</p></div>')
            else:
                blocks.append(f'        <p>{b["text"]}</p>')

        rm = ""
        if n.get("readmore"):
            lis = "".join(f'<li><a href="{escape(l["url"])}">{escape(l["label"])}</a></li>' for l in n["readmore"])
            rm = f"""        <div class="readmore">
          <p class="rm-label">{escape(n['readmore_label'])}</p>
          <ul>{lis}</ul>
        </div>"""

        items.append(f"""        <article class="news-item" id="{escape(n['id'])}">
          <h2>{escape(n['headline'])}</h2>
          <figure>
            <img src="{asset(d, n['image'])}" alt="" loading="lazy">
            <figcaption>{n['image_caption']}<span class="credit">{escape(n['image_credit'])}</span></figcaption>
          </figure>
{chr(10).join(blocks)}
{rm}
        </article>""")

    media = NEWS["media"]
    groups = []
    for g in media["groups"]:
        lis = "".join(f'<li><a href="{escape(l["url"])}">{escape(l["label"])}</a></li>' for l in g["links"])
        groups.append(f"""          <div class="media-group">
            <h3>{escape(g['heading'])}</h3>
            <ul class="media-links">{lis}</ul>
          </div>""")

    body = f"""    <section class="section">
      <div class="measure">
        <h1>{escape(NEWS['title'])}</h1>
        <p class="lede">{escape(NEWS['lede'])}</p>
        <hr class="rule">
        <h2 style="margin-top:0">{escape(NEWS['spotlight_label'])}</h2>
{chr(10).join(items)}

        <section class="meta" style="margin-top:3rem">
          <h2 style="margin-top:0">{escape(media['title'])}</h2>
          <figure>
            <img src="{asset(d, media['image'])}" alt="A pteropod" loading="lazy">
            <figcaption>{escape(media['image_caption'])}</figcaption>
          </figure>
{chr(10).join(groups)}
        </section>

        <p class="btn-row"><a class="btn primary" href="contact.html">Want to collaborate?</a></p>
      </div>
    </section>
"""
    write("news.html", d, NEWS["title"],
          "Awards, fellowships, reports and media coverage from the exocean laboratory at CEREGE.",
          "news.html", body)


def build_contact() -> None:
    c = SITE["contact"]
    d = 0
    user, domain = SITE["email"].split("@")
    address = "<br>".join(escape(line) for line in SITE["address"])
    body = f"""    <section class="section">
      <div class="measure">
        <h1>{escape(c['title'])}</h1>
        <p class="lede">{escape(c['lede'])}</p>
        <hr class="rule">
        <p>{escape(c['body'])}</p>

        <div class="contact-card">
          <p class="brand">{escape(SITE['name'])}<small>{escape(SITE['tagline'])}</small></p>
          <p class="eml-wrap">{email_span(user, domain)}</p>
          <address>{address}</address>
        </div>

        <div class="btn-row two">
          <a class="btn" href="{escape(SITE['bluesky'])}">Follow us on Bluesky</a>
          <a class="btn" href="news.html">News &amp; Highlights</a>
        </div>
      </div>
    </section>
"""
    write("contact.html", d, c["title"],
          "Get in touch with the exocean laboratory at CEREGE, Aix-en-Provence.",
          "contact.html", body)


def build_404() -> None:
    d = 0
    body = """    <section class="section">
      <div class="measure">
        <h1>Page not found</h1>
        <p class="lede">- That page has drifted off into the abyss.</p>
        <hr class="rule">
        <p>The page you were looking for doesn't exist, or it has moved.</p>
        <div class="btn-row two">
          <a class="btn primary" href="/index.html">Back to the lab</a>
          <a class="btn" href="/contact.html">Contact us</a>
        </div>
      </div>
    </section>
"""
    write("404.html", d, "Page not found", "Page not found.", "", body)


def build_extras() -> None:
    """robots.txt and a sitemap, so the site is findable."""
    pages = ["index.html", "expertise.html", "projects.html", "team.html", "news.html", "contact.html"]
    pages += [f"projects/{p['slug']}.html" for p in PROJECTS["projects"]]
    pages += [f"people/{m['slug']}.html" for m in ALL_MEMBERS.values() if m.get("bio")]
    base = SITE.get("baseurl") or ""
    urls = "\n".join(f"  <url><loc>{base}/{p}</loc></url>" for p in pages)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("  sitemap.xml, robots.txt, .nojekyll")


if __name__ == "__main__":
    print("Building exocean…")
    build_home()
    build_expertise()
    build_projects()
    build_team()
    build_news()
    build_contact()
    build_404()
    build_extras()
    print("Done.")

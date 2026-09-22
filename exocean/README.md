# exocean — lab website

The website of **exocean**, the Experimental Oceanology Laboratory at CEREGE,
Aix-en-Provence. Plain static HTML, no paid hosting, no subscription.

**Live site:** _(GitHub Pages URL goes here once Pages is switched on)_

---

## The short version

All the words and people live in four text files inside `content/`.
Everything else is generated.

| File | What's in it |
|---|---|
| `content/site.json` | Home page, Expertise page, contact details, menu |
| `content/team.json` | Every person, their photo, bio and links |
| `content/projects.json` | Deep-C, MANGO, DYNAMITE, ForCry, ASPERGE |
| `content/news.json` | News items and the press/media lists |

Change one of those, and the site rebuilds itself. You never have to touch HTML.

---

## How a change actually happens

**Automatically.** A GitHub Action watches `content/` and `assets/`. When one of
those files changes, it re-runs the generator and publishes the result. Edit a
JSON file in GitHub's web editor, click *Commit*, and the live site updates about
a minute later.

**Or locally**, if you have the folder on your machine:

```bash
python3 build.py
```

No installation, no dependencies — just Python 3, which macOS already has.

---

## Adding things

**A new team member** — open `content/team.json`, copy an existing block inside
the right group, change the fields. Drop their photo in `assets/img/` (square
works best, 640×640 or larger) and put the filename in `"photo"`.
Set `"photo": null` and they get a neat initials tile instead.

Anyone with a non-empty `"bio"` automatically gets their own page.
Anyone with `"bio": []` appears as a card only — which is how the external
collaborators are set up.

**A news item** — open `content/news.json` and copy an existing item to the top
of the `items` list. Body blocks come in three flavours:
`{"type": "p"}` for a paragraph, `{"type": "q"}` for an interview question, and
`{"type": "callout"}` for a highlighted box.

**A project** — copy a block in `content/projects.json`. Add
`"completed": true` to get the *Completed* tag.

HTML is allowed inside any text field (`<strong>`, `<em>`, `<a href="…">`),
which is how the bold phrases and inline links are done.

---

## E-mail addresses

Addresses are never written into the HTML. They're stored as
`"email_user"` + `"email_domain"` and assembled in the browser, so address
harvesters don't pick them up. This mirrors how the old Owlstown site did it.

---

## What's in the repo

```
content/          the four content files — this is what you edit
build.py          the generator; turns content/ into HTML
assets/css/       one stylesheet
assets/js/        one small script (e-mail assembly)
assets/img/       every photo, logo and figure
index.html        ┐
expertise.html    │
projects.html     │  generated — don't edit these by hand,
team.html         │  build.py will overwrite them
news.html         │
contact.html      │
projects/*.html   │
people/*.html     ┘
sitemap.xml       generated
404.html          generated
```

---

## Hosting

Static files. GitHub Pages serves them for free from this repo
(*Settings → Pages → Deploy from a branch → `main` / root*).

To put it on a custom domain later — `exocean.fr`, say — add a file called
`CNAME` at the top level containing just the domain, then point the domain's DNS
at GitHub. The domain itself costs around €10–15 a year; the hosting stays free.

---

## Known difference from the old site

The old Owlstown site had a **contact form**. A static site can't process a form
on its own. Right now the Contact page gives the lab's address as a clickable
`mailto:` link instead. If a real form is wanted, Formspree or Web3Forms both
have free tiers and need one line of HTML.

---

## Credits

Photography © Elodie Gazquez, © SEMEPA / CEREGE, © Jaime Suárez-Ibarra,
as credited on each image. Logo and brand: exocean.

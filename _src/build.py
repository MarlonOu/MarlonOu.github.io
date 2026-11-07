#!/usr/bin/env python3
# 產生「去處」官網三種語言的頁面：繁中在 /whereto/，英文在 /whereto/en/，日文在 /whereto/ja/。
# 網站根目錄是個人首頁（index.html，手寫，不經此腳本）；舊網址（/privacy.html、/en/ 等）產生轉址頁，App Store 上填的連結仍然有效。
# 內容在 _src/<語言>/<頁面>.html（第一、二行註解是 title、description），共用的頁首、語言切換、頁尾在這裡。
# 用法：在網站 repo 根目錄執行 `python3 _src/build.py`
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://marlonou.github.io"
LANGS = {
    "zh": {"dir": "whereto/", "html": "zh-Hant-TW", "brand": "去處", "nav": ["首頁", "支援", "隱私權"], "navlabel": "網站",
           "links": ["功能", "隱私", "價格"], "footer": ["支援", "隱私權政策"], "copy": "© 2026 去處 Whereto", "switch": "語言",
           "skip": "跳到主要內容", "get": "下載", "store": "在 App Store 查看",
           "theme": ["切換深色模式", "切換淺色模式"], "tagline": "每張照片，都有去處。",
           "fonts": "family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=Noto+Serif+TC:wght@500;700;900"},
    "en": {"dir": "whereto/en/", "html": "en", "brand": "Whereto", "nav": ["Home", "Support", "Privacy"], "navlabel": "Site",
           "links": ["Features", "Privacy", "Pricing"], "footer": ["Support", "Privacy Policy"], "copy": "© 2026 Whereto", "switch": "Language",
           "skip": "Skip to content", "get": "Get the app", "store": "View on the App Store",
           "theme": ["Switch to dark mode", "Switch to light mode"], "tagline": "Every photo has somewhere to go.",
           "fonts": "family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400"},
    "ja": {"dir": "whereto/ja/", "html": "ja", "brand": "Whereto", "nav": ["ホーム", "サポート", "プライバシー"], "navlabel": "サイト",
           "links": ["機能", "プライバシー", "価格"], "footer": ["サポート", "プライバシーポリシー"], "copy": "© 2026 Whereto", "switch": "言語",
           "skip": "本文へ移動", "get": "入手", "store": "App Store で見る",
           "theme": ["ダークモードに切り替え", "ライトモードに切り替え"], "tagline": "すべての写真に、行き先を。",
           "fonts": "family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=Noto+Serif+JP:wght@500;700;900"},
}
APP_STORE = "https://apps.apple.com/app/id6830008884"
PAGES = ["index", "support", "privacy"]
NAMES = {"zh": "繁中", "en": "EN", "ja": "日本語"}
LONG = {"zh": "繁體中文", "en": "English", "ja": "日本語"}
HREFLANG = {"zh": "zh-Hant", "en": "en", "ja": "ja"}


def url(lang, page):
    return "/" + LANGS[lang]["dir"] + ("" if page == "index" else page + ".html")


def build(lang, page):
    L = LANGS[lang]
    src = open(os.path.join(ROOT, "_src", lang, page + ".html")).read()
    title = re.search(r"<!--title:(.*?)-->", src).group(1)
    desc = re.search(r"<!--desc:(.*?)-->", src).group(1)
    body = re.sub(r"<!--(title|desc):.*?-->\n", "", src).replace('src="icon.png"', 'src="/whereto/icon.png"')
    if page != "index":
        body = body.replace("<main>", '<main id="main" class="doc">', 1)
    home = url(lang, "index")
    # 首頁內用錨點，其他頁連回首頁的段落
    anchor = (lambda a: "#" + a) if page == "index" else (lambda a: home + "#" + a)
    links = "\n".join(
        f'      <a href="{h}">{t}</a>' for h, t in zip([anchor("features"), anchor("privacy"), anchor("pricing")], L["links"]))
    switch = "".join(
        f'<a href="{url(l, page)}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}" data-lang="{l}" aria-label="{LONG[l]}"'
        f'{" aria-current=\"true\"" if l == lang else ""}>{NAMES[l]}</a>' for l in LANGS)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{BASE}{url(l, page)}">' for l in LANGS)
    # 繁中首頁：沒選過語言時，依瀏覽器語言導到英文或日文版
    redirect = ""
    if lang == "zh" and page == "index":
        redirect = """<script>
try{if(!localStorage.getItem('lang')){var l=(navigator.languages&&navigator.languages[0]||navigator.language||'').toLowerCase();
if(l.indexOf('zh')!==0){location.replace(l.indexOf('ja')===0?'/whereto/ja/':'/whereto/en/')}}}catch(e){}
</script>
"""
    # 主題在 CSS 載入前決定，避免閃一下
    theme = """<script>try{var t=localStorage.getItem('wt-theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>"""
    return f"""<!doctype html>
<html lang="{L["html"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="apple-itunes-app" content="app-id=6830008884">
<meta name="theme-color" content="#F6F4F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F0E0D" media="(prefers-color-scheme: dark)">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE}/whereto/icon.png">
<link rel="icon" href="/whereto/favicon.png">
<link rel="apple-touch-icon" href="/whereto/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{L["fonts"]}&display=swap">
<link rel="stylesheet" href="/whereto/style.css">
{alternates}
<link rel="alternate" hreflang="x-default" href="{BASE}{url("en", page)}">
{theme}
<noscript><style>.rv{{opacity:1;transform:none}}.display .line>span{{transform:none}}</style></noscript>
{redirect}<script src="/whereto/site.js" defer></script>
</head>
<body class="page-{page}">
<a class="skip" href="#main">{L["skip"]}</a>
<div class="progress" aria-hidden="true"></div>
<header class="nav" id="nav">
  <div class="wrap">
    <a class="brand" href="{home}"><img src="/whereto/icon.png" alt="" width="34" height="34">{L["brand"]}</a>
    <nav class="nav-links" aria-label="{L["navlabel"]}">
{links}
    </nav>
    <div class="nav-tools">
      <div class="lang" role="group" aria-label="{L["switch"]}">{switch}</div>
      <button class="icon-btn" id="themeBtn" type="button" aria-label="{L["theme"][0]}" data-dark="{L["theme"][0]}" data-light="{L["theme"][1]}">
        <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6l1.4 1.4M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/></svg>
      </button>
      <a class="btn btn-sm" href="{APP_STORE}">{L["get"]}</a>
    </div>
  </div>
</header>

{body.strip()}

<footer class="foot">
  <div class="wrap">
    <div class="foot-brand">
      <a class="brand" href="{home}"><img src="/whereto/icon.png" alt="" width="34" height="34">{L["brand"]}</a>
      <p>{L["tagline"]}</p>
    </div>
    <nav class="foot-links" aria-label="{L["navlabel"]}">
      <a href="{url(lang, "support")}">{L["footer"][0]}</a>
      <a href="{url(lang, "privacy")}">{L["footer"][1]}</a>
      <a href="{APP_STORE}">{L["store"]}</a>
      <a href="mailto:quchu.app@gmail.com">quchu.app@gmail.com</a>
    </nav>
    <p class="foot-copy">{L["copy"]}</p>
  </div>
</footer>
</body>
</html>
"""


for lang, L in LANGS.items():
    os.makedirs(os.path.join(ROOT, L["dir"]), exist_ok=True)
    for page in PAGES:
        out = os.path.join(ROOT, L["dir"], page + ".html")
        open(out, "w").write(build(lang, page))
        print("寫入", os.path.relpath(out, ROOT))


# 舊網址轉址：網站改版前「去處」放在根目錄
OLD_DIRS = {"zh": "", "en": "en/", "ja": "ja/"}


def stub(lang, page):
    target = url(lang, page)
    return f"""<!doctype html>
<html lang="{LANGS[lang]["html"]}">
<head>
<meta charset="utf-8">
<title>{"去處 Whereto" if lang == "zh" else "Whereto"}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{BASE}{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace("{target}"+location.search+location.hash)</script>
</head>
<body><p><a href="{target}">{BASE}{target}</a></p></body>
</html>
"""


for lang, old in OLD_DIRS.items():
    for page in PAGES:
        if lang == "zh" and page == "index":
            continue  # 根目錄首頁是個人首頁
        os.makedirs(os.path.join(ROOT, old), exist_ok=True)
        out = os.path.join(ROOT, old, page + ".html")
        open(out, "w").write(stub(lang, page))
        print("轉址", os.path.relpath(out, ROOT), "→", url(lang, page))

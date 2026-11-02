#!/usr/bin/env python3
# 產生「去處」官網三種語言的頁面：繁中在 /whereto/，英文在 /whereto/en/，日文在 /whereto/ja/。
# 網站根目錄是個人首頁（index.html，手寫，不經此腳本）；舊網址（/privacy.html、/en/ 等）產生轉址頁，App Store 上填的連結仍然有效。
# 內容在 _src/<語言>/<頁面>.html（第一、二行註解是 title、description），共用的頁首、語言切換、頁尾在這裡。
# 用法：在網站 repo 根目錄執行 `python3 _src/build.py`
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://marlonou.github.io"
LANGS = {
    "zh": {"dir": "whereto/", "html": "zh-Hant-TW", "brand": "去處 Whereto", "nav": ["首頁", "支援", "隱私權"], "navlabel": "網站",
           "footer": ["支援", "隱私權政策"], "copy": "© 2026 去處 Whereto", "switch": "語言"},
    "en": {"dir": "whereto/en/", "html": "en", "brand": "Whereto", "nav": ["Home", "Support", "Privacy"], "navlabel": "Site",
           "footer": ["Support", "Privacy Policy"], "copy": "© 2026 Whereto", "switch": "Language"},
    "ja": {"dir": "whereto/ja/", "html": "ja", "brand": "Whereto", "nav": ["ホーム", "サポート", "プライバシー"], "navlabel": "サイト",
           "footer": ["サポート", "プライバシーポリシー"], "copy": "© 2026 Whereto", "switch": "言語"},
}
PAGES = ["index", "support", "privacy"]
NAMES = {"zh": "繁中", "en": "English", "ja": "日本語"}
HREFLANG = {"zh": "zh-Hant", "en": "en", "ja": "ja"}


def url(lang, page):
    return "/" + LANGS[lang]["dir"] + ("" if page == "index" else page + ".html")


def build(lang, page):
    L = LANGS[lang]
    src = open(os.path.join(ROOT, "_src", lang, page + ".html")).read()
    title = re.search(r"<!--title:(.*?)-->", src).group(1)
    desc = re.search(r"<!--desc:(.*?)-->", src).group(1)
    body = re.sub(r"<!--(title|desc):.*?-->\n", "", src).replace('src="icon.png"', 'src="/whereto/icon.png"')
    nav = "\n".join(
        f'      <a href="{url(lang, p)}"{" aria-current=\"page\"" if p == page else ""}>{L["nav"][i]}</a>'
        for i, p in enumerate(PAGES))
    switch = "".join(
        f'<a href="{url(l, page)}" hreflang="{HREFLANG[l]}" lang="{HREFLANG[l]}" data-lang="{l}"'
        f'{" aria-current=\"true\"" if l == lang else ""}>{NAMES[l]}</a>' for l in LANGS)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="{BASE}{url(l, page)}">' for l in LANGS)
    # 根目錄首頁：沒選過語言時，依瀏覽器語言導到英文或日文版
    redirect = ""
    if lang == "zh" and page == "index":
        redirect = """<script>
try{if(!localStorage.getItem('lang')){var l=(navigator.languages&&navigator.languages[0]||navigator.language||'').toLowerCase();
if(l.indexOf('zh')!==0){location.replace(l.indexOf('ja')===0?'/whereto/ja/':'/whereto/en/')}}}catch(e){}
</script>
"""
    remember = """<script>document.querySelectorAll('.lang a').forEach(function(a){a.addEventListener('click',function(){try{localStorage.setItem('lang',a.dataset.lang)}catch(e){}})})</script>"""
    footer_links = f'<a href="{url(lang, "support")}">{L["footer"][0]}</a>\n    <a href="{url(lang, "privacy")}">{L["footer"][1]}</a>'
    return f"""<!doctype html>
<html lang="{L["html"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="/whereto/favicon.png">
<link rel="stylesheet" href="/whereto/style.css">
{alternates}
<link rel="alternate" hreflang="x-default" href="{BASE}{url("en", page)}">
{redirect}</head>
<body>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="{url(lang, "index")}"><img src="/whereto/icon.png" alt="">{L["brand"]}</a>
    <nav aria-label="{L["navlabel"]}">
{nav}
    </nav>
    <div class="lang" role="group" aria-label="{L["switch"]}">{switch}</div>
  </div>
</header>

{body.strip()}

<footer>
  <div class="wrap">
    <span>{L["copy"]}</span>
    {footer_links}
  </div>
</footer>
{remember}
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
<title>{LANGS[lang]["brand"]}</title>
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

"""
Prepares Mythral Lens for the desktop build:
- downloads every CDN script (three.js, controls, exporter, pako, jszip, Tailwind) into build/app/vendor/
- downloads every Google Font the app can use (UI fonts + all title fonts) into build/app/vendor/fonts/
- rewrites index.html so nothing is loaded from the internet at runtime
Runs on the GitHub Actions build machine (it has internet); the resulting app works fully offline.
"""
import hashlib, os, re, shutil, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "app")
OUT = os.path.join(ROOT, "build", "app")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def main(fetch=fetch):
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    vendor = os.path.join(OUT, "vendor"); fonts_dir = os.path.join(vendor, "fonts")
    os.makedirs(fonts_dir, exist_ok=True)
    html = open(os.path.join(OUT, "index.html"), encoding="utf-8").read()

    # 1) scripts
    used = set()
    def local_script(m):
        url = m.group(1)
        name = os.path.basename(urllib.parse.urlparse(url).path) or "lib.js"
        if url.startswith("https://cdn.tailwindcss.com"): name = "tailwind.js"
        if not name.endswith(".js"): name += ".js"
        base, n = name, 1
        while name in used: n += 1; name = base.replace(".js", f"-{n}.js")
        used.add(name)
        data = fetch(url)
        if len(data) < 200: raise SystemExit(f"Download looks wrong for {url} ({len(data)} bytes)")
        open(os.path.join(vendor, name), "wb").write(data)
        print(f"  script  {name:28s} {len(data)//1024:6d} KB")
        return f'<script src="vendor/{name}"></script>'
    html = re.sub(r'<script src="(https://[^"]+)"></script>', local_script, html)

    # 2) fonts: the UI fonts from the <link> plus every title font listed in GOOGLE_FONTS
    families = []
    link = re.search(r'<link href="(https://fonts\.googleapis\.com/css2\?[^"]+)" rel="stylesheet">', html)
    if link:
        q = urllib.parse.urlparse(link.group(1).replace("&amp;", "&")).query
        families += [v for k, v in urllib.parse.parse_qsl(q) if k == "family"]
    if "const GOOGLE_FONTS" in html:
        block = html.split("const GOOGLE_FONTS", 1)[1].split("];", 1)[0]
        for fam, weight in re.findall(r'\["([^"]+)", (\d+)\]', block):
            families.append(fam + (f":wght@{weight}" if weight != "400" else ""))
    css_all = []
    for fam in dict.fromkeys(families):
        url = "https://fonts.googleapis.com/css2?family=" + urllib.parse.quote(fam, safe=":@;,.") + "&display=swap"
        css = fetch(url).decode("utf-8")
        def local_font(m):
            furl = m.group(1)
            ext = os.path.splitext(urllib.parse.urlparse(furl).path)[1] or ".woff2"
            fname = hashlib.sha1(furl.encode()).hexdigest()[:16] + ext
            path = os.path.join(fonts_dir, fname)
            if not os.path.exists(path): open(path, "wb").write(fetch(furl))
            return f"url(fonts/{fname})"
        css_all.append(re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", local_font, css))
        print(f"  font    {fam}")
    open(os.path.join(vendor, "fonts.css"), "w", encoding="utf-8").write("\n".join(css_all))
    html = re.sub(r'<link rel="preconnect"[^>]*>\n?', "", html)
    if link: html = html.replace(link.group(0), '<link href="vendor/fonts.css" rel="stylesheet">')
    # title fonts are already bundled, so the app never needs to request them online
    html = html.replace("document.head.appendChild(l);", "/* bundled offline: vendor/fonts.css */")

    left = re.findall(r'(?:src|href)="(https://(?:cdn|fonts)[^"]+)"', html)
    if left: raise SystemExit("Still loading from the internet: " + ", ".join(left))
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(html)
    print(f"Offline app ready in build/app ({len(used)} scripts, {len(os.listdir(fonts_dir))} font files).")

if __name__ == "__main__":
    main()

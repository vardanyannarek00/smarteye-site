"""Screenshot built pages locally, serving CDN assets from npm copies (preview only)."""
import sys, os, http.server, threading, functools
from playwright.sync_api import sync_playwright

SITE, NPM, OUTDIR = sys.argv[1], sys.argv[2], sys.argv[3]
pages = sys.argv[4:]
os.makedirs(OUTDIR, exist_ok=True)

h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
h.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), h)
threading.Thread(target=srv.serve_forever, daemon=True).start()

NM = os.path.join(NPM, "node_modules")
MAP = {
    "jquery-3.4.1.min.js": f"{NM}/jquery/dist/jquery.min.js",
    "bootstrap.bundle.min.js": f"{NM}/bootstrap/dist/js/bootstrap.bundle.min.js",
    "font-awesome/5.15.4/css/all.min.css": f"{NM}/@fortawesome/fontawesome-free/css/all.min.css",
    "bootstrap-icons.css": f"{NM}/bootstrap-icons/font/bootstrap-icons.css",
}


def route(r):
    u = r.request.url
    for k, p in MAP.items():
        if u.endswith(k):
            return r.fulfill(path=p)
    if "/webfonts/" in u:
        return r.fulfill(path=f"{NM}/@fortawesome/fontawesome-free/webfonts/" + u.split("/webfonts/")[1])
    if "/fonts/bootstrap-icons" in u:
        return r.fulfill(path=f"{NM}/bootstrap-icons/font/fonts/" + u.split("/fonts/")[1].split("?")[0])
    if u.startswith("http://127.0.0.1"):
        return r.continue_()
    return r.abort()


with sync_playwright() as p:
    b = p.chromium.launch()
    for w, tag in [(1366, "desk"), (390, "mob")]:
        ctx = b.new_context(viewport={"width": w, "height": 900})
        ctx.route("**/*", route)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        for name in pages:
            pg.goto(f"http://127.0.0.1:8765/{name}")
            pg.wait_for_timeout(1500)
            pg.evaluate("document.querySelectorAll('.wow').forEach(e=>{e.style.visibility='visible';e.style.animationName='none'})")
            pg.screenshot(path=f"{OUTDIR}/{tag}-{name}.png", full_page=True)
            sw = pg.evaluate("document.documentElement.scrollWidth")
            print(tag, name, "scrollWidth", sw, "errors", errs)
            errs.clear()
        ctx.close()
    b.close()
srv.shutdown()

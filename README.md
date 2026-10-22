# smarteye.am

`site/` — the live website. The hosting server pulls this repo every 15 minutes and copies `site/` into `public_html` (copy only, nothing is deleted on the server).

`tools/` — everything needed to rebuild `site/`:
- `build.py` — generates all pages (texts, sections, lists of work photos/videos live here)
- `calc.py` — the system calculator on the homepage and quote page
- `smarteye.css` — brand styles; `send.php` — form handler (email + Telegram)
- `work-photos/`, `work-videos/` — web-ready installation media (EXIF/GPS stripped)

## Rebuild

```
python3 -I tools/build.py site /tmp/new-site
rm -rf site && cp -R /tmp/new-site site
printf '<?php\nhttp_response_code(404);\n' > site/tg-test.php   # keep the old setup page disabled
```

## Adding a new installation photo

1. Convert to JPG, strip EXIF/GPS, resize to max 1400 px → `tools/work-photos/<name>.jpg`, plus an 800×800 crop → `<name>-sq.jpg`
2. Add `("<name>", "<Armenian caption>")` to `WORK_PHOTOS` in `tools/build.py` (first 4 show on the homepage)
3. Rebuild and commit

Secrets (Telegram token) live only on the server in `/home/smarteye/smarteye-config.php`, never in this repo.

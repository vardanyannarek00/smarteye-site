#!/usr/bin/env python3
"""Generate the SmartEye System site pages from one shared layout.

Usage: python3 tools/build.py site /tmp/new-site   (then replace site/ with /tmp/new-site)
Photos/videos are read from tools/work-photos and tools/work-videos.
Copies css/js/lib/img from the template (skipping non-web files) and writes all pages.
"""
import json, re
import datetime
import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calc import calculator

SRC, OUT = sys.argv[1], sys.argv[2]

PHONE = "+37443535332"
PHONE_TXT = "+374 43 535 332"
EMAIL = "info@smarteye.am"
FB = "https://www.facebook.com/1385826704616620"
IG = "https://www.instagram.com/smarteye_system/"
TT = "https://www.tiktok.com/@smarteye.am"
YEAR = "2026"

NAV = [
    ("index.html", "Գլխավոր"),
    ("about.html", "Մեր մասին"),
    ("service.html", "Ծառայություններ"),
    ("project.html", "Աշխատանքներ"),
    ("quote.html", "Անվճար խորհրդատվություն"),
    ("contact.html", "Կապ"),
]

SERVICES = [
    ("fa-video", "Տեսախցիկների տեղադրում",
     "IP և անալոգ տեսախցիկների, NVR և DVR ձայնագրիչների տեղադրում տների, խանութների, գրասենյակների և արտադրամասերի համար։ Կարգավորում ենք հեռախոսից դիտումը, որ ձեր օբյեկտը միշտ տեսնեք՝ որտեղ էլ լինեք։"),
    ("fa-bell", "Ազդանշանային և հակահրդեհային համակարգեր",
     "Ներխուժման ազդանշանային համակարգեր, շարժման և դռան սենսորներ, ծխի և հրդեհի դետեկտորներ։ Վտանգի դեպքում ազդանշանը անմիջապես հասնում է ձեզ։"),
    ("fa-network-wired", "Լոկալ ցանցերի կառուցում",
     "Գրասենյակների և կազմակերպությունների լոկալ ցանցերի (LAN) և Wi-Fi-ի նախագծում, մոնտաժ և սպասարկում՝ կայուն, արագ և անվտանգ կապի համար։"),
    ("fa-check-double", "Ցանցային մալուխի ստուգում (Fluke)",
     "Ցանցային մալուխների ստուգում Fluke սարքով։ Տալիս ենք հաշվետվություն, թե գիծը համապատասխանում է Cat5e կամ Cat6 ստանդարտին։ Պետք է նոր ցանցի հանձնման, խնդիրների որոնման և կապալառուի աշխատանքը ստուգելու համար։"),
    ("fa-balance-scale", "Խանութի կշեռքներ",
     "Խանութների և առևտրի կետերի համար կշեռքների տեղադրում, կարգավորում և միացում։"),
    ("fa-desktop", "Համակարգիչների սպասարկում",
     "Համակարգիչների արագ և որակյալ սպասարկում՝ ինչպես տանը, այնպես էլ գրասենյակում։"),
]

SERVICE_OPTIONS = [s[1] for s in SERVICES] + ["Խելացի դռան աչք (EZVIZ)", "Այլ / չգիտեմ, խորհրդատվություն է պետք"]


LD_BUSINESS = json.dumps({
    "@context": "https://schema.org", "@type": "LocalBusiness", "@id": "https://smarteye.am/#business",
    "name": "SmartEye System", "alternateName": ["SmartEye", "Սմարթ Այ"],
    "description": "Տեսախցիկների, ազդանշանային համակարգերի (ալարմ) և ցանցերի տեղադրում Երևանում և Արագածոտնի մարզում։ Установка видеонаблюдения и сигнализации в Ереване. CCTV and alarm installation in Yerevan, Armenia.",
    "url": "https://smarteye.am/", "telephone": "+37443535332", "email": "info@smarteye.am",
    "image": "https://smarteye.am/img/work/work-10-hero.jpg", "logo": "https://smarteye.am/img/favicon.png",
    "address": {"@type": "PostalAddress", "addressLocality": "Yerevan", "addressRegion": "Yerevan", "addressCountry": "AM"},
    "areaServed": [{"@type": "City", "name": "Yerevan"}, {"@type": "AdministrativeArea", "name": "Aragatsotn"}],
    "knowsAbout": ["CCTV installation", "IP cameras", "Hikvision", "Dahua", "alarm systems", "Hikvision AX PRO", "LAN networks", "Fluke cable certification"],
    "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n}} for n in
                   ["Տեսախցիկների տեղադրում", "Ազդանշանային համակարգերի տեղադրում", "Լոկալ ցանցերի և Wi-Fi-ի կառուցում", "Մալուխի ստուգում Fluke-ով", "Խանութի կշեռքների տեղադրում"]],
    "sameAs": ["https://www.instagram.com/smarteye_system/", "https://www.facebook.com/1385826704616620", "https://www.tiktok.com/@smarteye.am"],
}, ensure_ascii=False)


def faq_ld(items):
    return '\n            <script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in items]},
        ensure_ascii=False) + "</script>"


def head(title, desc, fname="index.html"):
    url = "https://smarteye.am/" + ("" if fname == "index.html" else fname)
    robots = '\n    <meta name="robots" content="noindex">' if fname == "404.html" else f'\n    <link rel="canonical" href="{url}">'
    return f"""<!DOCTYPE html>
<html lang="hy">

<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta content="տեսախցիկների տեղադրում, տեսահսկում Երևան, ազդանշանային համակարգ, ալարմ, լոկալ ցանց, LAN, Hikvision, Dahua, խանութի կշեռք, SmartEye" name="keywords">
    <meta content="{desc}" name="description">{robots}
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{url}">
    <meta property="og:locale" content="hy_AM">
    <meta property="og:site_name" content="SmartEye System">
    <meta property="og:image" content="https://smarteye.am/img/work/work-10-hero.jpg">

    <link href="img/favicon.svg" rel="icon" type="image/svg+xml">
    <link href="img/favicon.png" rel="icon" type="image/png">
    <link href="img/favicon.png" rel="apple-touch-icon">
    <script type="application/ld+json">{LD_BUSINESS}</script>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Armenian:wght@400;500;700;900&family=Open+Sans:wght@400;500&family=Roboto:wght@500;700;900&display=swap" rel="stylesheet">

    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.4.1/font/bootstrap-icons.css" rel="stylesheet">

    <link href="lib/animate/animate.min.css" rel="stylesheet">
    <link href="lib/owlcarousel/assets/owl.carousel.min.css" rel="stylesheet">
    <link href="lib/lightbox/css/lightbox.min.css" rel="stylesheet">

    <link href="css/bootstrap.min.css" rel="stylesheet">
    <link href="css/style.css" rel="stylesheet">
    <!-- SmartEye brand colors (night blue). Remove this line to return to the template's green. -->
    <link href="css/smarteye.css" rel="stylesheet">
</head>

<body>
"""


def social(btn_class):
    return f"""<a class="{btn_class}" href="{FB}" target="_blank" rel="noopener" aria-label="Facebook"><i class="fab fa-facebook-f"></i></a>
                <a class="{btn_class}" href="{IG}" target="_blank" rel="noopener" aria-label="Instagram"><i class="fab fa-instagram"></i></a>
                <a class="{btn_class}" href="{TT}" target="_blank" rel="noopener" aria-label="TikTok"><i class="fab fa-tiktok"></i></a>"""


def topbar_nav(active):
    links = "\n".join(
        f'                <a href="{h}" class="nav-item nav-link{" active" if h == active else ""}">{t}</a>'
        for h, t in NAV)
    return f"""
    <!-- Topbar Start -->
    <div class="container-fluid bg-dark px-5">
        <div class="row gx-4 d-none d-lg-flex">
            <div class="col-lg-6 text-start">
                <div class="h-100 d-inline-flex align-items-center py-3 me-4">
                    <div class="btn-sm-square rounded-circle bg-primary me-2"><small class="fa fa-map-marker-alt text-white"></small></div>
                    <small>Երևան</small>
                </div>
                <div class="h-100 d-inline-flex align-items-center py-3">
                    <div class="btn-sm-square rounded-circle bg-primary me-2"><small class="fa fa-envelope-open text-white"></small></div>
                    <small><a class="text-secondary" href="mailto:{EMAIL}">{EMAIL}</a></small>
                </div>
            </div>
            <div class="col-lg-6 text-end">
                <div class="h-100 d-inline-flex align-items-center py-3">
                    <div class="btn-sm-square rounded-circle bg-primary me-2"><small class="fa fa-phone-alt text-white"></small></div>
                    <small><a class="text-secondary" href="tel:{PHONE}">{PHONE_TXT}</a></small>
                </div>
            </div>
        </div>
    </div>
    <!-- Topbar End -->

    <!-- Navbar Start -->
    <nav class="navbar navbar-expand-lg bg-white navbar-light sticky-top p-0 px-4 px-lg-5">
        <a href="index.html" class="navbar-brand d-flex align-items-center">
            <svg class="logo-mark me-2" viewBox="0 0 48 32" width="44" height="30" aria-hidden="true">
                <path d="M2 16 C10 3, 38 3, 46 16 C38 29, 10 29, 2 16 Z" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/>
                <circle cx="24" cy="16" r="7.5" fill="currentColor"/><circle cx="26.5" cy="13.5" r="2.4" fill="#fff"/>
            </svg>
            <span class="logo-text"><span class="logo-main">SmartEye</span><span class="logo-sub">System</span></span>
        </a>
        <button type="button" class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#navbarCollapse" aria-label="Մենյու">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarCollapse">
            <div class="navbar-nav ms-auto py-4 py-lg-0">
{links}
            </div>
            <div class="h-100 d-lg-inline-flex align-items-center d-none">
                {social("btn btn-square rounded-circle bg-light text-primary me-2")}
            </div>
        </div>
    </nav>
    <!-- Navbar End -->
"""


def page_header(title):
    return f"""
    <!-- Page Header Start -->
    <div class="container-fluid page-header py-5 mb-5">
        <div class="container py-5">
            <h1 class="display-3 text-white mb-3 animated slideInDown">{title}</h1>
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a class="text-white" href="index.html">Գլխավոր</a></li>
                    <li class="breadcrumb-item text-white active" aria-current="page">{title}</li>
                </ol>
            </nav>
        </div>
    </div>
    <!-- Page Header End -->
"""


def footer(extra_js=""):
    svc_links = "\n".join(
        f'                    <a class="btn btn-link" href="service.html">{s[1]}</a>' for s in SERVICES[:4])
    return f"""
    <!-- Footer Start -->
    <div class="container-fluid bg-dark text-secondary footer mt-5 pt-5 wow fadeIn" data-wow-delay="0.1s">
        <div class="container py-5">
            <div class="row g-5">
                <div class="col-lg-4 col-md-6">
                    <div class="footer-brand mb-3">
                        <svg viewBox="0 0 48 32" width="40" height="27" aria-hidden="true"><path d="M2 16 C10 3, 38 3, 46 16 C38 29, 10 29, 2 16 Z" fill="none" stroke="#1E6BFF" stroke-width="3"/><circle cx="24" cy="16" r="7.5" fill="#1E6BFF"/><circle cx="26.5" cy="13.5" r="2.4" fill="#fff"/></svg>
                        <span>SmartEye <small>System</small></span>
                    </div>
                    <p class="footer-about">Տեսահսկում, ազդանշանային համակարգեր և ցանցեր Երևանում և Արագածոտնում։</p>
                    <h5 class="text-light mb-3 mt-4">Կապ</h5>
                    <p class="mb-2"><i class="fa fa-map-marker-alt me-3"></i>Երևան</p>
                    <p class="mb-2"><i class="fa fa-phone-alt me-3"></i><a class="text-secondary" href="tel:{PHONE}">{PHONE_TXT}</a></p>
                    <p class="mb-2"><i class="fa fa-envelope me-3"></i><a class="text-secondary" href="mailto:{EMAIL}">{EMAIL}</a></p>
                    <div class="d-flex pt-2">
                        {social("btn btn-square btn-outline-secondary rounded-circle me-2")}
                    </div>
                </div>
                <div class="col-lg-4 col-md-6">
                    <h5 class="text-light mb-4">Ծառայություններ</h5>
{svc_links}
                </div>
                <div class="col-lg-4 col-md-6">
                    <h5 class="text-light mb-4">Արագ հղումներ</h5>
                    <a class="btn btn-link" href="about.html">Մեր մասին</a>
                    <a class="btn btn-link" href="smart.html">Խելացի տեսախցիկներ</a>
                    <a class="btn btn-link" href="alarm.html">Ազդանշանային համակարգեր</a>
                    <a class="btn btn-link" href="project.html">Աշխատանքներ</a>
                    <a class="btn btn-link" href="quote.html">Անվճար խորհրդատվություն</a>
                    <a class="btn btn-link" href="contact.html">Կապ</a>
                    <a class="btn btn-link" href="smarteye-presentation.pdf" target="_blank" rel="noopener">Ներկայացում (PDF)</a>
                </div>
            </div>
        </div>
        <div class="container">
            <div class="copyright border-top border-secondary py-4">
                <div class="row">
                    <div class="col-md-6 text-center text-md-start mb-3 mb-md-0">
                        &copy; {YEAR} <a class="border-bottom" href="index.html">SmartEye System</a>։ Բոլոր իրավունքները պաշտպանված են։<br><span class="small opacity-75">Установка видеонаблюдения и сигнализации в Ереване и Арагацотне • CCTV, alarm &amp; network installation in Yerevan, Armenia</span>
                    </div>
                    <div class="col-md-6 text-center text-md-end">
                        <!-- Required by the free HTML Codex template license (CC BY 4.0). Keep this credit unless a Credit Removal License is bought. -->
                        Designed By <a class="border-bottom" href="https://htmlcodex.com" target="_blank" rel="noopener">HTML Codex</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Footer End -->

    <a href="tel:{PHONE}" class="call-float btn btn-primary rounded-pill shadow d-lg-none" aria-label="Զանգել"><i class="fa fa-phone-alt me-2"></i>Զանգել</a>
    <a href="#" class="btn btn-lg btn-primary btn-lg-square rounded-circle back-to-top" aria-label="Վերև"><i class="bi bi-arrow-up"></i></a>

    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="lib/wow/wow.min.js"></script>
    <script src="lib/easing/easing.min.js"></script>
    <script src="lib/waypoints/waypoints.min.js"></script>
    <script src="lib/counterup/counterup.min.js"></script>
    <script src="lib/owlcarousel/owl.carousel.min.js"></script>
    <script src="lib/isotope/isotope.pkgd.min.js"></script>
    <script src="lib/lightbox/js/lightbox.min.js"></script>
    <script src="js/main.js"></script>{extra_js}
</body>

</html>
"""


def page(fname, active, title, desc, body, extra_js=""):
    html = head(title, desc, fname) + topbar_nav(active) + body + footer(extra_js)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)


# ---------- reusable sections ----------

MORE_LINKS = {"Տեսախցիկների տեղադրում": ("smart.html", "Խելացի տեսախցիկներ"),
              "Ազդանշանային և հակահրդեհային համակարգեր": ("alarm.html", "Մանրամասն")}


def more_link(name):
    if name not in MORE_LINKS:
        return ""
    href, label = MORE_LINKS[name]
    return f'\n                        <a class="more-link" href="{href}">{label} <i class="fa fa-arrow-right ms-1"></i></a>'


def services_grid(with_cta=False):
    delays = ["0.1s", "0.3s", "0.5s"]
    cards = []
    for i, (icon, name, text) in enumerate(SERVICES):
        cards.append(f"""
                <div class="col-md-6 col-lg-4 wow fadeIn" data-wow-delay="{delays[i % 3]}">
                    <div class="service-item border h-100 p-5">
                        <i class="fa {icon} step-icon"></i>
                        <h4 class="mb-3">{name}</h4>
                        <p class="mb-0">{text}</p>{more_link(name)}
                    </div>
                </div>""")
    if with_cta:
        cards.append(f"""
                <div class="col-md-6 col-lg-4 wow fadeIn" data-wow-delay="0.5s">
                    <div class="service-item service-cta border h-100 p-5 bg-primary">
                        <i class="fa fa-comments step-icon step-icon-light"></i>
                        <h4 class="mb-3 text-white">Անվճար խորհրդատվություն</h4>
                        <p class="mb-4 text-white">Կգանք, կզննենք օբյեկտը և կառաջարկենք ձեզ հարմար լուծում՝ անվճար։</p>
                        <a class="btn btn-light me-2 mb-2" href="tel:{PHONE}"><i class="fa fa-phone-alt me-2"></i>Զանգել</a>
                        <a class="btn btn-outline-light mb-2" href="quote.html#calc">Թողնել հայտ</a>
                    </div>
                </div>""")
    return f"""
    <!-- Service Start -->
    <div class="container-xxl py-5">
        <div class="container">
            <div class="text-center">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-3">Մեր ծառայությունները</h2>
                <p class="mb-5">Նախագծում, տեղադրում և սպասարկում ենք Hikvision և Dahua համակարգեր։ Սարքավորումը՝ Հայաստանի պաշտոնական ներմուծողներից, պաշտոնական երաշխիքով։</p>
            </div>
            <div class="row g-0 service-row">{"".join(cards)}
            </div>
        </div>
    </div>
    <!-- Service End -->
"""


def why_us():
    items = [
        ("fa-shield-alt", "Պաշտոնական երաշխիք", "Hikvision և Dahua սարքավորում պաշտոնական ներմուծողներից"),
        ("fa-handshake", "Անվճար խորհրդատվություն", "Օբյեկտի զննում և առաջարկ՝ առանց վճարի"),
        ("fa-mobile-alt", "Դիտում հեռախոսից", "Կարգավորում ենք, որ ամեն տեղից տեսնեք"),
        ("fa-headset", "Սպասարկում", "Տեղադրումից հետո էլ կապի մեջ ենք"),
    ]
    cols = "".join(f"""
                        <div class="col-sm-6">
                            <div class="d-flex align-items-center">
                                <i class="fa {ic} step-icon mb-0 flex-shrink-0"></i>
                                <div class="ms-4">
                                    <h5 class="mb-1">{t}</h5>
                                    <p class="mb-0 small">{d}</p>
                                </div>
                            </div>
                        </div>""" for ic, t, d in items)
    return f"""
    <!-- Feature Start -->
    <div class="container-fluid bg-light overflow-hidden my-5 px-lg-0">
        <div class="container feature px-lg-0">
            <div class="row g-0 mx-lg-0">
                <div class="col-lg-6 feature-text py-5 wow fadeIn" data-wow-delay="0.3s">
                    <div class="p-lg-5 ps-lg-0">
                        <div class="bg-primary mb-3" style="width: 60px; height: 2px;"></div>
                        <h2 class="display-5 mb-4">Ինչու ընտրել մեզ</h2>
                        <p class="mb-4 pb-2">Ընտրում ենք սարքավորումը ձեր օբյեկտին և բյուջեին համապատասխան, տեղադրում ենք կոկիկ և բացատրում ենք, թե ինչպես օգտվել համակարգից։</p>
                        <div class="row g-4">{cols}
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 pe-lg-0" style="min-height: 400px;">
                    <div class="position-relative h-100">
                        <img class="position-absolute img-fluid w-100 h-100" src="img/work/work-2.jpg" style="object-fit: cover;" alt="SmartEye-ի տեղադրած պտտվող տեսախցիկ">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Feature End -->
"""


WORK_PHOTOS = [  # real SmartEye installations (EXIF/GPS stripped); first 4 appear on the homepage
    ("work-8", "Գմբեթավոր տեսախցիկներ քարե տան վրա"),
    ("net-1", "Ցանցային ռեք՝ կոկիկ մալուխավորում"),
    ("work-12", "Տեսախցիկներ նոր շենքի պատին"),
    ("fluke-1", "Ցանցի ստուգում Fluke-ով"),
    ("work-10", "Hikvision տեսախցիկ՝ ամուր ամրացում"),
    ("work-9", "Երկու տեսախցիկ՝ երկու ուղղությամբ"),
    ("work-15", "Գմբեթավոր տեսախցիկ խանութի առաստաղին"),
    ("work-14", "Խանութի ամբողջական տեսահսկում"),
    ("work-16", "Ներքին տեսախցիկ՝ սպասարկման գոտում"),
    ("net-2", "Սերվերային պահարան և ցանցային մալուխներ"),
    ("work-11", "Պտտվող PTZ տեսախցիկ պատին"),
    ("fluke-2", "Fluke DSP. մալուխի թեստը՝ PASS"),
    ("work-13", "Շենքի անկյունների հսկողություն"),
    ("work-1", "Hikvision տեսախցիկ այգու մուտքի մոտ"),
    ("work-2", "Պտտվող տեսախցիկ տան անկյունում"),
    ("work-3", "Երկու տեսախցիկ՝ այգու երկու ուղղությամբ"),
    ("work-4", "Տեսախցիկ տան ճակատին"),
    ("work-5", "Այսպես է երևում տեսախցիկից"),
    ("work-6", "Hikvision տեսախցիկ՝ այգու հսկողություն"),
    ("work-7", "Տեսահսկվող օբյեկտ"),
    ("alarm-1", "Hikvision AX Hybrid PRO ալարմ և AcuSense NVR"),
    ("alarm-2", "Լարային շարժման սենսորի միացում"),
    ("alarm-3", "Ծխի սենսորի տեղադրում"),
]


def work_gallery(limit=None):
    items = WORK_PHOTOS[:limit] if limit else WORK_PHOTOS
    col = "col-6 col-lg-3" if limit == 4 else "col-6 col-lg-4"
    return "".join(f"""
                <div class="{col}">
                    <a class="work-tile d-block position-relative overflow-hidden" href="img/work/{n}.jpg" data-lightbox="work" data-title="{t}">
                        <img class="img-fluid w-100" src="img/work/{n}-sq.jpg" alt="{t}" loading="lazy">
                        <span class="work-cap">{t}</span>
                    </a>
                </div>""" for n, t in items)


WORK_VIDEOS = [  # self-hosted short clips (compressed, metadata stripped) in img/video/
    ("video-1", "Տեսախցիկների տեղադրում շենքի վրա"),
    ("video-2", "Dahua գմբեթավոր տեսախցիկ և դիտում էկրանին"),
    ("video-3", "Hikvision սարքավորումներ"),
]


def work_videos():
    return "".join(f"""
                <div class="col-md-4 col-sm-6">
                    <div class="work-video">
                        <video src="img/video/{n}.mp4" poster="img/video/{n}.jpg" controls muted playsinline preload="none"></video>
                        <p class="small text-center mt-2 mb-0">{t}</p>
                    </div>
                </div>""" for n, t in WORK_VIDEOS)


TIKTOK_VIDEOS = [  # most-viewed SmartEye TikToks; swap IDs here to feature newer ones
    "7665792168635682068",
    "7665790815272307989",
    "7677865339698302228",
]
FB_PLUGIN = ("https://www.facebook.com/plugins/page.php?href=" + FB.replace(":", "%3A").replace("/", "%2F")
             + "&tabs=timeline&width=340&height=520&small_header=true&adapt_container_width=true&hide_cover=false&show_facepile=false")


def our_work_cta(with_facebook=False):
    # Heavy TikTok/Facebook embeds only on the Աշխատանքներ page (with_facebook=True); the homepage stays fast.
    with_tiktok = with_facebook
    cards = [
        ("fab fa-instagram", "Instagram", "@smarteye_system", IG),
        ("fab fa-facebook-f", "Facebook", "SmartEye System", FB),
        ("fab fa-tiktok", "TikTok", "@smarteye.am", TT),
    ]
    card_html = "".join(f"""
                <div class="col-md-4 wow fadeInUp" data-wow-delay="{0.1 + 0.2 * i:.1f}s">
                    <a class="social-card d-flex align-items-center bg-white p-4 h-100" href="{url}" target="_blank" rel="noopener">
                        <span class="social-icon rounded-circle bg-primary text-white flex-shrink-0"><i class="{icon}"></i></span>
                        <span class="ms-3 text-start">
                            <span class="d-block h5 mb-0 text-dark">{name}</span>
                            <span class="d-block small text-muted">{handle}</span>
                        </span>
                        <span class="ms-auto btn btn-primary btn-sm rounded-pill px-3">Հետևել</span>
                    </a>
                </div>""" for i, (icon, name, handle, url) in enumerate(cards))
    vids = "".join(f"""
                <div class="col-lg-4 col-md-6 d-flex justify-content-center">
                    <blockquote class="tiktok-embed" cite="{TT}/video/{v}" data-video-id="{v}" style="max-width: 325px; min-width: 300px; margin: 0;">
                        <section><a href="{TT}/video/{v}" target="_blank" rel="noopener">Դիտել TikTok-ում</a></section>
                    </blockquote>
                </div>""" for v in TIKTOK_VIDEOS)
    fb = f"""
            <div class="row justify-content-center mt-5">
                <div class="col-lg-6 text-center">
                    <h3 class="mb-4">Facebook էջը</h3>
                    <iframe class="fb-page-embed" src="{FB_PLUGIN}" width="340" height="520" style="border:none; overflow:hidden; max-width:100%;"
                        scrolling="no" frameborder="0" allowfullscreen="true" loading="lazy" title="SmartEye System Facebook"
                        allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>
                </div>
            </div>""" if with_facebook else ""
    videos_block = f"""
            <h3 class="text-center mb-4">Տեսանյութեր</h3>
            <div class="row g-4 justify-content-center mb-5">{work_videos()}
            </div>""" if with_facebook else f"""
            <div class="text-center">
                <a class="btn btn-outline-primary rounded-pill px-4" href="project.html">Բոլոր աշխատանքները <i class="fa fa-arrow-right ms-2"></i></a>
            </div>"""
    tiktok_block = f"""
            <h3 class="text-center mb-4">TikTok-ում</h3>
            <div class="row g-4 justify-content-center">{vids}
            </div>""" if with_tiktok else ""
    tiktok_js = '<script async src="https://www.tiktok.com/embed.js"></script>' if with_tiktok else ""
    return f"""
    <!-- Social Start -->
    <div class="container-xxl py-5">
        <div class="container">
            <div class="text-center wow fadeInUp" data-wow-delay="0.1s">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-3">Մեր աշխատանքները</h2>
                <p class="mb-5 mx-auto" style="max-width: 640px;">Կատարած տեղադրումների տեսանյութերն ու լուսանկարները պարբերաբար հրապարակում ենք սոցցանցերում։ Հետևեք մեզ։</p>
            </div>
            <div class="row g-3 mb-5">{work_gallery(4 if not with_facebook else None)}
            </div>
            <div class="row g-4 mb-5">{card_html}
            </div>
{videos_block}
{tiktok_block}
            <div class="text-center mt-4"{'' if with_facebook else ' hidden'}>
                <a class="btn btn-primary rounded-pill py-3 px-5" href="{TT}" target="_blank" rel="noopener"><i class="fab fa-tiktok me-2"></i>Բոլոր տեսանյութերը</a>
            </div>{fb}
        </div>
    </div>
    {tiktok_js}
    <!-- Social End -->
"""


def smart_ai():
    feats = [
        ("fa-user", "Մարդու և մեքենայի ճանաչում", "Տեսախցիկը տարբերում է մարդուն և մեքենան ծառերից, կենդանիներից, ստվերներից ու անձրևից։"),
        ("fa-bell-slash", "Ավելի քիչ կեղծ ահազանգ", "Ծանուցումը գալիս է հեռախոսին միայն այն ժամանակ, երբ իսկապես մարդ կամ մեքենա կա։"),
        ("fa-draw-polygon", "Գոտիներ և սահմանագծեր", "Նշում ենք դարպասը, պատը կամ մուտքը, և տեսախցիկը ահազանգում է, երբ մեկը հատում է այդ գիծը։"),
        ("fa-search", "Արագ որոնում", "Ձայնագրության մեջ կարելի է գտնել միայն մարդկանց կամ մեքենաների հայտնվելու պահերը՝ առանց ժամերով դիտելու։"),
        ("fa-lightbulb", "Ակտիվ վախեցում", "Որոշ մոդելներ վառում են լույս և ձայնային ազդանշան տալիս, երբ անծանոթը մոտենում է։"),
        ("fa-mobile-alt", "Ամեն ինչ հեռախոսում", "Ահազանգը, նկարն ու տեսանյութը անմիջապես հեռախոսում են՝ Hik-Connect կամ DMSS հավելվածով։"),
    ]
    cards = "".join(f"""
                <div class="col-md-6 col-lg-4">
                    <div class="ai-feat h-100">
                        <i class="fa {ic}"></i>
                        <h5>{t}</h5>
                        <p class="mb-0">{d}</p>
                    </div>
                </div>""" for ic, t, d in feats)
    return f"""
    <!-- Smart AI Start -->
    <section class="ai-section" id="ai">
        <div class="container">
            <div class="row align-items-end g-4 mb-5">
                <div class="col-lg-7">
                    <span class="hero-kicker"><i class="fa fa-microchip me-2"></i>Արհեստական բանականություն</span>
                    <h2 class="display-5 text-white mb-0">Խելացի տեսախցիկներ, որոնք հասկանում են, թե ինչ են տեսնում</h2>
                </div>
                <div class="col-lg-5">
                    <p class="mb-0">Hikvision AcuSense և Dahua WizSense տեխնոլոգիաները տեսախցիկը դարձնում են պահակ, ոչ թե պարզապես ձայնագրող սարք։</p>
                </div>
            </div>
            <div class="row g-4">{cards}
            </div>
            <div class="text-center mt-5">
                <a href="quote.html#calc" class="btn btn-primary btn-lg rounded-pill px-4"><i class="fa fa-calculator me-2"></i>Հաշվիր քո խելացի համակարգը</a>
            </div>
        </div>
    </section>
    <!-- Smart AI End -->
"""


def smart_teaser():
    return """
    <!-- Smart teaser Start -->
    <div class="container-xxl py-4">
        <div class="container">
            <a class="smart-teaser" href="smart.html">
                <span class="smart-teaser-icon"><i class="fa fa-microchip"></i></span>
                <span class="flex-grow-1">
                    <span class="d-block h4 text-white mb-1">Խելացի (AI) տեսախցիկներ</span>
                    <span class="d-block">Ճանաչում են մարդուն և մեքենային, ահազանգում են միայն իրական վտանգի դեպքում։</span>
                </span>
                <span class="btn btn-primary rounded-pill px-4">Իմանալ ավելին <i class="fa fa-arrow-right ms-2"></i></span>
            </a>
        </div>
    </div>
    <!-- Smart teaser End -->
"""


def door_viewer():
    feats = [("fa-door-closed", "Տեղադրվում է դռան եղած դիտանցքի անցքում"),
             ("fa-tv", "Ներսում՝ մեծ էկրան, կռանալ ու անցքից նայել պետք չէ"),
             ("fa-bell", "Զանգի կոճակ և ծանուցում հեռախոսին"),
             ("fa-user-friends", "Հարմար է տարեցների և երեխաների համար")]
    feats_html = "".join(f'''
                            <li class="mb-2"><i class="fa {i} text-primary me-2"></i>{t}</li>''' for i, t in feats)
    return f"""
    <!-- Door viewer Start -->
    <div class="container-xxl py-4">
        <div class="container">
            <div class="door-card">
                <div class="row g-4 align-items-center">
                    <div class="col-md-5 text-center">
                        <img class="img-fluid door-img" src="img/ezviz-door-viewer.jpg" alt="EZVIZ խելացի դռան աչք՝ ներսի էկրանով" loading="lazy" width="540" height="540">
                    </div>
                    <div class="col-md-7">
                        <span class="badge bg-primary mb-2">Բնակարանների համար</span>
                        <h3 class="mb-3">Խելացի դռան աչք EZVIZ</h3>
                        <p>Տեսեք, թե ով է դռան մոտ, առանց դուռը բացելու։ Սովորական դիտանցքի փոխարեն դրսում տեղադրում ենք տեսախցիկ զանգի կոճակով, իսկ ներսում՝ էկրան։</p>
                        <ul class="list-unstyled mb-4">{feats_html}
                        </ul>
                        <a class="btn btn-primary rounded-pill px-4 me-2 mb-2" href="tel:{PHONE}"><i class="fa fa-phone-alt me-2"></i>Զանգել</a>
                        <a class="btn btn-outline-primary rounded-pill px-4 mb-2" href="quote.html">Անվճար խորհրդատվություն</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Door viewer End -->
"""


def smart_page_body():
    flow = [("fa-video", "Տեսախցիկը տեսնում է շարժում"), ("fa-microchip", "AI-ն որոշում է՝ մարդ է, մեքենա, թե պարզապես ծառ"),
            ("fa-filter", "Կենդանիները, ստվերներն ու անձրևը անտեսվում են"), ("fa-mobile-alt", "Ահազանգը նկարով գալիս է ձեր հեռախոսին")]
    flow_html = "".join(f"""
                <div class="col-6 col-lg-3">
                    <div class="step h-100">
                        <span class="step-num">{i + 1}</span>
                        <i class="fa {ic} step-icon"></i>
                        <p class="mb-0">{t}</p>
                    </div>
                </div>""" for i, (ic, t) in enumerate(flow))
    uses = [
        ("fa-home", "Տուն", "Գիշերը մարդ մոտեցավ դարպասին. ստանում եք ահազանգ նկարով, իսկ բակում վազող կատվի համար՝ ոչ։"),
        ("fa-store", "Խանութ", "Փակվելուց հետո ներս մտնողը անմիջապես հայտնաբերվում է։ Աշխատանքային ժամերին կարելի է ահազանգերը անջատել։"),
        ("fa-warehouse", "Պահեստ / արտադրություն", "Ցանկապատի երկայնքով գիծ ենք նշում. մեքենան կամ մարդը, որ հատում է այն, անմիջապես գրանցվում է։"),
        ("fa-tree", "Այգի / ամառանոց", "Երբ տանը չեք, տեսախցիկը հսկում է տարածքը, իսկ ծառերի ու քամու պատճառով կեղծ ահազանգ չի լինում։"),
    ]
    uses_html = "".join(f"""
                <div class="col-md-6">
                    <div class="use-card h-100">
                        <i class="fa {ic}"></i>
                        <div>
                            <h5>{t}</h5>
                            <p class="mb-0">{d}</p>
                        </div>
                    </div>
                </div>""" for ic, t, d in uses)
    cmp_rows = [
        ("Ինչի վրա է ահազանգում", "Ցանկացած շարժում՝ ծառ, կենդանի, լույս, անձրև", "Միայն մարդ կամ մեքենա"),
        ("Կեղծ ահազանգեր", "Շատ, մարդիկ հաճախ անջատում են ծանուցումները", "Զգալիորեն քիչ"),
        ("Ձայնագրության մեջ որոնում", "Պետք է դիտել ժամերով", "Զտում եք՝ «միայն մարդիկ» կամ «միայն մեքենաներ»"),
        ("Գոտիներ և գծեր", "Սահմանափակ", "Մուտք գոտի, գծի հատում, ներխուժում"),
        ("Գին", "Ավելի մատչելի", "Մի փոքր ավելի թանկ"),
    ]
    cmp_html = "".join(f"<tr><th>{a}</th><td><span class=\"cell-h\">Սովորական՝ </span>{b}</td><td><span class=\"cell-h\">Խելացի՝ </span>{c}</td></tr>" for a, b, c in cmp_rows)
    faq = [
        ("Գիշերը աշխատու՞մ է։", "Այո։ Գիշերային տեսողությամբ և ColorVu տեսախցիկներով ճանաչումը աշխատում է նաև մթության մեջ։"),
        ("Ինտերնետ պե՞տք է։", "Ճանաչումն աշխատում է տեսախցիկի կամ ձայնագրիչի մեջ, ինտերնետ պետք չէ։ Ինտերնետը պետք է միայն ահազանգը հեռախոսին ստանալու և հեռվից դիտելու համար։"),
        ("Կարելի՞ է առկա համակարգը դարձնել խելացի։", "Կախված է առկա ձայնագրիչից և տեսախցիկներից։ Հաճախ բավական է փոխել մի մասը։ Կնայենք զննման ժամանակ՝ անվճար։"),
        ("Կա՞ն անալոգ խելացի տեսախցիկներ։", "Այո, Hikvision-ը և Dahua-ն ունեն նաև անալոգ (HD) մոդելներ մարդու և մեքենայի ճանաչմամբ, բայց IP տարբերակներում ֆունկցիաներն ավելի շատ են։"),
    ]
    faq_html = "".join(f"""
                <div class="accordion-item">
                    <h3 class="accordion-header" id="sh{i}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#sc{i}" aria-expanded="false" aria-controls="sc{i}">{q}</button>
                    </h3>
                    <div id="sc{i}" class="accordion-collapse collapse" aria-labelledby="sh{i}" data-bs-parent="#faq">
                        <div class="accordion-body">{a}</div>
                    </div>
                </div>""" for i, (q, a) in enumerate(faq))
    faq_html += faq_ld(faq)
    return f"""
    <div class="container-xxl py-5">
        <div class="container">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-3">Ինչպես է աշխատում</h2>
                <p class="mx-auto mb-0" style="max-width: 640px;">Hikvision AcuSense և Dahua WizSense տեխնոլոգիաներով տեսախցիկը ոչ միայն ձայնագրում է, այլև հասկանում է, թե ինչ է տեսնում։</p>
            </div>
            <div class="row g-4">{flow_html}
            </div>
        </div>
    </div>
{smart_ai()}
    <div class="container-xxl py-5">
        <div class="container">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-0">Որտեղ է օգտակար</h2>
            </div>
            <div class="row g-4">{uses_html}
            </div>
        </div>
    </div>

    <div class="container-xxl py-5">
        <div class="container">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-0">Սովորական թե խելացի</h2>
            </div>
            <div class="table-responsive sys-table-wrap">
                <table class="table sys-table mb-0">
                    <thead><tr><th></th><th>Սովորական</th><th>Խելացի (AI)</th></tr></thead>
                    <tbody>{cmp_html}</tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="container-xxl py-5">
        <div class="container" style="max-width: 860px;">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-0">Հարցեր</h2>
            </div>
            <div class="accordion" id="faq">{faq_html}
            </div>
        </div>
    </div>
{calc_cta()}
"""


def alarm_page_body():
    flow = [("fa-door-open", "Դուռը բացվում է կամ սենսորը շարժում է տեսնում"), ("fa-satellite-dish", "Սենսորը ազդանշանն ուղարկում է կառավարման վահանակին"),
            ("fa-volume-up", "Սիրենան միանում է"), ("fa-mobile-alt", "Ահազանգը նկարով կամ տեսանյութով գալիս է ձեր հեռախոսին")]
    flow_html = "".join(f"""
                <div class="col-6 col-lg-3">
                    <div class="step h-100">
                        <span class="step-num">{i + 1}</span>
                        <i class="fa {ic} step-icon"></i>
                        <p class="mb-0">{t}</p>
                    </div>
                </div>""" for i, (ic, t) in enumerate(flow))
    devices = [
        ("fa-walking", "Շարժման սենսոր", "Տեսնում է մարդուն սենյակում։ Կան մոդելներ, որոնք անտեսում են կենդանիներին։"),
        ("fa-door-closed", "Դռան և պատուհանի սենսոր", "Ահազանգում է դուռը կամ պատուհանը բացելիս։"),
        ("fa-camera", "Սենսոր տեսախցիկով", "Շարժման դեպքում նկարում է, և ահազանգը գալիս է նկարով։"),
        ("fa-glass-martini-alt", "Ապակու կոտրման սենսոր", "Լսում է ապակու կոտրվելու ձայնը։"),
        ("fa-fire", "Ծխի և հրդեհի սենսոր", "Վաղ նախազգուշացում հրդեհի մասին։"),
        ("fa-tint", "Ջրի արտահոսքի սենսոր", "Խողովակի վթարի դեպքում անմիջապես տեղեկացնում է։"),
        ("fa-volume-up", "Սիրենա", "Ներսի և դրսի, ձայնով և լույսով։"),
        ("fa-key", "Վահանակ և հեռակառավարման բանալի", "Միացնել/անջատել առանց հեռախոսի։"),
    ]
    dev_html = "".join(f"""
                <div class="col-6 col-lg-3">
                    <div class="dev-card h-100">
                        <i class="fa {ic}"></i>
                        <h6>{t}</h6>
                        <p class="mb-0">{d}</p>
                    </div>
                </div>""" for ic, t, d in devices)
    rows = [
        ("Լարեր", "Չկան. սենսորները աշխատում են մարտկոցով", "Սենսորները միանում են մալուխով"),
        ("Տեղադրում", "Արագ, առանց պատերը փորելու և վերանորոգումը փչացնելու", "Ավելի երկար, լավ է անել վերանորոգման ժամանակ"),
        ("Սպասարկում", "Ժամանակ առ ժամանակ փոխել սենսորների մարտկոցները", "Մարտկոց փոխել պետք չէ"),
        ("Հարմար է", "Բնակարան, պատրաստի վերանորոգված տուն, գրասենյակ, վարձով տարածք", "Նոր շինություն, մեծ տարածք, պահեստ, արտադրություն"),
        ("Համադրում", "Կարելի է ավելացնել նաև լարային սենսորներ (Hybrid)", "Կարելի է ավելացնել նաև անլար սենսորներ"),
    ]
    trs = "".join(f"<tr><th>{a}</th><td><span class=\"cell-h\">Անլար՝ </span>{b}</td><td><span class=\"cell-h\">Լարային՝ </span>{c}</td></tr>" for a, b, c in rows)
    faq = [
        ("Եթե հոսանքն անջատվի, ալարմը կաշխատի՞։", "Այո։ Կառավարման վահանակն ունի պահուստային մարտկոց և շարունակում է աշխատել հոսանքի անջատման ժամանակ։"),
        ("Եթե ինտերնետը չլինի՞։", "Ալարմը և սիրենան աշխատում են առանց ինտերնետի։ Հեռախոսին ահազանգ ստանալու համար վահանակը կարող է կապ պահել Wi-Fi-ով, LAN-ով կամ SIM քարտով (4G), նաև մի քանի ճանապարհով միաժամանակ։"),
        ("Անլար ալարմը հուսալի՞ է։", "Hikvision AX PRO-ն օգտագործում է Tri-X անլար տեխնոլոգիա՝ կոդավորված կապով և խցանման դեմ պաշտպանությամբ։ Վահանակը նաև հետևում է, որ յուրաքանչյուր սենսոր կապի մեջ լինի։"),
        ("Տանը կենդանի ունեմ, անընդհատ կահազանգի՞։", "Կան շարժման սենսորներ, որոնք անտեսում են փոքր կենդանիներին։ Զննման ժամանակ կընտրենք ճիշտ մոդելը և տեղը։"),
        ("Կարելի՞ է միացնել տեսախցիկների հետ։", "Այո։ Ալարմը և Hikvision տեսախցիկները կառավարվում են նույն Hik-Connect հավելվածով, և ահազանգի պահին կարող եք անմիջապես տեսնել տեսախցիկը։"),
    ]
    faq_html = "".join(f"""
                <div class="accordion-item">
                    <h3 class="accordion-header" id="ah{i}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#ac{i}" aria-expanded="false" aria-controls="ac{i}">{q}</button>
                    </h3>
                    <div id="ac{i}" class="accordion-collapse collapse" aria-labelledby="ah{i}" data-bs-parent="#faq">
                        <div class="accordion-body">{a}</div>
                    </div>
                </div>""" for i, (q, a) in enumerate(faq))
    faq_html += faq_ld(faq)

    def head(t, sub=""):
        return f"""
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-{'3' if sub else '0'}">{t}</h2>
                {f'<p class="mx-auto mb-0" style="max-width: 660px;">{sub}</p>' if sub else ''}
            </div>"""

    return f"""
    <div class="container-xxl py-5">
        <div class="container">{head("Ինչպես է աշխատում", "Hikvision-ի ազդանշանային համակարգը պաշտպանում է տունը կամ բիզնեսը ներխուժումից, հրդեհից և ջրի արտահոսքից, իսկ ահազանգը գալիս է անմիջապես ձեր հեռախոսին։")}
            <div class="row g-4">{flow_html}
            </div>
        </div>
    </div>

    <div class="container-xxl py-5">
        <div class="container">{head("Երկու տարբերակ", "Ընտրում ենք ձեր տարածքին համապատասխանը. անլար, լարային կամ երկուսի համադրություն։ Սարքավորումը՝ պաշտոնական ներմուծողներից, իսկ տեղադրումն ու կարգավորումը՝ մենք։")}
            <div class="row g-4 mb-4">
                <div class="col-md-6">
                    <div class="sys-card h-100">
                        <span class="sys-tag">Առանց լարերի</span>
                        <i class="fa fa-wifi step-icon"></i>
                        <h4>Անլար՝ Hikvision AX PRO</h4>
                        <p>Սենսորները աշխատում են մարտկոցով և կապվում են վահանակի հետ ռադիոալիքով։ Պատերը փորել պետք չէ, տեղադրումը արագ է և մաքուր։</p>
                        <p class="sys-fit mb-0"><b>Հարմար է՝</b> բնակարան, վերանորոգված տուն, գրասենյակ, խանութ, վարձով տարածք։</p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="sys-card h-100">
                        <span class="sys-tag sys-tag-muted">Լարային + անլար</span>
                        <i class="fa fa-network-wired step-icon"></i>
                        <h4>Լարային՝ Hikvision AX Hybrid PRO</h4>
                        <p>Սենսորները միանում են մալուխով, մարտկոց փոխել պետք չէ։ Անհրաժեշտության դեպքում կարելի է ավելացնել նաև անլար սենսորներ։</p>
                        <p class="sys-fit mb-0"><b>Հարմար է՝</b> նոր կառուցվող տուն, մեծ տարածք, պահեստ, արտադրություն։</p>
                    </div>
                </div>
            </div>
            <div class="table-responsive sys-table-wrap">
                <table class="table sys-table mb-0">
                    <thead><tr><th></th><th>Անլար (AX PRO)</th><th>Լարային (AX Hybrid PRO)</th></tr></thead>
                    <tbody>{trs}</tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="container-xxl py-5">
        <div class="container">{head("Մեր տեղադրումներից", "Hikvision AX Hybrid PRO ալարմ՝ լարային սենսորներով, AcuSense NVR-ով և տեսախցիկներով, մեկ օբյեկտում։")}
            <div class="row g-3">{''.join(f"""
                <div class="col-md-4">
                    <a class="work-tile d-block position-relative overflow-hidden" href="img/work/{n}.jpg" data-lightbox="alarm" data-title="{t}">
                        <img class="img-fluid w-100" src="img/work/{n}-sq.jpg" alt="{t}" loading="lazy">
                        <span class="work-cap">{t}</span>
                    </a>
                </div>""" for n, t in [w for w in WORK_PHOTOS if w[0].startswith("alarm")])}
            </div>
        </div>
    </div>

    <div class="container-xxl py-5">
        <div class="container">{head("Ինչից է բաղկացած", "Համակարգը հավաքում ենք ըստ ձեր տարածքի. միայն այն, ինչ իսկապես պետք է։")}
            <div class="row g-3">{dev_html}
            </div>
        </div>
    </div>

    <section class="ai-section">
        <div class="container">
            <div class="row g-4 g-lg-5 align-items-center">
                <div class="col-lg-6">
                    <span class="hero-kicker"><i class="fa fa-mobile-alt me-2"></i>Hik-Connect հավելված</span>
                    <h2 class="display-5 text-white mb-3">Ալարմ և տեսախցիկներ՝ մեկ հավելվածում</h2>
                    <p class="mb-0">Միացրեք կամ անջատեք ալարմը հեռախոսից, տեսեք որ սենսորն է աշխատել, և ահազանգի պահին անմիջապես նայեք տեսախցիկին։ Ահազանգի հետ կարող է գալ նաև նկար կամ կարճ տեսանյութ, որ տեսնեք՝ իսկապես վտանգ կա՞, թե ոչ։</p>
                </div>
                <div class="col-lg-6">
                    <div class="row g-3">
                        <div class="col-6"><div class="ai-feat h-100"><i class="fa fa-lock"></i><h5>Միացնել/անջատել</h5><p class="mb-0">Հեռախոսից, վահանակից կամ բանալիով</p></div></div>
                        <div class="col-6"><div class="ai-feat h-100"><i class="fa fa-image"></i><h5>Ահազանգ նկարով</h5><p class="mb-0">Տեսնում եք, թե ինչ է կատարվում</p></div></div>
                        <div class="col-6"><div class="ai-feat h-100"><i class="fa fa-battery-half"></i><h5>Պահուստային սնուցում</h5><p class="mb-0">Աշխատում է հոսանքի անջատման ժամանակ</p></div></div>
                        <div class="col-6"><div class="ai-feat h-100"><i class="fa fa-sim-card"></i><h5>Wi-Fi, LAN, 4G</h5><p class="mb-0">Կապը չի կտրվում, եթե մեկը չաշխատի</p></div></div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <div class="container-xxl py-5">
        <div class="container" style="max-width: 860px;">{head("Հարցեր")}
            <div class="accordion" id="faq">{faq_html}
            </div>
        </div>
    </div>
{calc_cta()}
"""


def ip_vs_analog():
    rows = [
        ("Ինչպես է միանում", "Ցանցային (UTP) մալուխով. մեկ մալուխով և՛ հոսանք, և՛ պատկեր (PoE)", "Կոաքսիալ մալուխով + առանձին սնուցում"),
        ("Պատկերի որակ", "2, 4, 5 ՄՊ, ColorVu-ով կամ առանց. պարզ են դեմքերն ու մեքենայի համարները", "2, 4, 5 ՄՊ, ColorVu-ով կամ առանց"),
        ("Խելացի ֆունկցիաներ", "Մարդու և մեքենայի ճանաչում, ձայն, ավելի քիչ կեղծ ահազանգ", "Հիմնական շարժման ճանաչում"),
        ("Ձայնագրիչ", "NVR", "DVR"),
        ("Ընդլայնում", "Հեշտ է ավելացնել տեսախցիկներ, կարելի է օգտագործել առկա ցանցը", "Ավելացնելը սահմանափակ է ձայնագրիչի մուտքերով"),
        ("Գին", "Ավելի թանկ", "Ավելի մատչելի"),
    ]
    trs = "".join(f"<tr><th>{a}</th><td><span class=\"cell-h\">IP՝ </span>{b}</td><td><span class=\"cell-h\">Անալոգ՝ </span>{c}</td></tr>" for a, b, c in rows)
    return f"""
    <!-- IP vs Analog Start -->
    <div class="container-xxl py-5" id="ipvsanalog">
        <div class="container">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-3">IP թե անալոգ</h2>
                <p class="mx-auto mb-0" style="max-width: 640px;">Տեսահսկման երկու հիմնական տեսակ կա։ Երկուսն էլ դիտվում են հեռախոսից, տարբերությունը որակի, ֆունկցիաների և գնի մեջ է։</p>
            </div>
            <div class="row g-4 mb-4">
                <div class="col-md-6">
                    <div class="sys-card h-100">
                        <span class="sys-tag">Խորհուրդ ենք տալիս նոր տեղադրման համար</span>
                        <i class="fa fa-network-wired step-icon"></i>
                        <h4>IP (թվային) համակարգ</h4>
                        <p>Յուրաքանչյուր տեսախցիկ փոքր համակարգիչ է, որը պատկերը թվային ձևով ուղարկում է ցանցային մալուխով։</p>
                        <p class="sys-fit mb-0"><b>Հարմար է՝</b> խանութ, գրասենյակ, պահեստ, տուն, որտեղ կարևոր է տեսնել դեմքերն ու մանրամասները, կամ հետագայում ավելացնել տեսախցիկներ։</p>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="sys-card h-100">
                        <span class="sys-tag sys-tag-muted">Մատչելի տարբերակ</span>
                        <i class="fa fa-video step-icon"></i>
                        <h4>Անալոգ (HD) համակարգ</h4>
                        <p>Ժամանակակից անալոգ տեսախցիկները (Hikvision Turbo HD, Dahua HDCVI) նույնպես տալիս են HD պատկեր, բայց աշխատում են կոաքսիալ մալուխով։</p>
                        <p class="sys-fit mb-0"><b>Հարմար է՝</b> փոքր բյուջե, տուն կամ ամառանոց, ինչպես նաև հին համակարգի փոխարինում, երբ լարերն արդեն կան։</p>
                    </div>
                </div>
            </div>
            <div class="table-responsive sys-table-wrap">
                <table class="table sys-table mb-0">
                    <thead><tr><th></th><th>IP</th><th>Անալոգ (HD)</th></tr></thead>
                    <tbody>{trs}</tbody>
                </table>
            </div>
            <p class="text-center mt-4 mb-0">Չգիտե՞ք որն ընտրել. զննման ժամանակ կնայենք օբյեկտը և կառաջարկենք ձեզ ճիշտ տարբերակը՝ <a href="quote.html#calc">անվճար</a>։</p>
        </div>
    </div>
    <!-- IP vs Analog End -->
"""


def calc_cta():
    return f"""
    <!-- Calc CTA Start -->
    <div class="container-xxl py-5">
        <div class="container">
            <div class="cta-band">
                <div>
                    <h3 class="text-white mb-2">Ի՞նչ համակարգ է պետք ձեր օբյեկտին</h3>
                    <p class="mb-0">Պատասխանեք 6 հարցի և ստացեք անվճար հաշվարկ։</p>
                </div>
                <div class="d-flex flex-wrap gap-2">
                    <a href="quote.html#calc" class="btn btn-primary btn-lg rounded-pill px-4"><i class="fa fa-calculator me-2"></i>Հաշվիր համակարգը</a>
                    <a href="tel:{PHONE}" class="btn btn-outline-light btn-lg rounded-pill px-4"><i class="fa fa-phone-alt me-2"></i>Զանգել</a>
                </div>
            </div>
        </div>
    </div>
    <!-- Calc CTA End -->
"""


def quote_form(heading_tag="h2"):
    opts = "\n".join(f'                                        <option>{o}</option>' for o in SERVICE_OPTIONS)
    return f"""
    <!-- Quote Start -->
    <div class="container-fluid bg-light overflow-hidden my-5 px-lg-0">
        <div class="container quote px-lg-0">
            <div class="row g-0 mx-lg-0">
                <div class="col-lg-6 ps-lg-0" style="min-height: 400px;">
                    <div class="position-relative h-100">
                        <img class="position-absolute img-fluid w-100 h-100" src="img/work/work-2.jpg" style="object-fit: cover;" alt="SmartEye-ի տեղադրած տեսախցիկ">
                    </div>
                </div>
                <div class="col-lg-6 quote-text py-5 wow fadeIn" data-wow-delay="0.3s">
                    <div class="p-lg-5 pe-lg-0">
                        <div class="bg-primary mb-3" style="width: 60px; height: 2px;"></div>
                        <{heading_tag} class="display-5 mb-4">Անվճար խորհրդատվություն</{heading_tag}>
                        <p class="mb-4 pb-2">Լրացրեք ձևը կամ զանգահարեք <a href="tel:{PHONE}">{PHONE_TXT}</a>։ Կկապվենք ձեզ հետ, կզննենք օբյեկտը և կառաջարկենք լուծում՝ անվճար։</p>
                        <form id="form" class="js-quote-form" method="post" action="send.php">
                            <input type="hidden" name="form" value="quote">
                            <div class="hp-field" aria-hidden="true"><input name="website" type="text" tabindex="-1" autocomplete="off"></div>
                            <div class="row g-3">
                                <div class="col-12 col-sm-6">
                                    <input name="name" type="text" class="form-control border-0" placeholder="Ձեր անունը" style="height: 55px;" required>
                                </div>
                                <div class="col-12 col-sm-6">
                                    <input name="phone" type="tel" class="form-control border-0" placeholder="Հեռախոսահամար" style="height: 55px;" required>
                                </div>
                                <div class="col-12">
                                    <select name="service" class="form-select border-0" style="height: 55px;" required>
                                        <option value="" selected disabled>Ընտրեք ծառայությունը</option>
{opts}
                                    </select>
                                </div>
                                <div class="col-12">
                                    <textarea name="note" class="form-control border-0" rows="4" placeholder="Լրացուցիչ տեղեկություն (օբյեկտ, տեսախցիկների քանակ, հասցե)"></textarea>
                                </div>
                                <div class="col-12">
                                    <button class="btn btn-primary w-100 py-3" type="submit">Ուղարկել հայտը</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Quote End -->
"""


# The template's forms have no server behind them. This opens the visitor's mail app
# with the request filled in, so a request is never silently lost.
FORM_JS = """
    <script>
    (function () {
        var m = location.search.match(/[?&]sent=(ok|err)/);
        if (!m) return;
        var ok = m[1] === 'ok';
        var box = document.createElement('div');
        box.className = 'form-notice ' + (ok ? 'ok' : 'err');
        box.textContent = ok ? 'Շնորհակալություն, հայտը ստացանք։ Շուտով կկապվենք ձեզ հետ։'
                             : 'Ներողություն, հայտը չուղարկվեց։ Խնդրում ենք զանգահարել +374 43 535 332։';
        var form = document.querySelector('.js-quote-form, .js-contact-form');
        if (form) { form.parentNode.insertBefore(box, form); box.scrollIntoView({block: 'center'}); }
    })();
    </script>"""


# ---------- pages ----------

def build():
    os.makedirs(OUT, exist_ok=True)
    for d in ("css", "js", "lib", "img"):
        shutil.copytree(os.path.join(SRC, d), os.path.join(OUT, d), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("*.doc", "*.docx", "*.pdf", "*.txt"))
    shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "work-photos"), os.path.join(OUT, "img", "work"), dirs_exist_ok=True)
    shutil.copytree(os.path.join(os.path.dirname(os.path.abspath(__file__)), "work-videos"), os.path.join(OUT, "img", "video"), dirs_exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(__file__), "send.php"), os.path.join(OUT, "send.php"))
    shutil.copy(os.path.join(os.path.dirname(__file__), "smarteye-presentation.pdf"), os.path.join(OUT, "smarteye-presentation.pdf"))
    shutil.copy(os.path.join(os.path.dirname(__file__), "smarteye.css"), os.path.join(OUT, "css", "smarteye.css"))

    site_desc = "SmartEye System — տեսախցիկների, ազդանշանային համակարգերի և լոկալ ցանցերի տեղադրում Երևանում և Արագածոտնի մարզում։ Hikvision և Dahua սարքավորումներ, խանութի կշեռքներ, անվճար խորհրդատվություն։"

    # index
    trust = [("fa-shield-alt", "Hikvision և Dahua"), ("fa-mobile-alt", "Դիտում հեռախոսից"), ("fa-map-marker-alt", "Երևան և Արագածոտն")]
    trust_html = "".join(f'<span class="hero-chip"><i class="fa {i} me-2"></i>{t}</span>' for i, t in trust)

    steps = [
        ("fa-phone-alt", "Զանգ կամ հայտ", "Զանգահարեք կամ թողեք հայտ կայքում"),
        ("fa-search-location", "Անվճար զննում", "Գալիս ենք, նայում ենք օբյեկտը և առաջարկում լուծում"),
        ("fa-tools", "Տեղադրում", "Կոկիկ մոնտաժ, լարերը թաքցված, ամեն ինչ կարգավորված"),
        ("fa-mobile-alt", "Դիտում հեռախոսից", "Միացնում ենք հավելվածը և սովորեցնում օգտվել"),
    ]
    steps_html = "".join(f"""
                <div class="col-sm-6 col-lg-3">
                    <div class="step h-100">
                        <span class="step-num">{i + 1}</span>
                        <i class="fa {ic} step-icon"></i>
                        <h5 class="mb-2">{t}</h5>
                        <p class="mb-0 small">{d}</p>
                    </div>
                </div>""" for i, (ic, t, d) in enumerate(steps))

    faq = [
        ("Կարո՞ղ եմ տեսախցիկները դիտել հեռախոսից։",
         "Այո։ Տեղադրելուց հետո միացնում ենք Hik-Connect (Hikvision) կամ DMSS (Dahua) հավելվածը, և ձեր օբյեկտը կտեսնեք ցանկացած վայրից՝ ինտերնետի առկայության դեպքում։"),
        ("Խորհրդատվությունն իսկապե՞ս անվճար է։",
         "Այո։ Գալիս ենք, զննում ենք օբյեկտը, որոշում ենք տեսախցիկների քանակն ու տեղերը և ներկայացնում ենք առաջարկ՝ առանց որևէ պարտավորության։"),
        ("Ո՞ր բրենդներով եք աշխատում։",
         "Hikvision և Dahua՝ տեսահսկման ոլորտում աշխարհում ամենատարածված բրենդները։ Մենք օգնում ենք ընտրել մոդելը ձեր օբյեկտին և բյուջեին համապատասխան, իսկ սարքավորումը ձեռք է բերվում Հայաստանի պաշտոնական ներմուծողներից՝ պաշտոնական երաշխիքով։ Մենք տեղադրում, կարգավորում և սպասարկում ենք։"),
        ("Ո՞րն է տարբերությունը IP և անալոգ տեսախցիկների միջև։",
         "IP տեսախցիկները թվային են. ավելի բարձր որակ և խելացի ֆունկցիաներ (մարդու և մեքենայի ճանաչում)։ Անալոգները (HD) ավելի մատչելի են և հարմար են հին լարերով։ Մանրամասն՝ <a href=\"service.html#ipvsanalog\">այստեղ</a>։"),
        ("Ի՞նչ են «խելացի» (AI) տեսախցիկները։",
         "Hikvision AcuSense և Dahua WizSense տեսախցիկները ճանաչում են մարդուն և մեքենային, անտեսում են ծառերն ու կենդանիներին, ուստի ահազանգը գալիս է միայն իրական վտանգի դեպքում։ Մանրամասն՝ <a href=\"smart.html\">այստեղ</a>։"),
        ("Տեսախցիկները գիշերը տեսնու՞մ են։",
         "Այո, մեր առաջարկած տեսախցիկներն ունեն գիշերային տեսողություն։ Իսկ ColorVu մոդելները (2, 4 և 5 ՄՊ) գիշերն էլ գունավոր պատկեր են տալիս։"),
        ("Որտե՞ղ եք աշխատում։",
         "Երևանում և Արագածոտնի մարզում։ Այլ վայրերի համար զանգահարեք, կքննարկենք։"),
        ("Բացի տեսախցիկներից ի՞նչ եք անում։",
         "Ազդանշանային և հակահրդեհային համակարգեր, լոկալ ցանցեր և Wi-Fi, խանութի կշեռքներ, համակարգիչների սպասարկում։"),
    ]
    faq_html = "".join(f"""
                <div class="accordion-item">
                    <h3 class="accordion-header" id="fh{i}">
                        <button class="accordion-button{'' if i == 0 else ' collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#fc{i}" aria-expanded="{'true' if i == 0 else 'false'}" aria-controls="fc{i}">{q}</button>
                    </h3>
                    <div id="fc{i}" class="accordion-collapse collapse{' show' if i == 0 else ''}" aria-labelledby="fh{i}" data-bs-parent="#faq">
                        <div class="accordion-body">{a}</div>
                    </div>
                </div>""" for i, (q, a) in enumerate(faq))
    faq_html += faq_ld(faq)

    body = f"""
    <!-- Hero Start -->
    <section class="hero">
        <div class="container">
            <div class="row align-items-center g-5">
                <div class="col-lg-6">
                    <h1 class="hero-kicker">Տեսախցիկների, ալարմի և ցանցերի տեղադրում Երևանում</h1>
                    <p class="hero-title">Ձեր տունն ու բիզնեսը՝ միշտ ձեր աչքի առաջ</p>
                    <p class="hero-lead">Տեղադրում ենք տեսախցիկներ, ազդանշանային համակարգեր և ցանցեր Երևանում և Արագածոտնում։ Ամեն ինչ կարգավորում ենք այնպես, որ ձեր օբյեկտը տեսնեք հեռախոսից՝ ցանկացած պահի։</p>
                    <div class="d-flex flex-wrap gap-3 mb-4">
                        <a href="#calc" class="btn btn-primary btn-lg rounded-pill px-4"><i class="fa fa-calculator me-2"></i>Հաշվիր համակարգը</a>
                        <a href="tel:{PHONE}" class="btn btn-outline-light btn-lg rounded-pill px-4"><i class="fa fa-phone-alt me-2"></i>{PHONE_TXT}</a>
                    </div>
                    <a href="smarteye-presentation.pdf" target="_blank" rel="noopener" class="hero-pdf"><i class="fa fa-file-pdf me-2"></i>Դիտեք մեր ներկայացումը (PDF)</a>

                </div>
                <div class="col-lg-6">
                    <div class="hero-media">
                        <img src="img/work/work-10-hero.jpg" alt="SmartEye-ի տեղադրած Hikvision տեսախցիկ" class="hero-img" fetchpriority="high">
                        <div class="hero-badge"><i class="fa fa-video me-2"></i>Մեր իրական աշխատանքը</div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    <!-- Hero End -->

    <!-- Trust strip -->
    <div class="trust-strip">
        <div class="container">
            <div class="row g-3 text-center text-md-start">
                <div class="col-6 col-md-3"><div class="trust-item"><i class="fa fa-shield-alt"></i><span><b>Hikvision և Dahua</b>պաշտոնական երաշխիքով</span></div></div>
                <div class="col-6 col-md-3"><div class="trust-item"><i class="fa fa-handshake"></i><span><b>Անվճար</b>զննում և խորհրդատվություն</span></div></div>
                <div class="col-6 col-md-3"><div class="trust-item"><i class="fa fa-mobile-alt"></i><span><b>Դիտում հեռախոսից</b>կարգավորում ենք մենք</span></div></div>
                <div class="col-6 col-md-3"><div class="trust-item"><i class="fa fa-tools"></i><span><b>Կոկիկ մոնտաժ</b>և սպասարկում</span></div></div>
            </div>
        </div>
    </div>

    <!-- Steps Start -->
    <div class="container-xxl py-5">
        <div class="container">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-0">Ինչպես ենք աշխատում</h2>
            </div>
            <div class="row g-4">{steps_html}
            </div>
        </div>
    </div>
    <!-- Steps End -->
{services_grid()}
{smart_teaser()}
{door_viewer()}
{our_work_cta()}

    <!-- FAQ Start -->
    <div class="container-xxl py-5">
        <div class="container" style="max-width: 860px;">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-0">Հաճախ տրվող հարցեր</h2>
            </div>
            <div class="accordion" id="faq">{faq_html}
            </div>
        </div>
    </div>
    <!-- FAQ End -->
{calculator(PHONE, PHONE_TXT)}
"""
    page("index.html", "index.html",
         "SmartEye System — տեսախցիկների տեղադրում Երևանում և Արագածոտնում",
         site_desc, body, FORM_JS)

    # about
    page("about.html", "about.html", "Մեր մասին | SmartEye System",
         "SmartEye System-ը տեղադրում է տեսախցիկներ, ազդանշանային համակարգեր և լոկալ ցանցեր Երևանում՝ Hikvision և Dahua սարքավորումներով։",
         page_header("Մեր մասին") + about_block(more_link=False) + why_us() + calc_cta() + our_work_cta())

    # services
    page("service.html", "service.html",
         "Ծառայություններ | SmartEye System — տեսահսկում, ազդանշանային համակարգեր, ցանցեր",
         site_desc, page_header("Ծառայություններ") + services_grid() + smart_teaser() + door_viewer() + ip_vs_analog() + calc_cta())

    # projects / work
    page("project.html", "project.html", "Աշխատանքներ | SmartEye System",
         "SmartEye System-ի կատարած տեսախցիկների տեղադրումների լուսանկարներ և տեսանյութեր։",
         page_header("Աշխատանքներ") + our_work_cta(with_facebook=True) + calc_cta())

    # alarm
    page("alarm.html", "", "Ազդանշանային համակարգեր Hikvision | SmartEye System",
         "Hikvision ալարմ՝ անլար (AX PRO) և լարային (AX Hybrid PRO)։ Շարժման, դռան, ծխի և ջրի սենսորներ, ահազանգ հեռախոսին։ Տեղադրում Երևանում և Արագածոտնում։",
         page_header("Ազդանշանային համակարգեր") + alarm_page_body())

    # smart cameras
    page("smart.html", "", "Խելացի (AI) տեսախցիկներ | SmartEye System",
         "Hikvision AcuSense և Dahua WizSense խելացի տեսախցիկներ. մարդու և մեքենայի ճանաչում, ավելի քիչ կեղծ ահազանգ։ Տեղադրում Երևանում և Արագածոտնում։",
         page_header("Խելացի տեսախցիկներ") + smart_page_body())

    # quote
    page("quote.html", "quote.html", "Անվճար խորհրդատվություն | SmartEye System",
         "Թողեք հայտ և ստացեք անվճար խորհրդատվություն տեսախցիկների, ազդանշանային համակարգերի կամ ցանցի տեղադրման համար։",
         page_header("Անվճար խորհրդատվություն") + calculator(PHONE, PHONE_TXT) + ip_vs_analog(), FORM_JS)

    # contact
    page("contact.html", "contact.html", "Կապ | SmartEye System",
         f"Կապվեք SmartEye System-ի հետ՝ {PHONE_TXT}, {EMAIL}։ Երևան։",
         page_header("Կապ") + f"""
    <div class="container-fluid bg-light overflow-hidden px-lg-0" style="margin: 6rem 0;">
        <div class="container contact px-lg-0">
            <div class="row g-0 mx-lg-0">
                <div class="col-lg-6 contact-text py-5 wow fadeIn" data-wow-delay="0.3s">
                    <div class="p-lg-5 ps-lg-0">
                        <div class="bg-primary mb-3" style="width: 60px; height: 2px;"></div>
                        <h2 class="display-5 mb-4">Կապ մեզ հետ</h2>
                        <p class="mb-2"><i class="fa fa-phone-alt text-primary me-3"></i><a href="tel:{PHONE}">{PHONE_TXT}</a></p>
                        <p class="mb-2"><i class="fa fa-envelope text-primary me-3"></i><a href="mailto:{EMAIL}">{EMAIL}</a></p>
                        <p class="mb-4"><i class="fa fa-map-marker-alt text-primary me-3"></i>Երևան</p>
                        <form id="form" class="js-contact-form" method="post" action="send.php">
                            <input type="hidden" name="form" value="contact">
                            <div class="hp-field" aria-hidden="true"><input name="website" type="text" tabindex="-1" autocomplete="off"></div>
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <div class="form-floating">
                                        <input name="name" type="text" class="form-control" id="name" placeholder="Ձեր անունը" required>
                                        <label for="name">Ձեր անունը</label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="form-floating">
                                        <input name="phone" type="tel" class="form-control" id="phone" placeholder="Հեռախոս" required>
                                        <label for="phone">Հեռախոս</label>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <div class="form-floating">
                                        <input name="subject" type="text" class="form-control" id="subject" placeholder="Թեմա">
                                        <label for="subject">Թեմա</label>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <div class="form-floating">
                                        <textarea name="message" class="form-control" placeholder="Հաղորդագրություն" id="message" style="height: 120px" required></textarea>
                                        <label for="message">Հաղորդագրություն</label>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <button class="btn btn-primary rounded-pill py-3 px-5" type="submit">Ուղարկել</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
                <div class="col-lg-6 pe-lg-0" style="min-height: 400px;">
                    <div class="position-relative h-100">
                        <iframe class="position-absolute w-100 h-100" style="border:0;"
                            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d116770.30958254208!2d44.40616664732808!3d40.153492405659506!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x406aa2dab8fc8b5b%3A0x3d1479ae87da526a!2z0JXRgNC10LLQsNC9!5e1!3m2!1sru!2sam!4v1762772640092!5m2!1sru!2sam"
                            title="Քարտեզ՝ Երևան" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
                    </div>
                </div>
            </div>
        </div>
    </div>
""", FORM_JS)

    # 404
    page("404.html", "", "Էջը չի գտնվել | SmartEye System", site_desc,
         page_header("Էջը չի գտնվել") + """
    <div class="container-xxl py-5 wow fadeInUp" data-wow-delay="0.1s">
        <div class="container text-center">
            <div class="row justify-content-center">
                <div class="col-lg-6">
                    <i class="bi bi-exclamation-triangle display-1 text-primary"></i>
                    <h1 class="display-1">404</h1>
                    <h2 class="mb-4">Էջը չի գտնվել</h2>
                    <p class="mb-4">Ներողություն, այս էջը գոյություն չունի կամ տեղափոխվել է։</p>
                    <a class="btn btn-primary rounded-pill py-3 px-5" href="index.html">Վերադառնալ գլխավոր էջ</a>
                </div>
            </div>
        </div>
    </div>
""")

    # Retired pages: placeholder/broken content. Redirect so old links still land somewhere useful.
    for old, target in [("testimonial.html", "index.html"), ("team.html", "about.html"),
                        ("feature.html", "about.html"), ("hikvision.html", "service.html"),
                        ("dahua.html", "service.html"), ("service-cctv.html", "service.html")]:
        with open(os.path.join(OUT, old), "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html lang="hy"><head><meta charset="utf-8"><title>SmartEye System</title>
<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="https://smarteye.am/{target}"></head>
<body><a href="{target}">SmartEye System</a></body></html>
""")


def about_block(more_link):
    more = '<a href="about.html" class="btn btn-primary rounded-pill py-3 px-5">Ավելին</a>' if more_link else \
        '<a href="quote.html#calc" class="btn btn-primary rounded-pill py-3 px-5"><i class="fa fa-calculator me-2"></i>Հաշվիր համակարգը</a>'
    more += ' <a href="smarteye-presentation.pdf" target="_blank" rel="noopener" class="btn btn-outline-primary rounded-pill py-3 px-4 ms-sm-2 mt-2 mt-sm-0"><i class="fa fa-file-pdf me-2"></i>Մեր ներկայացումը (PDF)</a>'
    return f"""
    <!-- About Start -->
    <div class="container-fluid bg-light overflow-hidden my-5 px-lg-0">
        <div class="container about px-lg-0">
            <div class="row g-0 mx-lg-0">
                <div class="col-lg-6 ps-lg-0" style="min-height: 400px;">
                    <div class="position-relative h-100">
                        <img class="position-absolute img-fluid w-100 h-100" src="img/work/work-1.jpg" style="object-fit: cover;" alt="Hikvision տեսախցիկ՝ SmartEye-ի տեղադրում">
                    </div>
                </div>
                <div class="col-lg-6 about-text py-5 wow fadeIn" data-wow-delay="0.3s">
                    <div class="p-lg-5 pe-lg-0">
                        <div class="bg-primary mb-3" style="width: 60px; height: 2px;"></div>
                        <h2 class="display-5 mb-4">Մեր մասին</h2>
                        <p class="mb-4">SmartEye System-ը զբաղվում է տեսահսկման, ազդանշանային համակարգերի և լոկալ ցանցերի նախագծմամբ ու տեղադրմամբ Երևանում։ Մեր մասնագետներն ունեն համակարգային ադմինիստրավորման, ցանցերի և անվտանգության համակարգերի փորձ։</p>
                        <ul class="list-unstyled mb-4 pb-2">
                            <li class="mb-2"><i class="fa fa-check text-primary me-3"></i>Տներ, բնակարաններ և ամառանոցներ</li>
                            <li class="mb-2"><i class="fa fa-check text-primary me-3"></i>Խանութներ, գրասենյակներ և ռեստորաններ</li>
                            <li class="mb-2"><i class="fa fa-check text-primary me-3"></i>Պահեստներ և արտադրական տարածքներ</li>
                        </ul>
                        {more}
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- About End -->
"""


def seo_files():
    pages = ["index.html", "service.html", "smart.html", "alarm.html", "project.html", "about.html", "quote.html", "contact.html"]
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for pg in pages:
            loc = "https://smarteye.am/" + ("" if pg == "index.html" else pg)
            f.write(f"  <url><loc>{loc}</loc><lastmod>{datetime.date.today().isoformat()}</lastmod></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /send.php\nDisallow: /tg-test.php\nSitemap: https://smarteye.am/sitemap.xml\n")
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0B1530"/>'
           '<path d="M8 32 C18 16, 46 16, 56 32 C46 48, 18 48, 8 32 Z" fill="none" stroke="#1E6BFF" stroke-width="4"/>'
           '<circle cx="32" cy="32" r="9" fill="#1E6BFF"/><circle cx="35" cy="29" r="3" fill="#fff"/></svg>')
    with open(os.path.join(OUT, "img", "favicon.svg"), "w") as f:
        f.write(svg)
    shutil.copy(os.path.join(os.path.dirname(__file__), "favicon.png"), os.path.join(OUT, "img", "favicon.png"))


if __name__ == "__main__":
    build()
    seo_files()
    print("built", sorted(f for f in os.listdir(OUT) if f.endswith(".html")))

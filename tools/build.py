#!/usr/bin/env python3
"""Generate the SmartEye System site pages from one shared layout.

Usage: python3 build.py <template_dir> <out_dir>
Copies css/js/lib/img from the template (skipping non-web files) and writes all pages.
"""
import os, shutil, sys

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
    ("quote.html", "Անվճար առաջարկ"),
    ("contact.html", "Կապ"),
]

SERVICES = [
    ("icon-6.png", "Տեսախցիկների տեղադրում",
     "IP և անալոգ տեսախցիկների, NVR և DVR ձայնագրիչների տեղադրում տների, խանութների, գրասենյակների և արտադրամասերի համար։ Կարգավորում ենք հեռախոսից դիտումը, որ ձեր օբյեկտը միշտ տեսնեք՝ որտեղ էլ լինեք։"),
    ("icon-9.png", "Ազդանշանային և հակահրդեհային համակարգեր",
     "Ներխուժման ազդանշանային համակարգեր, շարժման և դռան սենսորներ, ծխի և հրդեհի դետեկտորներ։ Վտանգի դեպքում ազդանշանը անմիջապես հասնում է ձեզ։"),
    ("icon-3.png", "Լոկալ ցանցերի կառուցում",
     "Գրասենյակների և կազմակերպությունների լոկալ ցանցերի (LAN) և Wi-Fi-ի նախագծում, մոնտաժ և սպասարկում՝ կայուն, արագ և անվտանգ կապի համար։"),
    ("icon-10.png", "Խանութի կշեռքներ",
     "Խանութների և առևտրի կետերի համար կշեռքների վաճառք, տեղադրում և կարգավորում։"),
    ("icon-8.png", "Համակարգիչների սպասարկում",
     "Համակարգիչների արագ և որակյալ սպասարկում՝ ինչպես տանը, այնպես էլ գրասենյակում։"),
]

SERVICE_OPTIONS = [s[1] for s in SERVICES] + ["Այլ / չգիտեմ, խորհրդատվություն է պետք"]


def head(title, desc):
    return f"""<!DOCTYPE html>
<html lang="hy">

<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta content="տեսախցիկների տեղադրում, տեսահսկում Երևան, ազդանշանային համակարգ, ալարմ, լոկալ ցանց, LAN, Hikvision, Dahua, խանութի կշեռք, SmartEye" name="keywords">
    <meta content="{desc}" name="description">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://smarteye.am/">
    <meta property="og:image" content="https://smarteye.am/img/carousel-1.jpg">

    <link href="img/favicon.ico" rel="icon">

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
    <div id="spinner" class="show bg-white position-fixed translate-middle w-100 vh-100 top-50 start-50 d-flex align-items-center justify-content-center">
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
            <span class="sr-only">Բեռնվում է...</span>
        </div>
    </div>
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
            <h2 class="m-0 text-primary">SmartEye System</h2>
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
                    <h5 class="text-light mb-4">Կապ</h5>
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
                    <a class="btn btn-link" href="project.html">Աշխատանքներ</a>
                    <a class="btn btn-link" href="quote.html">Անվճար առաջարկ</a>
                    <a class="btn btn-link" href="contact.html">Կապ</a>
                </div>
            </div>
        </div>
        <div class="container">
            <div class="copyright border-top border-secondary py-4">
                <div class="row">
                    <div class="col-md-6 text-center text-md-start mb-3 mb-md-0">
                        &copy; {YEAR} <a class="border-bottom" href="index.html">SmartEye System</a>։ Բոլոր իրավունքները պաշտպանված են։
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
    html = head(title, desc) + topbar_nav(active) + body + footer(extra_js)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(html)


# ---------- reusable sections ----------

def services_grid(with_cta=True):
    delays = ["0.1s", "0.3s", "0.5s"]
    cards = []
    for i, (icon, name, text) in enumerate(SERVICES):
        cards.append(f"""
                <div class="col-md-6 col-lg-4 wow fadeIn" data-wow-delay="{delays[i % 3]}">
                    <div class="service-item border h-100 p-5">
                        <div class="btn-square bg-light rounded-circle mb-4" style="width: 64px; height: 64px;">
                            <img class="img-fluid" src="img/icon/{icon}" alt="">
                        </div>
                        <h4 class="mb-3">{name}</h4>
                        <p class="mb-0">{text}</p>
                    </div>
                </div>""")
    if with_cta:
        cards.append(f"""
                <div class="col-md-6 col-lg-4 wow fadeIn" data-wow-delay="0.5s">
                    <div class="service-item service-cta border h-100 p-5 bg-primary">
                        <div class="btn-square bg-light rounded-circle mb-4" style="width: 64px; height: 64px;">
                            <img class="img-fluid" src="img/icon/icon-2.png" alt="">
                        </div>
                        <h4 class="mb-3 text-white">Անվճար խորհրդատվություն</h4>
                        <p class="mb-4 text-white">Կգանք, կզննենք օբյեկտը և կառաջարկենք ձեզ հարմար լուծում՝ անվճար։</p>
                        <a class="btn btn-light me-2 mb-2" href="tel:{PHONE}"><i class="fa fa-phone-alt me-2"></i>Զանգել</a>
                        <a class="btn btn-outline-light mb-2" href="quote.html">Թողնել հայտ</a>
                    </div>
                </div>""")
    return f"""
    <!-- Service Start -->
    <div class="container-xxl py-5">
        <div class="container">
            <div class="text-center">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-3">Մեր ծառայությունները</h2>
                <p class="mb-5">Աշխատում ենք Hikvision և Dahua սարքավորումներով՝ նախագծումից մինչև տեղադրում և սպասարկում։</p>
            </div>
            <div class="row g-0 service-row">{"".join(cards)}
            </div>
        </div>
    </div>
    <!-- Service End -->
"""


def why_us():
    items = [
        ("icon-7.png", "Hikvision և Dahua", "Աշխարհում ամենատարածված բրենդները"),
        ("icon-10.png", "Անվճար խորհրդատվություն", "Օբյեկտի զննում և առաջարկ՝ առանց վճարի"),
        ("icon-3.png", "Դիտում հեռախոսից", "Կարգավորում ենք, որ ամեն տեղից տեսնեք"),
        ("icon-2.png", "Սպասարկում", "Տեղադրումից հետո էլ կապի մեջ ենք"),
    ]
    cols = "".join(f"""
                        <div class="col-sm-6">
                            <div class="d-flex align-items-center">
                                <div class="btn-square bg-white rounded-circle flex-shrink-0" style="width: 64px; height: 64px;">
                                    <img class="img-fluid" src="img/icon/{ic}" alt="">
                                </div>
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
                        <img class="position-absolute img-fluid w-100 h-100" src="img/feature.jpg" style="object-fit: cover;" alt="Տեսախցիկ">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Feature End -->
"""


WORK_PHOTOS = [  # real SmartEye installations (EXIF/GPS stripped)
    ("work-1", "Hikvision տեսախցիկ այգու մուտքի մոտ"),
    ("work-2", "Պտտվող տեսախցիկ տան անկյունում"),
    ("work-3", "Երկու տեսախցիկ՝ այգու երկու ուղղությամբ"),
    ("work-4", "Տեսախցիկ տան ճակատին"),
    ("work-5", "Այսպես է երևում տեսախցիկից"),
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


TIKTOK_VIDEOS = [  # most-viewed SmartEye TikToks; swap IDs here to feature newer ones
    "7665792168635682068",
    "7665790815272307989",
    "7677865339698302228",
]
FB_PLUGIN = ("https://www.facebook.com/plugins/page.php?href=" + FB.replace(":", "%3A").replace("/", "%2F")
             + "&tabs=timeline&width=340&height=520&small_header=true&adapt_container_width=true&hide_cover=false&show_facepile=false")


def our_work_cta(with_facebook=False):
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
            <h3 class="text-center mb-4">Վերջին տեսանյութերը</h3>
            <div class="row g-4 justify-content-center">{vids}
            </div>
            <div class="text-center mt-4">
                <a class="btn btn-primary rounded-pill py-3 px-5" href="{TT}" target="_blank" rel="noopener"><i class="fab fa-tiktok me-2"></i>Բոլոր տեսանյութերը</a>
            </div>{fb}
        </div>
    </div>
    <script async src="https://www.tiktok.com/embed.js"></script>
    <!-- Social End -->
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
                        <img class="position-absolute img-fluid w-100 h-100" src="img/quote.jpg" style="object-fit: cover;" alt="">
                    </div>
                </div>
                <div class="col-lg-6 quote-text py-5 wow fadeIn" data-wow-delay="0.3s">
                    <div class="p-lg-5 pe-lg-0">
                        <div class="bg-primary mb-3" style="width: 60px; height: 2px;"></div>
                        <{heading_tag} class="display-5 mb-4">Անվճար առաջարկ</{heading_tag}>
                        <p class="mb-4 pb-2">Լրացրեք ձևը կամ զանգահարեք <a href="tel:{PHONE}">{PHONE_TXT}</a>։ Կկապվենք ձեզ հետ, կզննենք օբյեկտը և կառաջարկենք լուծում՝ անվճար։</p>
                        <form class="js-quote-form">
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
FORM_JS = f"""
    <script>
    document.querySelectorAll('.js-quote-form, .js-contact-form').forEach(function (form) {{
        form.addEventListener('submit', function (e) {{
            e.preventDefault();
            var d = new FormData(form), lines = [];
            d.forEach(function (v, k) {{ if (v) lines.push(v); }});
            var subject = form.classList.contains('js-quote-form') ? 'Հայտ կայքից — ' + (d.get('service') || '') : (d.get('subject') || 'Նամակ կայքից');
            window.location.href = 'mailto:{EMAIL}?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\\n'));
        }});
    }});
    </script>"""


# ---------- pages ----------

def build():
    os.makedirs(OUT, exist_ok=True)
    for d in ("css", "js", "lib", "img"):
        shutil.copytree(os.path.join(SRC, d), os.path.join(OUT, d), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("*.doc", "*.docx", "*.pdf", "*.txt"))
    shutil.copytree("/home/claude/media/web", os.path.join(OUT, "img", "work"), dirs_exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(__file__), "smarteye.css"), os.path.join(OUT, "css", "smarteye.css"))

    site_desc = "SmartEye System — տեսախցիկների, ազդանշանային համակարգերի և լոկալ ցանցերի տեղադրում Երևանում։ Hikvision և Dahua սարքավորումներ, խանութի կշեռքներ, անվճար խորհրդատվություն։"

    # index
    slides = [
        ("carousel-1.jpg", "Տեսահսկում և անվտանգություն՝ ձեր տան և բիզնեսի համար",
         "Տեսախցիկներ, ազդանշանային համակարգեր և ցանցեր՝ Hikvision և Dahua սարքավորումներով։"),
        ("carousel-2.jpg", "Տեսեք ձեր օբյեկտը հեռախոսից՝ ցանկացած պահի",
         "Տեղադրում ենք, կարգավորում ենք հեռակա դիտումը և սովորեցնում ենք օգտվել։"),
        ("carousel-3.jpg", "Անվճար խորհրդատվություն և առաջարկ",
         "Կգանք, կզննենք օբյեկտը և կառաջարկենք լուծում՝ ձեր բյուջեին համապատասխան։"),
    ]
    car = "".join(f"""
            <div class="owl-carousel-item position-relative">
                <img class="img-fluid" src="img/{img}" alt="">
                <div class="carousel-inner">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-12 col-lg-8 text-center">
                                <{"h1" if i == 0 else "h2"} class="display-3 text-white animated slideInDown mb-4">{h}</{"h1" if i == 0 else "h2"}>
                                <p class="fs-5 text-white mb-4 pb-2">{p}</p>
                                <a href="quote.html" class="btn btn-primary rounded-pill py-md-3 px-md-5 me-3 animated slideInLeft">Անվճար առաջարկ</a>
                                <a href="tel:{PHONE}" class="btn btn-light rounded-pill py-md-3 px-md-5 animated slideInRight"><i class="fa fa-phone-alt me-2"></i>Զանգել</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>""" for i, (img, h, p) in enumerate(slides))

    facts = [
        ("icon-3.png", "01", "Տեսահսկում", "Տեսախցիկների և ձայնագրիչների տեղադրում, հեռախոսից դիտման կարգավորում։"),
        ("icon-4.png", "02", "Ցանցերի կառուցում", "Լոկալ և կորպորատիվ ցանցերի նախագծում, մոնտաժ և սպասարկում։"),
        ("icon-2.png", "03", "Տեխնիկական աջակցություն", "Արագ արձագանք և խնդիրների օպերատիվ լուծում տեղադրումից հետո։"),
    ]
    facts_html = "".join(f"""
                <div class="col-md-6 col-lg-4 wow fadeIn" data-wow-delay="{0.1 + 0.2 * i:.1f}s">
                    <div class="h-100 bg-dark p-4 p-xl-5">
                        <div class="d-flex align-items-center justify-content-between mb-4">
                            <div class="btn-square rounded-circle bg-primary" style="width: 64px; height: 64px;">
                                <img class="img-fluid" src="img/icon/{ic}" alt="">
                            </div>
                            <span class="display-1 mb-0 fact-num">{n}</span>
                        </div>
                        <h5 class="text-white">{t}</h5>
                        <hr class="w-25">
                        <span>{d}</span>
                    </div>
                </div>""" for i, (ic, n, t, d) in enumerate(facts))

    body = f"""
    <!-- Carousel Start -->
    <div class="container-fluid p-0 pb-5">
        <div class="owl-carousel header-carousel position-relative">{car}
        </div>
    </div>
    <!-- Carousel End -->

    <!-- Facts Start -->
    <div class="container-xxl py-5">
        <div class="container">
            <div class="row g-4">{facts_html}
            </div>
        </div>
    </div>
    <!-- Facts End -->
{about_block(more_link=True)}
{services_grid()}
{why_us()}
{our_work_cta()}
{quote_form()}
"""
    page("index.html", "index.html",
         "SmartEye System — տեսախցիկների տեղադրում և անվտանգության համակարգեր Երևանում",
         site_desc, body, FORM_JS)

    # about
    page("about.html", "about.html", "Մեր մասին | SmartEye System",
         "SmartEye System-ը տեղադրում է տեսախցիկներ, ազդանշանային համակարգեր և լոկալ ցանցեր Երևանում՝ Hikvision և Dahua սարքավորումներով։",
         page_header("Մեր մասին") + about_block(more_link=False) + why_us() + our_work_cta())

    # services
    page("service.html", "service.html",
         "Ծառայություններ | SmartEye System — տեսահսկում, ազդանշանային համակարգեր, ցանցեր",
         site_desc, page_header("Ծառայություններ") + services_grid())

    # projects / work
    page("project.html", "project.html", "Աշխատանքներ | SmartEye System",
         "SmartEye System-ի կատարած տեսախցիկների տեղադրումների լուսանկարներ և տեսանյութեր։",
         page_header("Աշխատանքներ") + our_work_cta(with_facebook=True))

    # quote
    page("quote.html", "quote.html", "Անվճար առաջարկ | SmartEye System",
         "Թողեք հայտ և ստացեք անվճար խորհրդատվություն տեսախցիկների, ազդանշանային համակարգերի կամ ցանցի տեղադրման համար։",
         page_header("Անվճար առաջարկ") + quote_form(), FORM_JS)

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
                        <form class="js-contact-form">
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
        '<a href="quote.html" class="btn btn-primary rounded-pill py-3 px-5">Անվճար առաջարկ</a>'
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


if __name__ == "__main__":
    build()
    print("built", sorted(f for f in os.listdir(OUT) if f.endswith(".html")))

"""System configurator ("հաշվիչ") for the homepage and quote.html.

The visitor first picks what they need (cameras, alarm or both); only the
relevant questions are shown. No prices: it builds a recommended setup and
sends it as a detailed request via send.php (email + Telegram).
"""

OBJECTS = [
    ("home", "fa-home", "Տուն / բնակարան"),
    ("shop", "fa-store", "Խանութ"),
    ("office", "fa-briefcase", "Գրասենյակ"),
    ("garden", "fa-tree", "Այգի / ամառանոց"),
    ("warehouse", "fa-warehouse", "Պահեստ / արտադրություն"),
]

SYSTEMS = [
    ("ip", "IP (թվային)", "Ավելի բարձր որակ, խելացի ֆունկցիաներ"),
    ("analog", "Անալոգ (HD)", "Ավելի մատչելի, հարմար հին լարերով"),
    ("unsure", "Չգիտեմ", "Կօգնենք ընտրել զննման ժամանակ"),
]

QUALITY = [
    ("2", "2 ՄՊ", "Full HD, մատչելի"),
    ("4", "4 ՄՊ", "Բարձր որակ"),
    ("5", "5 ՄՊ", "Ամենամանրամասն"),
]

DAYS = [("7", "7 օր"), ("14", "14 օր"), ("30", "30 օր")]

CAM_EXTRAS = [
    ("ai", "Խելացի ճանաչում (AcuSense / WizSense)"),
    ("cash", "Դրամարկղի (կասսայի) տեսախցիկ"),
]

AUDIO = [("no", "Առանց ձայնի"), ("yes", "Ձայնով (միկրոֆոն)")]

ALARM_TYPES = [
    ("wired", "Լարային", "Hikvision AX Hybrid PRO"),
    ("wireless", "Անլար", "Hikvision AX PRO"),
    ("unsure", "Չգիտեմ", "Կօգնենք ընտրել"),
]

# key, icon, label, default count
ALARM_PARTS = [
    ("motion", "fa-walking", "Շարժման տվիչ", 2),
    ("smoke", "fa-fire", "Ծխի տվիչ", 1),
    ("sirenIn", "fa-volume-up", "Սիրենա՝ ներսի", 1),
    ("sirenOut", "fa-bullhorn", "Սիրենա՝ դրսի", 1),
    ("pedal", "fa-shoe-prints", "Տագնապի ոտնակ (պեդալ)", 0),
]

OTHER = [
    ("net", "Ցանց / Wi-Fi"),
    ("fluke", "Մալուխի ստուգում Fluke-ով (Cat5e/Cat6 հաշվետվություն)"),
    ("scale", "Խանութի կշեռք"),
]


def _radios(name, items, checked, wide=False):
    cls = "calc-opt calc-opt-wide" if wide else "calc-opt"
    out = []
    for item in items:
        v, t = item[0], item[1]
        d = item[2] if len(item) > 2 else ""
        body = f"<b>{t}</b><small>{d}</small>" if wide else t
        out.append(f"""
                            <label class="{cls}">
                                <input type="radio" name="{name}" value="{v}" data-label="{t}"{' checked' if v == checked else ''}>
                                <span>{body}</span>
                            </label>""")
    return "".join(out)


def _checks(name, items):
    return "".join(f"""
                            <label class="calc-opt">
                                <input type="checkbox" name="{name}" value="{v}" data-label="{t}">
                                <span>{t}</span>
                            </label>""" for v, t in items)


def _stepper(key, icon, label, value):
    return f"""
                                <div class="col-sm-6">
                                    <div class="calc-step">
                                        <span class="calc-step-label"><i class="fa {icon} me-2"></i>{label}</span>
                                        <button type="button" class="calc-btn" data-step="{key}" data-d="-1" aria-label="Պակասեցնել">−</button>
                                        <output id="c_{key}">{value}</output>
                                        <button type="button" class="calc-btn" data-step="{key}" data-d="1" aria-label="Ավելացնել">+</button>
                                    </div>
                                </div>"""


def calculator(phone, phone_txt):
    objs = "".join(f"""
                            <label class="calc-obj">
                                <input type="radio" name="obj" value="{v}" data-label="{t}"{' checked' if i == 0 else ''}>
                                <span><i class="fa {ic}"></i>{t}</span>
                            </label>""" for i, (v, ic, t) in enumerate(OBJECTS))
    alarm_steps = "".join(_stepper(k, ic, t, d) for k, ic, t, d in ALARM_PARTS)
    defaults = {"in": 2, "out": 2, **{k: d for k, _, _, d in ALARM_PARTS}}
    js_defaults = ", ".join(f"{k}: {v}" for k, v in defaults.items())
    js_alarm = "[" + ", ".join(f'["{k}", "{t}"]' for k, _, t, _ in ALARM_PARTS) + "]"

    return f"""
    <!-- Calculator Start -->
    <div class="container-xxl py-5" id="calc">
        <div class="container">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-3">Հաշվիր քո համակարգը</h2>
                <p class="mx-auto mb-0" style="max-width: 620px;">Ընտրիր, թե ինչ է պետք, և պատասխանիր մի քանի հարցի. կտեսնես քո համակարգը, իսկ մենք կկապվենք և կհաշվարկենք ճշգրիտ արժեքը՝ անվճար։</p>
            </div>
            <div class="row g-4">
                <div class="col-lg-7">
                    <div class="calc-card">
                        <div class="calc-q">
                            <h5><span></span>Ի՞նչ է պետք</h5>
                            <div class="calc-need">
                                <label class="calc-tile">
                                    <input type="checkbox" name="need" value="cam" checked>
                                    <span class="calc-tile-body">
                                        <i class="fa fa-video calc-tile-ic"></i>
                                        <b>Տեսախցիկներ</b>
                                        <small>Տեսահսկում և դիտում հեռախոսից</small>
                                        <i class="fa fa-check calc-tile-check"></i>
                                    </span>
                                </label>
                                <label class="calc-tile">
                                    <input type="checkbox" name="need" value="alarm">
                                    <span class="calc-tile-body">
                                        <i class="fa fa-bell calc-tile-ic"></i>
                                        <b>Ազդանշանային համակարգ</b>
                                        <small>Ալարմ, տվիչներ, սիրենա</small>
                                        <i class="fa fa-check calc-tile-check"></i>
                                    </span>
                                </label>
                            </div>
                        </div>
                        <div class="calc-q">
                            <h5><span></span>Ի՞նչ օբյեկտ է</h5>
                            <div class="calc-objs">{objs}
                            </div>
                        </div>

                        <div class="calc-group" data-for="cam">
                            <div class="calc-group-title"><i class="fa fa-video me-2"></i>Տեսախցիկներ</div>
                            <div class="calc-q">
                                <h5><span></span>Քանի՞ տեսախցիկ</h5>
                                <div class="row g-3">{_stepper("in", "fa-door-closed", "Ներսում", 2)}{_stepper("out", "fa-sun", "Դրսում", 2)}
                                </div>
                                <p class="small text-muted mt-2 mb-0">Չգիտե՞ս, թե քանիսը։ Թող այսպես, զննման ժամանակ կճշտենք։</p>
                            </div>
                            <div class="calc-q">
                                <h5><span></span>Համակարգի տեսակ <a class="calc-help" href="service.html#ipvsanalog">Ո՞րն ընտրել</a></h5>
                                <div class="calc-opts calc-grid">{_radios("sys", SYSTEMS, "ip", wide=True)}
                                </div>
                            </div>
                            <div class="calc-q">
                                <h5><span></span>Պատկերի որակ</h5>
                                <div class="calc-opts calc-grid">{_radios("q", QUALITY, "4", wide=True)}
                                </div>
                                <div class="calc-opts mt-2">
                                    <label class="calc-opt">
                                        <input type="checkbox" name="colorvu" value="1">
                                        <span><i class="fa fa-moon"></i>ColorVu՝ գիշերն էլ գունավոր</span>
                                    </label>
                                </div>
                            </div>
                            <div class="calc-q">
                                <h5><span></span>Ձայն</h5>
                                <div class="calc-opts">{_radios("audio", AUDIO, "no")}
                                </div>
                            </div>
                            <div class="calc-q">
                                <h5><span></span>Քանի՞ օր պահել ձայնագրությունը</h5>
                                <div class="calc-opts">{_radios("days", DAYS, "14")}
                                </div>
                            </div>
                            <div class="calc-q mb-0">
                                <h5><span></span>Լրացուցիչ տեսախցիկների համար</h5>
                                <div class="calc-opts">{_checks("camx", CAM_EXTRAS)}
                                </div>
                            </div>
                        </div>

                        <div class="calc-group" data-for="alarm" hidden>
                            <div class="calc-group-title"><i class="fa fa-bell me-2"></i>Ազդանշանային համակարգ</div>
                            <div class="calc-q">
                                <h5><span></span>Ալարմի տեսակ <a class="calc-help" href="alarm.html">Ո՞րն ընտրել</a></h5>
                                <div class="calc-opts calc-grid">{_radios("atype", ALARM_TYPES, "wired", wide=True)}
                                </div>
                            </div>
                            <div class="calc-q mb-0">
                                <h5><span></span>Ի՞նչ սարքեր են պետք</h5>
                                <div class="row g-2">{alarm_steps}
                                </div>
                                <p class="small text-muted mt-2 mb-0">Չգիտե՞ք քանակը. թողեք այսպես, զննման ժամանակ կճշտենք։</p>
                            </div>
                        </div>

                        <div class="calc-q mb-0 mt-4">
                            <h5><span></span>Այլ ծառայություններ</h5>
                            <div class="calc-opts">{_checks("other", OTHER)}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-5">
                    <div class="calc-result" id="form">
                        <h4 class="text-white mb-3">Քո համակարգը</h4>
                        <ul class="calc-list" id="cList"></ul>
                        <p class="calc-note">Մոտավոր հաշվարկ է։ Զննումից հետո կօգնենք ընտրել ճշգրիտ մոդելները. սարքավորումը ձեռք է բերվում պաշտոնական ներմուծողներից՝ երաշխիքով, իսկ տեղադրումն ու կարգավորումը մենք ենք անում։</p>
                        <form class="js-quote-form" method="post" action="send.php" enctype="multipart/form-data">
                            <input type="hidden" name="form" value="quote">
                            <input type="hidden" name="service" id="cService">
                            <input type="hidden" name="note" id="cNote">
                            <div class="hp-field" aria-hidden="true"><input name="website" type="text" tabindex="-1" autocomplete="off"></div>
                            <input name="name" type="text" class="form-control mb-2" placeholder="Ձեր անունը" required>
                            <input name="phone" type="tel" class="form-control mb-2" placeholder="Հեռախոսահամար" required>
                            <input name="place" id="cPlace" type="text" class="form-control mb-2" placeholder="Բնակավայր (օր.՝ Երևան, Աշտարակ)">
                            <input type="hidden" name="loc" id="cLoc">
                            <div class="calc-attach mb-3">
                                <button type="button" class="calc-attach-btn" id="cLocBtn"><i class="fa fa-map-marker-alt me-2"></i><span>Ուղարկել տեղադրությունը</span></button>
                                <label class="calc-attach-btn mb-0">
                                    <i class="fa fa-camera me-2"></i><span id="cPhotoTxt">Կցել նկար (մինչև 5)</span>
                                    <input type="file" name="photos[]" id="cPhotos" accept="image/*" multiple hidden>
                                </label>
                                <p class="calc-attach-note mb-0">Ոչ պարտադիր. օբյեկտի նկարները և քարտեզի տեղը կօգնեն ավելի ճշգրիտ հաշվարկել։</p>
                            </div>
                            <button class="btn btn-primary w-100 py-3 rounded-pill" type="submit">Ստանալ ճշգրիտ գինը</button>
                        </form>
                        <p class="text-center small mt-3 mb-0">կամ զանգահարեք <a class="text-white fw-medium" href="tel:{phone}">{phone_txt}</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <a href="#form" class="calc-mbar" id="cBar"><span id="cBarTxt">Քո համակարգը</span><b>Տեսնել և ուղարկել <i class="fa fa-arrow-down ms-1"></i></b></a>
    <script>
    (function () {{
        var root = document.getElementById('calc');
        if (!root) return;
        var n = {{ {js_defaults} }};
        var ALARM = {js_alarm};
        function val(name) {{ return root.querySelector('input[name="' + name + '"]:checked'); }}
        function labels(name) {{
            return Array.prototype.map.call(root.querySelectorAll('input[name="' + name + '"]:checked'), function (e) {{ return e.dataset.label; }});
        }}
        function render() {{
            var cam = !!root.querySelector('input[name="need"][value="cam"]:checked');
            var alarm = !!root.querySelector('input[name="need"][value="alarm"]:checked');
            root.querySelector('[data-for="cam"]').hidden = !cam;
            root.querySelector('[data-for="alarm"]').hidden = !alarm;
            Object.keys(n).forEach(function (k) {{ var o = document.getElementById('c_' + k); if (o) o.textContent = n[k]; }});

            var obj = val('obj'), lines = [], what = [];
            if (cam) {{
                var total = n.in + n.out;
                var sys = val('sys'), q = val('q'), days = +(val('days') || {{ value: 14 }}).value;
                var cvu = val('colorvu');
                var rec = !sys || sys.value === 'unsure' ? 'ձայնագրիչ (NVR կամ DVR՝ կընտրենք միասին)'
                        : sys.value === 'ip' ? 'ձայնագրիչ (NVR)' : 'ձայնագրիչ (DVR)';
                var ch = total <= 4 ? 4 : total <= 8 ? 8 : total <= 16 ? 16 : 32;
                // H.265, continuous recording: ~10 GB/day for 2 MP, ~20 GB/day for 4 MP, ~25 GB/day for 5 MP
                var perDay = !q ? 20 : q.value === '2' ? 10 : q.value === '5' ? 25 : 20;
                var tb = total * perDay * days / 1000;
                var disk = [1, 2, 4, 6, 8, 10, 12, 16].find(function (d) {{ return d >= tb; }}) || Math.ceil(tb);
                lines.push(['fa-video', total + ' տեսախցիկ (' + n.in + ' ներսում, ' + n.out + ' դրսում)']);
                lines.push(['fa-project-diagram', 'Համակարգ՝ ' + (sys ? sys.dataset.label : '')]);
                lines.push(['fa-image', 'Որակ՝ ' + (q ? q.dataset.label : '') + (cvu ? ', ColorVu (գիշերը գունավոր)' : '')]);
                var au = val('audio');
                lines.push(['fa-microphone', 'Ձայն՝ ' + (au ? au.dataset.label.toLowerCase() : 'առանց ձայնի')]);
                lines.push(['fa-server', ch + '-ալիքանի ' + rec]);
                lines.push(['fa-hdd', 'Կոշտ սկավառակ՝ ' + disk + ' ՏԲ (' + days + ' օր)']);
                lines.push(['fa-mobile-alt', 'Դիտում հեռախոսից']);
                labels('camx').forEach(function (x) {{ lines.push(['fa-plus', x]); }});
                what.push(total + ' տեսախցիկ');
            }}
            if (alarm) {{
                var at = val('atype');
                lines.push(['fa-bell', 'Ալարմ՝ ' + (at ? at.dataset.label : '') + (at && at.value !== 'unsure' ? ' (' + at.parentNode.querySelector('small').textContent + ')' : '')]);
                ALARM.forEach(function (a) {{ if (n[a[0]] > 0) lines.push(['fa-check', a[1] + '՝ ' + n[a[0]]]); }});
                lines.push(['fa-mobile-alt', 'Ահազանգ հեռախոսին (Hik-Connect)']);
                what.push('ալարմ');
            }}
            labels('other').forEach(function (x) {{ lines.push(['fa-tools', x]); }});
            if (!lines.length) lines.push(['fa-info-circle', 'Ընտրեք, թե ինչ է պետք']);

            document.getElementById('cList').innerHTML = lines.map(function (l) {{
                return '<li><i class="fa ' + l[0] + '"></i>' + l[1] + '</li>';
            }}).join('');
            document.getElementById('cBarTxt').textContent = what.length ? what.join(' + ') : 'Ընտրեք, թե ինչ է պետք';
            document.getElementById('cService').value = 'Հաշվիչ — ' + (obj ? obj.dataset.label : '') + (what.length ? ', ' + what.join(' + ') : '');
            document.getElementById('cNote').value =
                'Օբյեկտ: ' + (obj ? obj.dataset.label : '') + '\\n' +
                lines.map(function (l) {{ return '• ' + l[1]; }}).join('\\n');
        }}
        root.addEventListener('click', function (e) {{
            var b = e.target.closest('.calc-btn');
            if (!b) return;
            var k = b.dataset.step;
            n[k] = Math.max(0, Math.min(32, n[k] + (+b.dataset.d)));
            render();
        }});
        root.addEventListener('change', render);
        var locBtn = document.getElementById('cLocBtn');
        locBtn.addEventListener('click', function () {{
            var t = locBtn.querySelector('span');
            if (!navigator.geolocation) {{ t.textContent = 'Տեղադրությունը հասանելի չէ'; return; }}
            t.textContent = 'Որոշում ենք...';
            navigator.geolocation.getCurrentPosition(function (p) {{
                var ll = p.coords.latitude.toFixed(6) + ',' + p.coords.longitude.toFixed(6);
                document.getElementById('cLoc').value = 'https://maps.google.com/?q=' + ll;
                locBtn.classList.add('done'); t.textContent = 'Տեղադրությունը ավելացվեց ✓';
            }}, function () {{ t.textContent = 'Չստացվեց, գրեք հասցեն վերևում'; }}, {{ enableHighAccuracy: true, timeout: 15000 }});
        }});
        var photos = document.getElementById('cPhotos');
        function shrink(file) {{
            return new Promise(function (ok) {{
                var img = new Image(), url = URL.createObjectURL(file);
                img.onload = function () {{
                    var k = Math.min(1, 1600 / Math.max(img.width, img.height));
                    var c = document.createElement('canvas'); c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
                    c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
                    c.toBlob(function (b) {{ URL.revokeObjectURL(url); ok(b ? new File([b], 'photo.jpg', {{ type: 'image/jpeg' }}) : file); }}, 'image/jpeg', 0.82);
                }};
                img.onerror = function () {{ ok(file); }};
                img.src = url;
            }});
        }}
        photos.addEventListener('change', function () {{
            var files = Array.prototype.slice.call(photos.files, 0, 5);
            var txt = document.getElementById('cPhotoTxt');
            if (!files.length) {{ txt.textContent = 'Կցել նկար (մինչև 5)'; return; }}
            txt.textContent = 'Պատրաստում ենք...';
            Promise.all(files.map(shrink)).then(function (out) {{
                try {{ var dt = new DataTransfer(); out.forEach(function (f) {{ dt.items.add(f); }}); photos.files = dt.files; }} catch (e) {{}}
                txt.textContent = out.length + ' նկար կցված է ✓';
                photos.parentNode.classList.add('done');
            }});
        }});
        root.querySelector('form').addEventListener('submit', function () {{
            var p = document.getElementById('cPlace').value.trim();
            if (p) document.getElementById('cNote').value += '\\nԲնակավայր: ' + p;
        }});
        var bar = document.getElementById('cBar'), card = root.querySelector('.calc-card'), res = document.getElementById('form');
        if ('IntersectionObserver' in window) {{
            var vis = {{ card: false, res: false }};
            var io = new IntersectionObserver(function (es) {{
                es.forEach(function (e) {{ vis[e.target === card ? 'card' : 'res'] = e.isIntersecting; }});
                bar.classList.toggle('show', vis.card && !vis.res);
            }});
            io.observe(card); io.observe(res);
        }}
        render();
    }})();
    </script>
    <!-- Calculator End -->
"""

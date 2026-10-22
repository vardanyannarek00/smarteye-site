"""System configurator ("հաշվիչ") for quote.html.

No prices: it builds a recommended setup (cameras, recorder channels, disk size)
from the visitor's answers and sends it as a detailed request via send.php.
"""

OBJECTS = [
    ("home", "fa-home", "Տուն / բնակարան"),
    ("shop", "fa-store", "Խանութ"),
    ("office", "fa-briefcase", "Գրասենյակ"),
    ("garden", "fa-tree", "Այգի / ամառանոց"),
    ("warehouse", "fa-warehouse", "Պահեստ / արտադրություն"),
]

QUALITY = [
    ("4", "4 ՄՊ", "Բարձր որակ, գիշերը՝ սև-սպիտակ"),
    ("5c", "5 ՄՊ ColorVu", "Գիշերն էլ գունավոր պատկեր"),
]

SYSTEMS = [
    ("ip", "IP (թվային)", "Ավելի բարձր որակ, խելացի ֆունկցիաներ"),
    ("analog", "Անալոգ (HD)", "Ավելի մատչելի, հարմար հին լարերով"),
    ("unsure", "Չգիտեմ", "Կօգնենք ընտրել զննման ժամանակ"),
]

DAYS = [("7", "7 օր"), ("14", "14 օր"), ("30", "30 օր")]

EXTRAS = [
    ("alarm", "Ազդանշանային համակարգ"),
    ("net", "Ցանց / Wi-Fi"),
    ("audio", "Ձայնի ձայնագրում"),
    ("scale", "Խանութի կշեռք"),
]


def calculator(phone, phone_txt):
    objs = "".join(f"""
                            <label class="calc-opt">
                                <input type="radio" name="obj" value="{v}" data-label="{t}"{' checked' if i == 0 else ''}>
                                <span><i class="fa {ic}"></i>{t}</span>
                            </label>""" for i, (v, ic, t) in enumerate(OBJECTS))
    qual = "".join(f"""
                            <label class="calc-opt calc-opt-wide">
                                <input type="radio" name="q" value="{v}" data-label="{t}"{' checked' if v == '4' else ''}>
                                <span><b>{t}</b><small>{d}</small></span>
                            </label>""" for v, t, d in QUALITY)
    systems = "".join(f"""
                            <label class="calc-opt calc-opt-wide">
                                <input type="radio" name="sys" value="{v}" data-label="{t}"{' checked' if v == 'ip' else ''}>
                                <span><b>{t}</b><small>{d}</small></span>
                            </label>""" for v, t, d in SYSTEMS)
    days = "".join(f"""
                            <label class="calc-opt">
                                <input type="radio" name="days" value="{v}"{' checked' if v == '14' else ''}>
                                <span>{t}</span>
                            </label>""" for v, t in DAYS)
    extras = "".join(f"""
                            <label class="calc-opt">
                                <input type="checkbox" name="extra" value="{v}" data-label="{t}">
                                <span>{t}</span>
                            </label>""" for v, t in EXTRAS)

    return f"""
    <!-- Calculator Start -->
    <div class="container-xxl py-5" id="calc">
        <div class="container">
            <div class="text-center mb-5">
                <div class="bg-primary mb-3 mx-auto" style="width: 60px; height: 2px;"></div>
                <h2 class="display-5 mb-3">Հաշվիր քո համակարգը</h2>
                <p class="mx-auto mb-0" style="max-width: 620px;">Պատասխանիր 6 հարցի. կտեսնես, թե ինչ համակարգ է պետք քո օբյեկտին, իսկ մենք կուղարկենք ճշգրիտ գինը՝ անվճար։</p>
            </div>
            <div class="row g-4">
                <div class="col-lg-7">
                    <div class="calc-card">
                        <div class="calc-q">
                            <h5><span>1</span>Ի՞նչ օբյեկտ է</h5>
                            <div class="calc-opts">{objs}
                            </div>
                        </div>
                        <div class="calc-q">
                            <h5><span>2</span>Քանի՞ տեսախցիկ</h5>
                            <div class="row g-3">
                                <div class="col-sm-6">
                                    <div class="calc-step">
                                        <span class="calc-step-label"><i class="fa fa-door-closed me-2"></i>Ներսում</span>
                                        <button type="button" class="calc-btn" data-step="in" data-d="-1" aria-label="Պակասեցնել">−</button>
                                        <output id="cIn">2</output>
                                        <button type="button" class="calc-btn" data-step="in" data-d="1" aria-label="Ավելացնել">+</button>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="calc-step">
                                        <span class="calc-step-label"><i class="fa fa-sun me-2"></i>Դրսում</span>
                                        <button type="button" class="calc-btn" data-step="out" data-d="-1" aria-label="Պակասեցնել">−</button>
                                        <output id="cOut">2</output>
                                        <button type="button" class="calc-btn" data-step="out" data-d="1" aria-label="Ավելացնել">+</button>
                                    </div>
                                </div>
                            </div>
                            <p class="small text-muted mt-2 mb-0">Չգիտե՞ս, թե քանիսը։ Թող այսպես, զննման ժամանակ կճշտենք։</p>
                        </div>
                        <div class="calc-q">
                            <h5><span>3</span>Համակարգի տեսակ <a class="calc-help" href="#ipvsanalog">Ո՞րն ընտրել</a></h5>
                            <div class="calc-opts">{systems}
                            </div>
                        </div>
                        <div class="calc-q">
                            <h5><span>4</span>Պատկերի որակ</h5>
                            <div class="calc-opts">{qual}
                            </div>
                        </div>
                        <div class="calc-q">
                            <h5><span>5</span>Քանի՞ օր պահել ձայնագրությունը</h5>
                            <div class="calc-opts">{days}
                            </div>
                        </div>
                        <div class="calc-q mb-0">
                            <h5><span>6</span>Լրացուցիչ</h5>
                            <div class="calc-opts">{extras}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-5">
                    <div class="calc-result" id="form">
                        <h4 class="text-white mb-3">Քո համակարգը</h4>
                        <ul class="calc-list" id="cList"></ul>
                        <p class="calc-note">Սարքավորման ճշգրիտ մոդելն ու գինը կասենք անվճար զննումից հետո։ Մոտավոր հաշվարկ է։</p>
                        <form class="js-quote-form" method="post" action="send.php">
                            <input type="hidden" name="form" value="quote">
                            <input type="hidden" name="service" id="cService">
                            <input type="hidden" name="note" id="cNote">
                            <div class="hp-field" aria-hidden="true"><input name="website" type="text" tabindex="-1" autocomplete="off"></div>
                            <input name="name" type="text" class="form-control mb-2" placeholder="Ձեր անունը" required>
                            <input name="phone" type="tel" class="form-control mb-2" placeholder="Հեռախոսահամար" required>
                            <input name="place" id="cPlace" type="text" class="form-control mb-3" placeholder="Բնակավայր (օր.՝ Երևան, Աշտարակ)">
                            <button class="btn btn-primary w-100 py-3 rounded-pill" type="submit">Ստանալ ճշգրիտ գինը</button>
                        </form>
                        <p class="text-center small mt-3 mb-0">կամ զանգահարեք <a class="text-white fw-medium" href="tel:{phone}">{phone_txt}</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
    (function () {{
        var root = document.getElementById('calc');
        if (!root) return;
        var n = {{ in: 2, out: 2 }};
        var $ = function (s) {{ return root.querySelector(s); }};
        function val(name) {{ var e = root.querySelector('input[name="' + name + '"]:checked'); return e ? e : null; }}
        function render() {{
            document.getElementById('cIn').textContent = n.in;
            document.getElementById('cOut').textContent = n.out;
            var total = n.in + n.out;
            var sys = val('sys');
            var rec = !sys || sys.value === 'unsure' ? 'ձայնագրիչ (NVR կամ DVR՝ կընտրենք միասին)'
                    : sys.value === 'ip' ? 'ձայնագրիչ (NVR)' : 'ձայնագրիչ (DVR)';
            var q = val('q'), days = +(val('days') || {{ value: 14 }}).value;
            var ch = total <= 4 ? 4 : total <= 8 ? 8 : total <= 16 ? 16 : 32;
            // H.265, continuous recording: ~20 GB/day for 4 MP, ~25 GB/day for 5 MP cameras
            var perDay = q && q.value === '5c' ? 25 : 20;
            var tb = total * perDay * days / 1000;
            var disks = [1, 2, 4, 6, 8, 10, 12, 16];
            var disk = disks.find(function (d) {{ return d >= tb; }}) || Math.ceil(tb);
            var extras = Array.prototype.map.call(root.querySelectorAll('input[name="extra"]:checked'), function (e) {{ return e.dataset.label; }});
            var obj = val('obj');
            var lines = [];
            lines.push(['fa-video', total + ' տեսախցիկ' + (total ? ' (' + n.in + ' ներսում, ' + n.out + ' դրսում)' : '')]);
            lines.push(['fa-project-diagram', 'Համակարգ՝ ' + (sys ? sys.dataset.label : '')]);
            lines.push(['fa-image', 'Որակ՝ ' + (q ? q.dataset.label : '')]);
            lines.push(['fa-server', ch + '-ալիքանի ' + rec]);
            lines.push(['fa-hdd', 'Կոշտ սկավառակ՝ ' + disk + ' ՏԲ (' + days + ' օր)']);
            lines.push(['fa-mobile-alt', 'Դիտում հեռախոսից']);
            extras.forEach(function (x) {{ lines.push(['fa-plus', x]); }});
            document.getElementById('cList').innerHTML = lines.map(function (l) {{
                return '<li><i class="fa ' + l[0] + '"></i>' + l[1] + '</li>';
            }}).join('');
            document.getElementById('cService').value = 'Հաշվիչ — ' + (obj ? obj.dataset.label : '') + ', ' + total + ' տեսախցիկ';
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
        var form = root.querySelector('form');
        form.addEventListener('submit', function () {{
            var p = document.getElementById('cPlace').value.trim();
            if (p) document.getElementById('cNote').value += '\\nԲնակավայր: ' + p;
        }});
        render();
    }})();
    </script>
    <!-- Calculator End -->
"""

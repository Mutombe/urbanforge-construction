"""Static page builder for the Urban Forge site.

Pages live in _src/pages/*.html and are written to the project root.
Tokens:
  {{head:Title|Description}}   <head> block
  {{header:page}}              sprite + preloader + header + drawer (page = home|about|services|projects|contact)
  {{footer}}                   footer, to-top button and scripts
  {{lineart}}                  construction skyline line drawing
  {{art:NAME}}                 industry shape for shape cards (ibeam|arches|pipe|blocks|truss|bricks)
  {{zwmap}}                    Zimbabwe operations map
Run:  python _src/build.py
"""
import os, re, itertools

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC = os.path.join(os.path.dirname(__file__), 'pages')
_uid = itertools.count(1)

SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M8 7h9v9"/></symbol>
  <symbol id="i-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16m-6-6 6 6-6 6"/></symbol>
  <symbol id="i-left" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 12H4m6-6-6 6 6 6"/></symbol>
  <symbol id="i-up" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5m-6 6 6-6 6 6"/></symbol>
  <symbol id="i-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></symbol>
  <symbol id="i-grid" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="5" r="2"/><circle cx="12" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="12" cy="19" r="2"/><circle cx="19" cy="19" r="2"/></symbol>
  <symbol id="i-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/></symbol>
  <symbol id="i-mail" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/></symbol>
  <symbol id="i-pin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></symbol>
  <symbol id="i-fb" viewBox="0 0 24 24" fill="currentColor"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H7v4h3v8h4v-8h3l1-4h-4V8.5c0-.3.2-.5.5-.5Z"/></symbol>
  <symbol id="i-ig" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/></symbol>
  <symbol id="i-in" viewBox="0 0 24 24" fill="currentColor"><path d="M4.5 3a2 2 0 1 1 0 4 2 2 0 0 1 0-4ZM3 9h3v12H3zm6 0h3v1.7c.5-.9 1.7-2 3.6-2C19 8.7 20 11 20 14v7h-3v-6.2c0-1.6-.3-3.2-2.2-3.2-1.9 0-2.8 1.3-2.8 3.3V21H9z"/></symbol>
  <symbol id="i-wa" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.3.8 3.2.7.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.2-.2-.5-.3Z"/></symbol>
  <symbol id="i-user" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0Z"/></symbol>
  <symbol id="i-book" viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h7a3 3 0 0 1 1 .2V20a3 3 0 0 0-1-.2H4Zm16 0h-7a3 3 0 0 0-1 .2V20a3 3 0 0 1 1-.2h7Z"/></symbol>
  <!-- line icons for services / values -->
  <symbol id="i-building" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M6 42h36M10 42V14l14-6v34M24 42V18l14 5v19"/><path d="M15 18h4M15 24h4M15 30h4M29 26h4M29 32h4M15 36h4"/><path d="M33 8v8m-4-4h8"/></symbol>
  <symbol id="i-crane" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M10 42V8l-4 6h36M10 8l30 6M14 14 10 18m4-4v28M6 42h14"/><path d="M36 14v10m-3 0h6v4h-6z"/><path d="M26 42V30h14v12"/></symbol>
  <symbol id="i-blueprint" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><rect x="6" y="10" width="36" height="28" rx="2"/><path d="M6 16h6v22M18 16h18v16H24v-8h-6"/><path d="M28 20v4"/></symbol>
  <symbol id="i-land" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"><path d="M4 36 16 24l10 8 6-6 12 10"/><path d="M4 42h40"/><path d="M30 8a5 5 0 0 1 10 0c0 4-5 9-5 9s-5-5-5-9Z"/><circle cx="35" cy="8" r="1.6"/></symbol>
  <symbol id="i-shield" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5Z"/><path d="m8.5 12 2.5 2.5 4.5-5"/></symbol>
  <symbol id="i-hammer" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m14 12-8.5 8.5a2.1 2.1 0 0 1-3-3L11 9"/><path d="M15 13 21 7l-4-4-3 1-4 4 2 2Z"/></symbol>
  <symbol id="i-bulb" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V16h8v-1.3A7 7 0 0 0 12 2Z"/></symbol>
  <symbol id="i-hand" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.9-3.9a3 3 0 0 0-4.2 0l-.9.9a1 1 0 1 1-3-3l2.8-2.8a5 5 0 0 1 6.3-.6l.5.3a2 2 0 0 0 1.4.3H21M3 4h3l6 6"/><path d="m3 13 6 6 2-2"/></symbol>
  <symbol id="i-leaf" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.2-6.1 2.4-.5 4.8-2 5.8-3.9"/></symbol>
  <symbol id="i-target" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></symbol>
</svg>"""

NAV = [('home', 'index.html', 'Home'), ('about', 'about.html', 'About'), ('services', 'services.html', 'Services'),
       ('projects', 'projects.html', 'Projects'), ('contact', 'contact.html', 'Contact')]


def head(title, desc):
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0e1b33">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="assets/img/hero-harare.webp">
<link rel="icon" href="favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600;700&family=Manrope:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">"""


def header(page):
    links = '\n'.join(f'<a href="{href}"{" aria-current=\"page\"" if key == page else ""}>{label}</a>' for key, href, label in NAV)
    drawer_links = '\n'.join(f'<a href="{href}" style="--i:{i}"><span>0{i + 1}</span>{label}</a>' for i, (key, href, label) in enumerate(NAV))
    light = ' header--light' if False else ''
    return f"""{SPRITE}
<a class="sr-only" href="#main">Skip to content</a>
<div class="preloader" aria-hidden="true">
  <div class="preloader__inner">
    <img class="preloader__mark" src="assets/img/mark.png" alt="" width="84" height="84">
    <div class="preloader__bar"><span></span></div>
    <div class="preloader__count">000</div>
  </div>
</div>
<header class="header{light}">
  <div class="container header__inner">
    <div class="nav-pill">
      <a class="brand" href="index.html" aria-label="Urban Forge Construction — home">
        <img class="logo-light" src="assets/img/logo-light.webp" alt="Urban Forge Construction" width="125" height="38">
        <img class="logo-dark" src="assets/img/logo.webp" alt="Urban Forge Construction" width="125" height="38">
      </a>
      <nav class="nav" aria-label="Primary">
{links}
      </nav>
    </div>
    <div class="header__actions">
      <a class="header__phone" href="tel:+263788661056"><svg><use href="#i-phone"/></svg>+263 788 661 056</a>
      <a class="btn" href="contact.html#quote">Get a quote <span class="btn__ic"><svg><use href="#i-arrow"/></svg></span></a>
      <button class="menu-btn" type="button" data-drawer-open aria-controls="drawer" aria-expanded="false" aria-label="Open menu"><svg><use href="#i-grid"/></svg></button>
    </div>
  </div>
</header>
<div class="drawer" id="drawer" aria-hidden="true">
  <div class="drawer__scrim" data-drawer-close></div>
  <div class="drawer__panel" role="dialog" aria-modal="true" aria-label="Menu">
    <div class="drawer__top">
      <img src="assets/img/logo-light.webp" alt="Urban Forge Construction" width="131" height="40">
      <button class="drawer__close" type="button" data-drawer-close aria-label="Close menu"><svg><use href="#i-close"/></svg></button>
    </div>
    <nav class="drawer__nav" aria-label="Menu">
{drawer_links}
    </nav>
    <a class="btn" href="contact.html#quote" style="align-self:flex-start">Request a quote <span class="btn__ic"><svg><use href="#i-arrow"/></svg></span></a>
    <div class="drawer__meta">
      <div><strong>Corporate headquarters</strong>11 Falmouth Road, Alexander Park, Harare</div>
      <div><strong>Talk to the project desk</strong><a href="tel:+263788661056">+263 788 661 056</a> · <a href="mailto:info@urbanforge.co.zw">info@urbanforge.co.zw</a></div>
    </div>
  </div>
</div>"""


FOOTER = """<footer class="footer">
  <div class="footer__bg"><img src="assets/img/apex-tower.webp" alt="" loading="lazy"></div>
  <div class="footer__word" aria-hidden="true">urbanforge</div>
  <div class="container">
    <div class="footer__news">
      <div>
        <h2>Build with the forge</h2>
        <p>Project updates, development opportunities and site news from across Zimbabwe.</p>
      </div>
      <form class="news-form" data-mailto="newsletter">
        <label class="sr-only" for="news-email">Email address</label>
        <input id="news-email" type="email" name="email" placeholder="Enter your email address" required>
        <button class="btn" type="submit">Subscribe <span class="btn__ic"><svg><use href="#i-arrow"/></svg></span></button>
      </form>
    </div>
    <div class="footer__grid">
      <div class="footer__brand">
        <img src="assets/img/logo-light.webp" alt="Urban Forge Construction" width="171" height="52" loading="lazy">
        <p>Forging the future of Zimbabwe's real estate landscape with authoritative scale and uncompromising quality.</p>
        <div class="footer__social">Follow us:
          <a href="https://www.facebook.com/" aria-label="Facebook" rel="noopener"><svg><use href="#i-fb"/></svg></a>
          <a href="https://www.linkedin.com/" aria-label="LinkedIn" rel="noopener"><svg><use href="#i-in"/></svg></a>
          <a href="https://www.instagram.com/" aria-label="Instagram" rel="noopener"><svg><use href="#i-ig"/></svg></a>
          <a href="https://wa.me/263788661056" aria-label="WhatsApp" rel="noopener"><svg><use href="#i-wa"/></svg></a>
        </div>
      </div>
      <div>
        <h4>Services</h4>
        <ul>
          <li><a href="services.html#property">Property Development</a></li>
          <li><a href="services.html#construction">Construction Services</a></li>
          <li><a href="services.html#management">Project Management</a></li>
          <li><a href="services.html#land">Land Development</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About us</a></li>
          <li><a href="projects.html">Projects</a></li>
          <li><a href="about.html#values">Our values</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Headquarters</h4>
        <address>11 Falmouth Road,<br>Alexander Park, Harare,<br>Zimbabwe<br><a href="tel:+263788661056">+263 788 661 056</a><br><a href="mailto:info@urbanforge.co.zw">info@urbanforge.co.zw</a></address>
      </div>
    </div>
    <div class="footer__bar">
      <span>© <span data-year>2026</span> Urban Forge Construction. All rights reserved.</span>
      <nav aria-label="Legal"><a href="contact.html">Privacy Policy</a><a href="contact.html">Terms of Service</a></nav>
    </div>
  </div>
</footer>
<button class="to-top" type="button" aria-label="Back to top"><svg viewBox="0 0 54 54" aria-hidden="true"><circle cx="27" cy="27" r="24"/></svg><i><svg style="position:static;transform:none;width:16px;height:16px"><use href="#i-up"/></svg></i></button>
<script src="assets/js/main.js" defer></script>"""

# construction skyline drawn in single-weight lines (cranes, frames, excavator, tower)
LINEART = """<svg viewBox="0 0 1440 260" preserveAspectRatio="xMidYMax slice" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" aria-hidden="true">
  <path d="M0 252h1440"/>
  <!-- tower crane left -->
  <path d="M120 252V40m10 212V40M120 40h10M120 60l10-20M120 80l10-20M120 100l10-20M120 120l10-20M120 140l10-20M120 160l10-20M120 180l10-20M120 200l10-20M120 220l10-20M120 240l10-20"/>
  <path d="M60 40h300M60 30h300M125 40V10M125 10 60 30m65-20 235 20M90 30v10m30-10v10m40-10v10m40-10v10m40-10v10m40-10v10m40-10v10m40-10v10"/>
  <path d="M300 40v90m-8 0h16v14h-16zM62 40v24h30V40"/>
  <!-- building frame under construction -->
  <path d="M190 252V130h160v122M190 160h160M190 190h160M190 220h160M230 130v122M270 130v122M310 130v122M190 130l40 30m0-30 40 30m0-30 40 30m0-30 40 30"/>
  <!-- finished tower -->
  <path d="M420 252V70h90v182M420 90h90M440 110h12m14 0h12m14 0h12M440 135h12m14 0h12m14 0h12M440 160h12m14 0h12m14 0h12M440 185h12m14 0h12m14 0h12M440 210h12m14 0h12m14 0h12M455 252v-22h20v22"/>
  <!-- excavator -->
  <path d="M580 252h120M590 252a14 14 0 0 1 0-28h100a14 14 0 0 1 0 28M600 224v-34h50l14 34M612 196h26v18h-26zM664 200l40-50 36 30M740 180l8 30-22 6"/>
  <!-- low rise + scaffold -->
  <path d="M780 252V150h140v102M780 150l70-40 70 40M800 175h22v22h-22zm40 0h22v22h-22zm40 0h22v22h-22zM835 252v-36h30v36"/>
  <path d="M930 252V120m40 132V120m-40 20h40m-40 30h40m-40 30h40m-40 30h40M930 140l40 30m-40 0 40 30m-40 0 40 30"/>
  <!-- tower crane right -->
  <path d="M1110 252V30m12 222V30M1110 30h12M1110 50l12-20M1110 70l12-20M1110 90l12-20M1110 110l12-20M1110 130l12-20M1110 150l12-20M1110 170l12-20M1110 190l12-20M1110 210l12-20M1110 230l12-20"/>
  <path d="M990 30h380M990 20h380M1116 30V0M1116 0 990 20m126-20 254 20M1300 30v70m-8 0h16v14h-16z"/>
  <!-- mid rise -->
  <path d="M1180 252V110h120v142M1180 130h120M1180 160h120M1180 190h120M1180 220h120M1210 110v142M1240 110v142M1270 110v142"/>
  <path d="M1320 252V170h100v82M1340 190h20v20h-20zm40 0h20v20h-20zM1355 252v-26h30v26"/>
  <!-- traffic cones -->
  <path d="M560 252l8-26 8 26m-12-12h8M730 252l8-26 8 26m-12-12h8"/>
</svg>"""


def art(kind):
    """Industry shapes for shape cards (Teamway-style), monochrome gradients tinted by --ink-tone."""
    u = next(_uid)
    g = f"""<defs>
      <linearGradient id="a{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="var(--ink-tone)" stop-opacity=".05"/><stop offset="1" stop-color="var(--ink-tone)" stop-opacity=".85"/></linearGradient>
      <linearGradient id="b{u}" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--ink-tone)" stop-opacity=".9"/><stop offset="1" stop-color="var(--ink-tone)" stop-opacity=".08"/></linearGradient>
      <radialGradient id="c{u}" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="var(--ink-tone)" stop-opacity=".35"/><stop offset="1" stop-color="var(--ink-tone)" stop-opacity=".9"/></radialGradient>
    </defs>"""
    A, B, C = f'url(#a{u})', f'url(#b{u})', f'url(#c{u})'
    shapes = {
        # stacked steel I-beam profiles
        'ibeam': f"""<path d="M30 20h150v34h-55v52h55v34H30v-34h55V54H30z" fill="{A}"/>
                     <path d="M120 170h150v34h-55v52h55v34H120v-34h55v-52h-55z" fill="{B}"/>
                     <path d="M30 320h150v34h-55v52h55v34H30v-34h55v-52H30z" fill="{A}" opacity=".7"/>""",
        # brick arches / culverts
        'arches': f"""<circle cx="180" cy="90" r="80" fill="{C}"/>
                      <path d="M40 260a90 90 0 0 1 180 0z" fill="{A}"/><path d="M40 270a90 90 0 0 0 180 0z" fill="{B}" opacity=".7"/>
                      <path d="M200 380a90 90 0 0 1 180 0z" fill="{A}" opacity=".8"/><circle cx="300" cy="200" r="70" fill="{C}" opacity=".85"/>""",
        # pipe cross-sections / survey target
        'pipe': f"""<ellipse cx="200" cy="220" rx="190" ry="150" fill="{C}"/>
                    <ellipse cx="215" cy="220" rx="120" ry="100" fill="{A}"/>
                    <ellipse cx="225" cy="220" rx="70" ry="62" fill="{C}"/>
                    <circle cx="232" cy="220" r="26" fill="{B}"/>""",
        # building massing blocks (stepped)
        'blocks': f"""<rect x="60" y="20" width="120" height="120" rx="10" fill="{A}"/>
                      <rect x="180" y="140" width="160" height="120" rx="10" fill="{B}"/>
                      <rect x="60" y="260" width="120" height="140" rx="10" fill="{A}"/>
                      <rect x="200" y="300" width="120" height="100" rx="10" fill="{C}" opacity=".7"/>""",
        # crane jib lattice truss
        'truss': f"""<path d="M0 120h400v40H0z" fill="{A}"/>
                     <path d="M20 160l40 120 40-120 40 120 40-120 40 120 40-120 40 120 40-120 40 120 40-120" stroke="var(--ink-tone)" stroke-opacity=".5" stroke-width="10" fill="none" stroke-linejoin="round"/>
                     <path d="M0 280h400v40H0z" fill="{B}"/>
                     <path d="M260 20l60 100h-120z" fill="{C}"/>""",
        # staggered bricks
        'bricks': f"""<rect x="40" y="40" width="160" height="70" rx="14" fill="{A}"/><rect x="210" y="40" width="160" height="70" rx="14" fill="{B}"/>
                      <rect x="120" y="120" width="160" height="70" rx="14" fill="{C}"/><rect x="290" y="120" width="160" height="70" rx="14" fill="{A}" opacity=".7"/>
                      <rect x="40" y="200" width="160" height="70" rx="14" fill="{B}"/><rect x="210" y="200" width="160" height="70" rx="14" fill="{A}"/>
                      <rect x="120" y="280" width="160" height="70" rx="14" fill="{A}" opacity=".6"/><rect x="290" y="280" width="160" height="70" rx="14" fill="{C}"/>""",
    }
    return f'<div class="shape-card__art" aria-hidden="true"><svg viewBox="0 0 400 440" preserveAspectRatio="xMaxYMid meet">{g}{shapes[kind]}</svg></div>'


ZW_PATH = "M26 239 L70 242 L86 253 L125 253 L170 255 L210 240 L250 200 L290 170 L330 140 L376 112 L385 63 L440 35 L500 25 L542 23 L617 46 L664 80 L722 104 L770 129 L798 131 L785 180 L795 220 L800 260 L795 290 L770 340 L772 360 L785 385 L780 430 L805 460 L790 500 L765 520 L750 570 L737 593 L690 645 L630 702 L590 690 L540 693 L498 682 L455 675 L435 679 L405 655 L375 625 L302 608 L272 545 L270 510 L230 507 L210 465 L160 425 L117 415 L95 355 L65 315 L50 280 Z"

ZWMAP = f"""<div class="zw-map" data-reveal="zoom">
  <svg viewBox="-10 -10 840 740" role="img" aria-labelledby="zwmap-t">
    <title id="zwmap-t">Map of Zimbabwe showing Urban Forge's headquarters in Harare and operations in Mutare and Bulawayo</title>
    <defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0v10" stroke="#1a3460" stroke-opacity=".07" stroke-width="3"/></pattern></defs>
    <path class="land" d="{ZW_PATH}"/>
    <path class="land-hatch" d="{ZW_PATH}"/>
    <path class="route" d="M605 243 Q 700 270 767 357"/>
    <path class="route" d="M605 243 Q 470 330 358 475"/>
    <path class="route" d="M358 475 Q 590 520 767 357" style="opacity:.45"/>
    <g class="pin hq" data-city="harare" tabindex="0" data-tip="Harare|Headquarters · Alexander Park"><circle class="pulse" cx="605" cy="243" r="14"/><circle class="core" cx="605" cy="243" r="12"/><text x="628" y="234">Harare</text><text class="sub" x="628" y="258">Headquarters</text></g>
    <g class="pin" data-city="mutare" tabindex="0" data-tip="Mutare|Mixed-use &amp; land development"><circle class="pulse" cx="767" cy="357" r="10" style="animation-delay:.8s"/><circle class="core" cx="767" cy="357" r="11"/><text x="680" y="400">Mutare</text></g>
    <g class="pin" data-city="bulawayo" tabindex="0" data-tip="Bulawayo|Commercial construction"><circle class="pulse" cx="358" cy="475" r="10" style="animation-delay:1.6s"/><circle class="core" cx="358" cy="475" r="11"/><text x="382" y="468">Bulawayo</text></g>
  </svg>
</div>"""


def build():
    for fn in sorted(os.listdir(SRC)):
        src = open(os.path.join(SRC, fn), encoding='utf8').read()
        src = re.sub(r'\{\{head:([^|}]+)\|([^}]+)\}\}', lambda m: head(m.group(1), m.group(2)), src)
        src = re.sub(r'\{\{header:(\w+)\}\}', lambda m: header(m.group(1)), src)
        src = re.sub(r'\{\{art:(\w+)\}\}', lambda m: art(m.group(1)), src)
        src = src.replace('{{footer}}', FOOTER).replace('{{lineart}}', LINEART).replace('{{zwmap}}', ZWMAP)
        left = re.findall(r'\{\{[^}]+\}\}', src)
        assert not left, f'{fn}: unresolved tokens {left}'
        open(os.path.join(ROOT, fn), 'w', encoding='utf8', newline='\n').write(src)
        print('built', fn)


if __name__ == '__main__':
    build()

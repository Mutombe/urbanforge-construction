# Urban Forge Construction — website

Static, dependency-free site (HTML + CSS + vanilla JS). Open `index.html` directly or serve the folder
(`python -m http.server`) and deploy the folder as-is to any static host.

## Pages
| File | Contents |
|---|---|
| `index.html` | Hero slider + typed services, about intro, services slider, "what makes us different" bento, 3D glass band, project polaroids, promise card over aerial, crews, client marquee, tapes, FAQ, contact, insights |
| `about.html` | Story, stats, glass mission/vision, industry-shape value cards, Zimbabwe map, clients |
| `services.html` | Four service rows (with 3D objects), process timeline + gallery, "who we build for" shape cards |
| `projects.html` | Filterable portfolio, charts (by project / sector / city), map, field gallery + lightbox |
| `contact.html` | Quote form, contact details, Google map, Zimbabwe map, starting-point cards |

## Editing
Edit the sources in `_src/pages/*.html`, then rebuild with `python _src/build.py`. The build injects shared
partials (header, drawer, footer, icon sprite, line-art skyline, shape-card art, Zimbabwe map), all defined
in `_src/build.py`. Do not edit the root `*.html` files directly; they are overwritten.

## Brand tokens (`assets/css/style.css`, `:root`)
- Navy `--navy #1a3460` (from the logo's "Urban"), deep `--navy-950 #0a1426`
- Forge orange `--forge #d56b43` (from the logo's "Forge")
- Steel neutrals `--steel-*`, paper `#f6f6f4`
- Type: Lexend (display), Manrope (body), JetBrains Mono (labels)

## Assets
- `python _src/tools/build_assets.py <urban_folder> <old_site_images>` converts the source photos and logos to WebP in `assets/img/`.
- `python _src/tools/render3d.py [nut ibeam cone gear globe]` ray-marches the 3D brand objects
  (`assets/img/obj-*.webp`). Each object is a signed distance function, with forge-orange metal, navy lacquer,
  a reflective white band and pearl-globe materials, plus a studio environment, 4 lights, Fresnel, AO and tone mapping.
  Poses and scales are in the `OBJECTS` table, and the palette is at the top of the file.

## Before going live
1. **iStock images are watermarked comps.** `cranes-sky`, `timber-frame`, `roof-framing`, `engineer-plans`,
   `team-site-review`, `excavator-loading` and `residence-finished` show the iStock watermark. License them and
   overwrite the files with the same names (re-run `build_assets.py`), or replace them with your own site photos.
2. **Forms** open the visitor's email app with the enquiry pre-filled (to info@urbanforge.co.zw). To submit
   silently, point the forms at a form service (e.g. Formspree) or your backend.
3. **Confirm the facts**: the stats (USD 5M+, 50+ projects, 100% satisfaction), the project values and the
   ISO 9001 / SAZ registration come from the old site and the supplied assets. The old site also showed a
   "$75M" stat that contradicts its own "over USD $5 million" copy; this site uses USD 5M+.
4. Add real social profile URLs (footer and hero rail currently link to the platform home pages).

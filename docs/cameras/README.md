# Manufacturer camera screens (work in progress, branch `cameras`)

How it works
- The game already renders live cameras from each car's own positions (rear, front, sides, overhead) into small off-screen images.
  `rcDraw()` (in `src/app_template.html`, search `v340 manufacturer camera screens`) takes over the centre screen whenever the camera
  page is up (shifting into R brings it up) and draws the brand's own layout over those live images.
- `RC_MAP[brand](trim, modelYear)` picks the screen generation; `RC_STYLES[id]` holds the layout, guide-line spec and buttons.
- Guide lines are projected onto the ground with the same camera matrix the picture was rendered with, so they line up with the
  car's real width and turn with the front wheels (`rcLines`). The overhead view is a real render from above the car, cropped to the
  panel; the car graphic is drawn over it because real systems can't see the car (`rcCarTop`). Parking-sensor zones come from the
  game's existing sensors (`sys.pdc`).
- Views offered per car = what the car really has in the game data: rear always; overhead/side only with a 360 camera (`has360()`);
  front only with a front camera (`hasFrontCam()`); wide views on systems that document them.
- Performance: nothing extra renders unless the camera page is open in the cockpit view; the overhead and main views share the
  existing alternate-frame render (`G().camEvery`), 480x288 each.

Confidence key: VERIFIED = from the maker's manual / support page; LIKELY = consistent with manuals but a detail (colour, position)
not stated; UNVERIFIED = not found, left out or kept minimal.

## Group 1: Toyota / Lexus / Mazda (done)
| Screen id | Cars (by model year) | Layout | Lines | Confidence |
|---|---|---|---|---|
| `toy_e3` | Toyota up to MY2022 (Entune 3.0 era: RAV4 2018/2019, Camry 2022, Highlander 2019, 4Runner 2022, Sienna, Sequoia 2021, Corolla iM, Prius 2020, Land Cruiser 2021, C-HR 2021) | Rear view monitor full screen; panoramic view beside it when fitted; guide-line and view buttons bottom right | width lines, centre line, red 0.5 m, blue 1 m (manual); width-line colour not stated -> green | VERIFIED lines/distances; LIKELY colours/buttons |
| `toy_tam` | Toyota MY2023 on (Toyota Audio Multimedia: Camry 2025, RAV4 2026, Tacoma, Tundra, Grand Highlander, Sequoia, Land Cruiser, 4Runner 2026, bZ, Crown Signia, C-HR 2027, Corolla, Prius, Sienna 2026) | overhead left, camera right, pill buttons for each view along the bottom | yellow estimated course lines that turn with the wheel, red 0.5 m, blue width lines in wide view | LIKELY (layout from Toyota's PVM manuals; exact button art original) |
| `lex_li` | Lexus MY2022 on (Lexus Interface, 14-inch: NX, RX, TX, LX, GX, RZ, UX, TZ) | overhead + camera, slim icon strip right, "Check surroundings for safety." | as `toy_tam` | LIKELY |
| `lex_old` | Lexus up to MY2021 (Remote Touch / Enform: NX 2020, RX 2021, GX 2022, LX 2020) | camera full screen, grey square buttons along the bottom | as `toy_e3` | LIKELY |
| `mazda_mc` | Mazda 2026 range (Mazda Connect, commander knob) | knob selection list left, overhead (tyre icons) + camera, view status icon | amber projected path lines (turn with wheel), red 0.5 m, amber 1 m and 2 m; wide views: red to 0.5 m then blue extended width lines to 2 m; path also drawn on the overhead | VERIFIED (Mazda manuals) |

Mazda views per manual: top+front, top+front wide, side, top+rear, top+rear wide (implemented); See-Through View and Trailer Hitch
View exist on some trims (not implemented: no per-trim evidence in the game data yet).

Sources
- Mazda USA owner's manuals, "How to Use the 360° View Monitor": 2026 CX-90 https://www.mazdausa.com/static/manuals/2026/cx-90/contents/65550300.html ,
  2026 CX-70 https://www.mazdausa.com/static/manuals/2026/cx-70/contents/1653808267.html , 2026 Mazda3 https://www.mazdausa.com/static/manuals/2026/mazda3/contents/65550300.html
- Mazda CX-8 "Top View/Rear View" (line colours and distances): https://owners-manual.mazda.com/gen/en/cx-8/cx-8_8hh9eo19a/contents/05283007.html
- Toyota rear view monitor guide lines (red 0.5 m, blue 1 m, width and centre lines): Tundra https://www.manualslib.com/manual/1407350/Toyota-Tundra.html?page=278 ,
  Camry https://www.manualslib.com/manual/967439/Toyota-Camry.html?page=209
- 2019 RAV4 owner's manual, panoramic view monitor: https://manualslib.com/manual/1780848/Toyota-Rav-4-2019.html?page=334
- Toyota multimedia owner's manuals index (Audio Multimedia): https://assets.sia.toyota.com/publications/en/omnav-s/OM06269U/pdf/OM06269U.pdf

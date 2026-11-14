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

## Group 2+: every other brand (done)
All built with `rcMake()` (one factory, each brand's own layout, button strip position and style, colours, safety text and lines).

| Screen id | Cars | Layout | Lines (colours) | Confidence |
|---|---|---|---|---|
| `ford_s3` | Ford / Lincoln to MY2020 (SYNC 3) | camera full, soft keys bottom | fixed lines green / yellow / red zones, active guidelines, centerline | VERIFIED line types (Ford support page); zone distances UNVERIFIED |
| `ford_s4` | Ford MY2021 on (SYNC 4 / 4A) | overhead left, icon buttons bottom, settings cog | as above | LIKELY layout |
| `lincoln` | Lincoln MY2021 on | overhead left, view strip right | as above | LIKELY |
| `gm` | Chevrolet / GMC / Buick | overhead beside camera, view bar bottom | amber guidelines turning with the wheel, distance marks | VERIFIED views (Chevrolet Surround Vision page); colours LIKELY |
| `cadillac` | Cadillac | views in a left column | as `gm` | LIKELY |
| `stla` | Jeep / Ram / Dodge / Chrysler | camera + overhead, X (close) and zoom buttons, "Check Entire Surroundings" for 5 s, More Cams | red 0-1 ft, yellow 1-6.5 ft, green beyond (Ram manual) | VERIFIED distances/text |
| `hyk` / `genesis` | Hyundai, Kia / Genesis | view column left, settings cog | red / yellow / green distance lines, path turns with the wheel | VERIFIED behaviour (Hyundai manual); colours LIKELY |
| `honda` / `acura` | Honda / Acura | Normal / Wide / Top Down, view name on screen, sensor graphic | fixed guidelines red / yellow / green, dynamic guidelines | VERIFIED views (Honda manual); colours LIKELY |
| `nissan` / `infiniti` | Nissan / Infiniti | camera left, bird's-eye right, "Check entire surroundings." | red 0.5 m, yellow 1 m, green 2 m and 3 m; green width lines; yellow predictive course | VERIFIED distances (Nissan manual) |
| `subaru`, `vw`, `audi`, `porsche`, `bmw`, `merc`, `volvo`, `jlr`, `rivian`, `lucid` | those brands | each its own arrangement | see `RCL` in code | LIKELY (from general knowledge of each system; no manual fetched) |

Not changed: Tesla keeps its existing camera screen; concept cars, work trucks and pre-2012 cars without cameras keep the generic screen.

## Parking sensors (`pdcKit()`)
Every car used to have front and rear sensors. Now: 360 camera -> front and rear; premium brands -> front and rear; mainstream cars -> none on the
cheapest third of the model's trims, then front and rear for Toyota / Honda / Hyundai / Kia / Mazda / VW, rear only for GM / Ford / Stellantis /
Nissan / Subaru (front too on the top trim); 2011 and older -> none (premium: rear, 5/7 Series front too); Tesla -> camera-based (Tesla Vision)
distances. This is a rule, not a per-trim spec lookup: individual trims may differ (UNVERIFIED per trim).

Sources (group 2): Ford rear view camera https://www.ford.ca/support/how-tos/ford-technology/driver-assist-features/rear-view-camera/ ;
Chevrolet Surround Vision https://www.chevrolet.com/support/vehicle/driving-safety/mirrors-and-cameras/surround-vision ;
Ram 2022 Surround View Camera https://vehicleinfo.mopar.com/assets/publications/en-us/Ram/2022/2500_3500/om_html/GUID-7F83E962-52CD-46D8-9C86-FF4C39D1E9A5.html ;
Hyundai Parking Assistance screen https://ownersmanual.hyundai.com/ivi/ccNC_Lite/AV/MEX/English/Cameraview_rvm.html ;
Honda Multi View Camera System https://techinfo.honda.com/rjanisis/pubs/OM/AH/A3BM2626IOM/enu/details/66333ff6c65dd9-62000111.html ;
Nissan Juke 2024 front and rear view https://www.nissan.ie/ownership/car-owner-manual/manuals/iom/juke/0f16/e1/2024/front-and-rearview-1.shtml

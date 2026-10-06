# Stitch screens → Recall app

Flow order. `screen.png` = visual target, `code.html` = read tokens/copy only (don't port).

| Folder | What it shows | App location |
|---|---|---|
| 00_design_system/DESIGN.md | Colours, type, radius tokens ("Warm Editorial Memory") | `.streamlit/config.toml` + `recall/ui.py` |
| 01_home | Photos-style library grid by month, search bar, "Help me remember" chip | `app.py` landing |
| 02_search_flooded | "212 photos found" for a broad search + "Can't find it?" card | `app.py` after keyword search |
| 03_describe_it | Free-text "Describe it" → "We understood" editable cue chips | `app.py` Describe box (M4) |
| 04_step1_when | Step 1/4 When: life chapters, years, era text box | guided step 1 |
| 05_step2_who | Step 2/4 Who: people chips, Just me / A group / Not sure | guided step 2 |
| 06_step3_where | Step 3/4 Where: city → place list with counts | guided step 3 |
| 07_step4_what | Step 4/4 What: Type chips + event list + "Anything else?" | guided step 4 |
| 08_results | "Is it one of these?" 3–5 moment cards (MAIN results design) | results |
| 09_moment_view | Moment grid, This is the photo / Not it, Timeline context (before/after) | moment view |
| 10_found_it | Success: time, retrieval path, Try another task | success state |
| 11_how_it_works | Evaluator explainer + "Where AI is used" | `pages/1_How_it_works.py` |
| alt_results_large_cards | Alternative results layout with big cards | reference only |
| alt_all_filters_one_page | All facets on one page | reference for an "Edit all filters" view |
| _assets/ | Two AI mood images from Stitch | NOT library photos; don't use in the app |

## Fix while adapting (Stitch placeholders)
- App name: use **Recall** everywhere (several screens say "Memory Cue Inspector").
- Use real data from `data/index.json` / `chapters.csv` / `people.csv`, never mock values
  (e.g. "Manipal University", "3,420 photos", "Sony Alpha", "RAW").
- Don't show invented metrics ("Recall Match 99.4%", "96% sensory match", "6.6x faster",
  "4m 12s scroll"). Show only measured ones: elapsed time, steps, photos narrowed.
- No Google/Google Photos logos or wordmarks; keep "Demo library · AI-generated and stock images".

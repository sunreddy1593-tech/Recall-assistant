import os
import pandas as pd
from PIL import Image, ImageDraw, ImageText

# 1. Chapters
chapters = [
    {"name": "School · boy-cut era", "start": "2012-06-01", "end": "2015-05-31", "aliases": "boy cut;short hair;middle school"},
    {"name": "College", "start": "2018-07-01", "end": "2022-05-31", "aliases": "college;engineering;hostel"},
    {"name": "Masters in Scotland", "start": "2023-09-01", "end": "2024-08-31", "aliases": "scotland;edinburgh;uni abroad"},
    {"name": "Working in Ireland", "start": "2025-01-01", "end": "2026-12-31", "aliases": "ireland;dublin;first job"}
]

os.makedirs("library/photos", exist_ok=True)
pd.DataFrame(chapters).to_csv("library/chapters.csv", index=False)

# 2. Manifest data covering the 6 scenarios
photos = []
scenarios = [
    # Scenario 1: Scotland, face mask, home
    ("scotland_mask.jpg", "2024-03-10T14:30:00", 55.9533, -3.1883, "Home in Edinburgh", "Just me", "scotland face mask", (255, 100, 100)),
    ("scotland_distractor1.jpg", "2024-03-12T10:00:00", 55.9533, -3.1883, "University", "Friends", "uni", (200, 100, 100)),
    
    # Scenario 2: Ireland fast food uniform, ~2025
    ("ireland_job.jpg", "2025-06-15T18:00:00", 53.3498, -6.2603, "McDonalds Dublin", "Just me", "uniform at work", (100, 255, 100)),
    ("ireland_distractor.jpg", "2025-06-20T19:00:00", 53.3498, -6.2603, "Pub", "Friends", "pub", (100, 200, 100)),

    # Scenario 3: Birthday with college friends, Feb 2019 or 2020, 3 places in one evening
    ("bday_2019_p1.jpg", "2019-02-14T19:00:00", 18.5204, 73.8567, "Dinner Place", "Ananya; Rhea; Kabir", "dinner", (100, 100, 255)),
    ("bday_2019_p2.jpg", "2019-02-14T21:30:00", 18.5204, 73.8567, "Club", "Ananya; Rhea; Kabir", "club", (150, 100, 255)),
    ("bday_2019_p3.jpg", "2019-02-14T23:45:00", 18.5204, 73.8567, "Street Food", "Ananya; Rhea; Kabir", "late night", (200, 100, 255)),
    ("bday_2020.jpg", "2020-02-14T20:00:00", 18.5204, 73.8567, "House Party", "Ananya; Rhea; Kabir", "2020 bday", (100, 150, 255)),

    # Scenario 4: Sibling school award, 7th grade, before COVID (e.g. 2019)
    ("sibling_award.jpg", "2018-10-10T10:00:00", 28.7041, 77.1025, "School Auditorium", "Rahul (Brother); Parents", "award", (255, 255, 100)),
    ("sibling_distractor.jpg", "2018-12-25T11:00:00", 28.7041, 77.1025, "Home", "Rahul (Brother)", "christmas", (200, 255, 100)),

    # Scenario 5: Small café in Goa, year unknown
    ("goa_cafe.jpg", "2021-11-05T13:00:00", 15.5527, 73.7517, "Café Bodega, Panjim", "Ananya; Kabir", "goa cafe", (255, 100, 255)),
    ("goa_distractor.jpg", "2021-11-06T17:00:00", 15.5527, 73.7517, "Beach", "Ananya; Kabir", "goa beach", (200, 100, 255)),
    ("goa_cafe_old.jpg", "2018-12-15T14:00:00", 15.5527, 73.7517, "Eva Cafe", "Rhea", "old goa trip", (255, 150, 255)),

    # Scenario 6: Screenshot of a bill, sometime last year (2025)
    ("bill_screenshot.jpg", "2025-08-10T10:00:00", None, None, None, None, "electricity bill screenshot", (100, 255, 255)),
    ("meme_screenshot.jpg", "2025-08-12T11:00:00", None, None, None, None, "meme screenshot", (100, 200, 255)),
    ("flight_screenshot.jpg", "2025-09-01T15:00:00", None, None, None, None, "flight ticket screenshot", (100, 255, 200)),
]

manifest = []
for filename, taken_at, lat, lon, place, people, text, color in scenarios:
    manifest.append({
        "filename": filename,
        "taken_at": taken_at,
        "lat": lat,
        "lon": lon,
        "place_override": place,
        "people": people,
        "notes": text
    })
    
    # Generate simple image
    img = Image.new('RGB', (400, 300), color=color)
    d = ImageDraw.Draw(img)
    d.text((20, 140), text, fill=(0,0,0))
    img.save(f"library/photos/{filename}")

pd.DataFrame(manifest).to_csv("library/manifest.csv", index=False)
print("Generated placeholder data successfully.")

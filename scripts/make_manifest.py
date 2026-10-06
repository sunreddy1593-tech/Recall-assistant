import os
import glob
import pandas as pd
import random
from datetime import datetime, timedelta

def get_coords(place):
    lookup = {
        'Hyderabad': (17.3850, 78.4867),
        'Pune-Koregaon-Park': (18.5362, 73.8939),
        'Pune-FC-Road': (18.5195, 73.8427),
        'Pune-Viman-Nagar': (18.5684, 73.9137),
        'Pune': (18.5204, 73.8567),
        'Goa-Panjim': (15.4909, 73.8278),
        'Goa-Anjuna': (15.5908, 73.7431),
        'Coorg': (12.3375, 75.8069),
        'Bengaluru': (12.9716, 77.5946),
        'Bengaluru-Koramangala': (12.9279, 77.6271),
        'Bengaluru-Indiranagar': (12.9784, 77.6408),
        'Bengaluru-Whitefield': (12.9698, 77.7499),
        'Edinburgh': (55.9533, -3.1883),
        'Edinburgh-Portobello': (55.9536, -3.1118),
        'Isle-of-Skye': (57.3225, -6.1557),
        'Dublin': (53.3498, -6.2603),
        'Dublin-Temple-Bar': (53.3455, -6.2642),
        'Howth': (53.3850, -6.0645),
        'Galway': (53.2707, -9.0568),
        'Cork': (51.8985, -8.4756)
    }
    return lookup.get(place, (None, None))

def main():
    photos_dir = "library/photos"
    manifest_rows = []
    
    people_df = pd.DataFrame()
    if os.path.exists("library/people.csv"):
        people_df = pd.read_csv("library/people.csv")
        people_df = people_df.set_index('filename')

    for root, dirs, files in os.walk(photos_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                folder_name = os.path.basename(root)
                rel_path = f"{folder_name}/{file}"
                
                # Default values
                taken_at = None
                lat, lon = None, None
                place_override = None
                
                # Parse folder name YYYY-MM-DD_Place
                if '_' in folder_name:
                    date_str, place = folder_name.split('_', 1)
                    try:
                        base_date = datetime.strptime(date_str, "%Y-%m-%d")
                        # Add random time
                        random_hour = random.randint(8, 22)
                        random_minute = random.randint(0, 59)
                        random_second = random.randint(0, 59)
                        taken_at_dt = base_date + timedelta(hours=random_hour, minutes=random_minute, seconds=random_second)
                        taken_at = taken_at_dt.strftime("%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        print(f"Skipping date parsing for {folder_name}")
                    
                    if place != "NoLocation":
                        lat, lon = get_coords(place)
                        # The spec says "place_override: optional venue name shown in Where"
                        # We could leave place_override blank to let reverse geocoding find City,
                        # or set place_override to the folder place if we want to bypass geocoding.
                        # Wait, the spec says "if place_override -> use it as venue. Else reverse-geocode".
                        # Let's set it as place_override to get nice names like "Koregaon Park, Pune" etc. 
                        # Actually let's just use it as place_override to be safe, replacing hyphens.
                        place_override = place.replace('-', ' ')
                
                people_val = ""
                if not people_df.empty and rel_path in people_df.index:
                    people_val = people_df.loc[rel_path, 'people']
                    if isinstance(people_val, pd.Series):
                        people_val = people_val.iloc[0]
                
                manifest_rows.append({
                    'filename': rel_path,
                    'taken_at': taken_at,
                    'lat': lat,
                    'lon': lon,
                    'place_override': place_override,
                    'people': people_val,
                    'notes': ""
                })
                
    df = pd.DataFrame(manifest_rows)
    df.to_csv("library/manifest.csv", index=False)
    print(f"Generated library/manifest.csv with {len(df)} rows.")

if __name__ == '__main__':
    main()

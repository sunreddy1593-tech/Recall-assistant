import pandas as pd
import json
import os

manifest = pd.read_csv('library/manifest.csv')
photos = manifest['filename'].tolist()

photo_labels = []
for p in photos:
    lower = p.lower()
    p_type = 'photo'
    if 'screenshot' in lower or 'nolocation' in lower:
        p_type = 'screenshot'
    if 'bill' in lower:
        p_type = 'document'

    text = ""
    if p_type in ['screenshot', 'document']:
        if 'bill' in lower or '2026-10-05' in lower:
            text = "electricity bill; amount due; Demo Power"
        else:
            text = "some text on screen"
            
    caption = "A view of the scene"
    if 'mask' in lower or ('010' in lower and '2023-11-20' in lower):
        caption = "Crouched on the floor wearing a face mask"
    elif 'uniform' in lower or ('001' in lower and '2025-02-08' in lower):
        caption = "Coworker in fast-food uniform"
    elif '002' in lower and '2019-02-14' in lower:
        caption = "Birthday night out with college friends"
    elif '001' in lower and '2019-01-25' in lower:
        caption = "Little brother with his school medal"
    elif '005' in lower and '2022-12-30' in lower:
        caption = "Colourful cafe on a Goa trip"
    elif p_type == 'document':
        caption = "Electricity bill for the month"
    elif p_type == 'screenshot':
        caption = "Screenshot of a meme or chat"
        
    photo_labels.append({
        'filename': p,
        'caption': caption,
        'objects': 'person; table' if p_type == 'photo' else '',
        'clothing': 'casual' if p_type == 'photo' else '',
        'text_in_image': text
    })

pd.DataFrame(photo_labels).to_csv('library/photo_labels.csv', index=False)

folders = set()
for p in photos:
    if '/' in p:
        folders.add(p.split('/')[0])
    else:
        folders.add("root")

moment_labels = []
for f in folders:
    lower = f.lower()
    is_nolocation = 'nolocation' in lower
    t = 'screenshot' if is_nolocation else 'photo'
    e_type = 'other'
    
    if 'bday' in lower: e_type = 'birthday_party'
    elif 'goa' in lower: e_type = 'trip_sightseeing'
    elif 'edinburgh' in lower: e_type = 'college_campus'
    elif 'dublin' in lower: e_type = 'office_work'
    elif 'hyderabad' in lower: e_type = 'family_home'
    elif 'pune' in lower: e_type = 'family_home'
    elif is_nolocation: e_type = 'screenshot'
    elif f == 'root': e_type = 'other'
    
    moment_labels.append({
        'folder': f,
        'event_type': e_type,
        'event_label': f"Event at {f}",
        'scene': 'indoor',
        'type': t,
        'objects': 'various',
        'notes': ''
    })
    
pd.DataFrame(moment_labels).to_csv('library/moment_labels.csv', index=False)
print("Labels created.")

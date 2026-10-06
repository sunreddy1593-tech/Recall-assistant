# Demo library — "Ananya's phone" (simulated)

143 photos in 41 moments, organised as `library/photos/<YYYY-MM-DD>_<Place>/` to stand in for the date
and location a real phone records automatically. Folder names contain ONLY date and place —
never event labels — so the app cannot read answers from them.

Persona: Ananya Sharma — school in Hyderabad (2012–18) → college in Pune (2018–22) → first job in
Bengaluru (2022–23) → Masters in Edinburgh (2023–24) → job in Dublin (2024–25) → back in India (2026).

Files
- `library/chapters.csv` — life chapters (era map) used by the "Roughly when?" question.
- `library/people.csv` — simulated face groups (merge into manifest.csv `people` column):
  Ananya (her), Rohan (close friend/colleague in Bengaluru), Riya / Meera / Arjun (college friends),
  Kabir (younger brother), Tom (coworker in Dublin).
- `library/credits.csv` — original source file for every photo (Pexels / Unsplash / AI-generated).
- `tests/answer_key.csv` — 6 test tasks with tester prompts, target photos and look-alikes.
  PRIVATE: the app must never read this file.
- Screenshots/documents (`*_NoLocation`) are fictional mock-ups ("Demo Bank", "Demo Air"…) with no
  real personal data. Note: their visible in-image dates are Oct 2026.

Credits: photos from Pexels and Unsplash (free licence) plus AI-generated images; see credits.csv.

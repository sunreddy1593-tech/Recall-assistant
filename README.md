# Recall (MVP)

Guided filters for half-remembered photos.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your Gemini API key:
   - Create `.streamlit/secrets.toml`
   - Add your key: `GEMINI_API_KEY = "your_google_ai_studio_key"`
3. Prepare data:
   - Put photos in `library/photos/` (following `<YYYY-MM-DD>_<Place>/` folder naming)
   - Ensure `library/chapters.csv`, `library/people.csv`, and `library/credits.csv` exist.
   - Run `python scripts/make_manifest.py` to generate `library/manifest.csv`
4. Build the index:
   ```bash
   python scripts/build_index.py
   ```
   *(To test UI without AI labelling, run with `--no-ai`)*
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deployment (Streamlit Cloud)
1. Push this repository to GitHub.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and deploy from your repository.
3. In the Streamlit Cloud dashboard, go to the app settings -> Secrets.
4. Add your Gemini API key:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key"
   ```

## Credits
Photo sources and credits are listed in `library/credits.csv` and shown on the "How it works" page in the app.

## Test Scenarios
1. Squatting on the floor at home in Scotland, wearing a face mask (Scotland chapter).
2. At work in a fast-food uniform during a job abroad (Ireland, ~2025).
3. Birthday with college friends, ~Feb 2019 or 2020, across 3 places in one evening.
4. A sibling receiving a school award, "in 7th, before COVID".
5. A small café on a Goa trip with friends, year unknown.
6. A screenshot of a bill, "sometime last year", among many other screenshots (practical retrieval).

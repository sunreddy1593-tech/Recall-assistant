import streamlit as st

st.title("How it works")
st.markdown("""
Not a better search engine — a recall assistant for when search can't help. It turns a partial memory into the right photo.

**The process:**
1. **Offline Indexing:** Photos are processed offline to extract locations, group by time/place into events, and tag with basic properties. (AI labeling to come).
2. **Help Me Remember:** Instead of a single search bar, it guides you step by step (When, Who, Where, What) through what you DO remember.
3. **Faceted Filtering:** Every answer narrows the remaining choices instantly, showing accurate counts.
4. **Moment Cards:** Results are grouped into moments instead of an endless grid.
""")

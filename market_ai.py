import os
import pandas as pd
from google import genai

def analyze_market_gaps(reviews_df):
    if reviews_df is None or reviews_df.empty:
        return "No reviews available."

    reviews_df["rating"] = pd.to_numeric(reviews_df["rating"], errors="coerce")
    low = reviews_df[reviews_df["rating"] <= 2]

    if low.empty:
        return "No low rated reviews found."

    low = low.head(100)

    text = ""
    for _, row in low.iterrows():
        t = str(row["review_text"]).strip()
        if t and t.lower()!= "nan":
            text += f"App: {row['app_title']} | Rating: {row['rating']} | Review: {t[:400]}\n"

    if not text:
        return "No usable text."

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY")
        except:
            pass

    if not api_key:
        return "Please set GEMINI_API_KEY in secrets."

    prompt = f"""
You are a market analyst. Analyze these low-rated reviews:

1. Main bugs and complaints
2. Missing features
3. Market opportunities
4. 3 recommendations for a new app

Use only the reviews. Add limitation note.

Reviews:
{text}
"""

    try:
        client = genai.Client(api_key=api_key)
        res = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return res.text if res.text else "Empty response"
    except Exception as e:
        return f"Error: {e}"
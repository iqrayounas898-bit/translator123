# app.py
"""
Simple Translator Streamlit App
Uses deep-translator to translate text (GoogleTranslator / LibreTranslator fallback).
Run: streamlit run app.py
"""

import streamlit as st
from deep_translator import GoogleTranslator, LibreTranslator
import pandas as pd
import io

# ---------- Language dictionary (name -> code) ----------
LANGS = {
    "Auto-detect": "auto",
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "Bengali": "bn",
    "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Malay": "ms",
    "Persian (Farsi)": "fa",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Turkish": "tr",
    "Vietnamese": "vi",
    # Add more if you'd like
}

# ---------- Helper functions ----------
def translate_text(text: str, src: str, tgt: str) -> str:
    """
    Translate text using GoogleTranslator (deep-translator).
    If GoogleTranslator fails, try LibreTranslator as a fallback.
    src and tgt should be ISO codes or 'auto' for auto-detect.
    """
    if not text:
        return ""
    # If user selected 'auto' use GoogleTranslator with source 'auto' if supported
    try:
        translator = GoogleTranslator(source=src if src != "auto" else "auto", target=tgt)
        return translator.translate(text)
    except Exception as e:
        # Fallback to LibreTranslator (may require a LibreTranslate instance online)
        try:
            translator = LibreTranslator(source=src if src != "auto" else "auto", target=tgt)
            return translator.translate(text)
        except Exception as e2:
            # If both fail, return a helpful error message
            return f"[Translation failed: {e} | fallback failed: {e2}]"

def translate_dataframe(df: pd.DataFrame, column: str, src: str, tgt: str) -> pd.DataFrame:
    """
    Translate values in a dataframe column and return new dataframe with column '<column>_translated'.
    """
    out = df.copy()
    translated = []
    for val in out[column].astype(str).fillna(""):
        translated.append(translate_text(val, src, tgt))
    out[f"{column}_translated"] = translated
    return out

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Translator", layout="wide")
st.title("🌐 Simple Translator (Streamlit)")

with st.sidebar:
    st.header("Settings")
    src_lang_name = st.selectbox("Source language", options=list(LANGS.keys()), index=0)
    tgt_lang_name = st.selectbox("Target language", options=[k for k in LANGS.keys() if k != "Auto-detect"], index=1)
    show_history = st.checkbox("Show translation history", value=True)
    st.markdown("---")
    st.markdown("**Notes:**")
    st.markdown("- Uses `deep-translator`. No API key for basic GoogleTranslator usage.")
    st.markdown("- Large/bulk translations might be rate-limited.")

src_code = LANGS[src_lang_name]
tgt_code = LANGS[tgt_lang_name]

st.header("Translate text")
col1, col2 = st.columns([2, 1])
with col1:
    input_text = st.text_area("Enter text to translate", height=200, placeholder="Type or paste text here...")
    if st.button("Translate"):
        if not input_text.strip():
            st.warning("Please type some text to translate.")
        else:
            with st.spinner("Translating..."):
                result = translate_text(input_text, src_code, tgt_code)
                st.success("Translated")
                st.text_area("Translation", value=result, height=200)
                # Save to session history
                hist = st.session_state.get("history", [])
                hist.insert(0, {"source": input_text, "translated": result, "src": src_lang_name, "tgt": tgt_lang_name})
                st.session_state["history"] = hist

with col2:
    if "history" not in st.session_state:
        st.session_state["history"] = []
    st.subheader("Quick actions")
    if st.button("Clear history"):
        st.session_state["history"] = []
        st.success("History cleared.")
    st.markdown("## Download")
    # Make a small example download of translated text (if present)
    if st.session_state["history"]:
        first = st.session_state["history"][0]
        st.download_button("Download latest translation (txt)", data=first["translated"], file_name="translation.txt")

st.markdown("---")
st.header("Translate file (CSV or TXT)")
uploaded = st.file_uploader("Upload a .txt or .csv file (CSV must have a text column)", type=["txt", "csv"])
if uploaded is not None:
    name = uploaded.name
    st.write(f"Uploaded: **{name}**")
    if name.lower().endswith(".txt"):
        raw = uploaded.read().decode("utf-8")
        st.text_area("File content", value=raw, height=200)
        if st.button("Translate text file"):
            with st.spinner("Translating file..."):
                translated = translate_text(raw, src_code, tgt_code)
                st.download_button("Download translated file", data=translated, file_name=f"translated_{name}")
                st.success("File translated. Use the download button to save it.")
    else:
        # CSV
        try:
            df = pd.read_csv(uploaded)
        except Exception:
            uploaded.seek(0)
            df = pd.read_csv(io.StringIO(uploaded.read().decode("utf-8", errors="ignore")))
        st.write("Preview of uploaded CSV")
        st.dataframe(df.head())
        st.markdown("Choose the column to translate:")
        text_cols = [c for c in df.columns if df[c].dtype == "object" or df[c].dtype == "string"]
        if not text_cols:
            st.warning("No text-like columns detected. If your text is numeric-coded, convert or adjust the file.")
        else:
            col_to_translate = st.selectbox("Column", text_cols)
            if st.button("Translate column"):
                with st.spinner("Translating CSV column (this may take time for many rows)..."):
                    out_df = translate_dataframe(df, col_to_translate, src_code, tgt_code)
                    st.success("Translation complete")
                    st.dataframe(out_df.head())
                    csv_bytes = out_df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download translated CSV", data=csv_bytes, file_name=f"translated_{name}")

st.markdown("---")
if show_history:
    st.header("Translation history")
    hist = st.session_state.get("history", [])
    if not hist:
        st.info("No translations yet.")
    else:
        for i, item in enumerate(hist):
            with st.expander(f"#{i+1} {item['src']} → {item['tgt']}"):
                st.write("**Source:**")
                st.write(item["source"])
                st.write("**Translated:**")
                st.write(item["translated"])

st.markdown("---")
st.caption("Made with ❤️ using Streamlit and deep-translator.")

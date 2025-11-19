# app.py
import streamlit as st

# Try importing deep-translator safely
try:
    from deep_translator import GoogleTranslator, LibreTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except Exception as e:
    DEEP_TRANSLATOR_AVAILABLE = False

import pandas as pd
import io

st.set_page_config(page_title="Translator App", layout="wide")
st.title("🌐 Simple Translator App")

# ---------------- Languages -----------------
LANGS = {
    "Auto-detect": "auto",
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese": "zh-CN"
}

# ---------------- Helper -----------------
def translate_text(text, src, tgt):
    if not DEEP_TRANSLATOR_AVAILABLE:
        return "❌ deep-translator package not installed. Check requirements.txt"

    if not text.strip():
        return ""

    # Try Google first
    try:
        tr = GoogleTranslator(source=src, target=tgt)
        return tr.translate(text)
    except:
        pass

    # Fallback to Libre
    try:
        tr = LibreTranslator(source=src, target=tgt)
        return tr.translate(text)
    except:
        return "❌ Translation failed. Try again later."

# ---------------- UI -----------------
src_lang = st.selectbox("Source Language", list(LANGS.keys()))
tgt_lang = st.selectbox("Target Language", [k for k in LANGS.keys() if k != "Auto-detect"])

text = st.text_area("Enter text to translate")

if st.button("Translate"):
    result = translate_text(text, LANGS[src_lang], LANGS[tgt_lang])
    st.text_area("Translation", value=result, height=200)

# ---------------- File Upload -----------------
st.markdown("---")
st.subheader("Translate Text File or CSV")

file = st.file_uploader("Upload file", type=["txt", "csv"])

if file:
    if file.name.endswith(".txt"):
        data = file.read().decode("utf-8")
        st.write("File Content:")
        st.text_area("File", value=data, height=200)

        if st.button("Translate File"):
            translated = translate_text(data, LANGS[src_lang], LANGS[tgt_lang])
            st.download_button("Download Translation", translated, "translated.txt")

    else:
        df = pd.read_csv(file)
        st.write(df.head())

        col = st.selectbox("Select column to translate", df.columns)

        if st.button("Translate Column"):
            df[f"{col}_translated"] = df[col].astype(str).apply(
                lambda x: translate_text(x, LANGS[src_lang], LANGS[tgt_lang])
            )
            st.write(df.head())
            st.download_button("Download CSV", df.to_csv(index=False), "translated.csv")

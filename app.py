import streamlit as st
import pandas as pd
import json

st.title("GPT Wrapped 💫")

st.write(
    """1. Click on the profile icon on the bottom left of the ChatGPT interface.
         \n2. Select Settings > Data Controls > Export Data.
         \n3. Once you receive the download link via email, download your data, unzip the file, and upload the `conversations.json` file below."""
)

uploaded = st.file_uploader("Upload your `conversations.json` file", type=["json"])

if uploaded:
    data = json.load(uploaded)

    total_convos = len(data)

    st.subheader("your stats")
    st.metric("total conversations", total_convos)

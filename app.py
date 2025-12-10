import streamlit as st
import pandas as pd
from data_parser import *
from analysis import *
import json
import matplotlib.pyplot as plt

st.set_page_config(page_title="GPT Wrapped", page_icon="✨", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --accent: #7c3aed;
        --accent-2: #22d3ee;
        --card: #0f172a;
        --card-alt: #111827;
        --text: #e5e7eb;
    }
    .hero {
        padding: 24px 28px;
        border-radius: 18px;
        background: radial-gradient(circle at 10% 20%, rgba(124,58,237,0.25), transparent 35%),
                    radial-gradient(circle at 80% 0%, rgba(34,211,238,0.25), transparent 32%),
                    #0b1224;
        border: 1px solid rgba(255,255,255,0.08);
        color: var(--text);
        margin-bottom: 12px;
    }
    .hero h1 { margin: 0; font-size: 2.4rem; font-weight: 800; }
    .hero p { margin-top: 8px; color: #cbd5e1; font-size: 1rem; }
    .card-row { display: grid; grid-template-columns: repeat(auto-fit,minmax(200px,1fr)); gap: 12px; }
    .stat-card {
        background: var(--card);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 14px 16px;
        color: var(--text);
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    .stat-label { text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.75rem; color: #94a3b8; }
    .stat-value { font-size: 1.6rem; font-weight: 700; color: var(--text); margin-top: 6px; }
    .pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: linear-gradient(120deg, var(--accent), var(--accent-2));
        color: #0b1224;
        font-weight: 700;
        font-size: 0.85rem;
        margin-left: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>GPT Wrapped</h1>
        <p>Upload your ChatGPT export to see how your year looked in conversations.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """**How to export**
    \n 1) Profile > Settings > Data Controls > Export Data
    \n 2) Download the zip from the email
    \n 3) Unzip and upload `conversations.json`
    """
)

name = st.text_input("What should we call you?", placeholder="Type your name")

uploaded = st.file_uploader("Upload your `conversations.json` file", type=["json"])

if uploaded:
    data = json.load(uploaded)

    all_messages = []
    for conv in data:
        messages = extract_messages(conv)
        for msg in messages:
            msg["conversation_id"] = conv.get("id")
            msg["conversation_title"] = conv.get("title", "Untitled")
            all_messages.append(msg)

    all_messages = filter_messages_by_year(all_messages, 2025)

    total_convos = len(set(m.get("conversation_id") for m in all_messages))
    total_messages = len(all_messages)
    user_messages = [m for m in all_messages if m["author"] == "user"]
    assistant_messages = [m for m in all_messages if m["author"] == "assistant"]

    display_name = name.strip() if name.strip() else "Your"
    st.markdown(f"### ✨ {display_name} 2025 ChatGPT Wrapped")

    user_word_count = count_words_in_messages(user_messages)

    st.markdown("<div class='card-row'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='stat-card'><div class='stat-label'>Words you sent</div><div class='stat-value'>{user_word_count:,}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"You sent **{user_word_count:,} words** to ChatGPT this year that's about **{user_word_count / 70000:.2f} books** worth. Author much?"
    )
    st.markdown(
        f"<div class='stat-card'><div class='stat-label'>Total conversations</div><div class='stat-value'>{total_convos}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='stat-card'><div class='stat-label'>Total messages</div><div class='stat-value'>{total_messages}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='stat-card'><div class='stat-label'>Messages you sent</div><div class='stat-value'>{len(user_messages)}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # st.subheader("Your word cloud")
    # wordcloud = generate_word_cloud(user_messages)
    # if wordcloud:
    #     fig, ax = plt.subplots(figsize=(10, 5))
    #     ax.imshow(wordcloud, interpolation="bilinear")
    #     ax.axis("off")
    #     st.pyplot(fig)
    # else:
    #     st.write("Uh oh, something went wrong generating your word cloud.")

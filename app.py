import streamlit as st
import pandas as pd
from data_parser import *
from analysis import *
from database import *
import json
import matplotlib.pyplot as plt
import nltk
import hashlib

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("taggers/averaged_perceptron_tagger")
except LookupError:
    nltk.download("averaged_perceptron_tagger")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

st.set_page_config(page_title="GPT Wrapped", page_icon="✨", layout="wide")

st.title("GPT Wrapped 💫")

st.markdown(
    """Upload your ChatGPT export to see how your year looked in conversations.

**How to export:**
1. Profile → Settings → Data Controls → Export Data
2. Download the zip from the email
3. Unzip and upload `conversations.json`
    """
)

name = st.text_input("What should we call you?", placeholder="Type your name")

uploaded = st.file_uploader("Upload your `conversations.json` file", type=["json"])

if uploaded:
    data = json.load(uploaded)

    # Generate unique hash for this user based on their data
    file_hash = get_file_hash(data)

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

    st.divider()

    display_name = name.strip() if name.strip() else "Your"
    st.header(f"{display_name}'s 2025 ChatGPT Wrapped")

    user_word_count = count_words_in_messages(user_messages)

    st.markdown(
        f"### You sent **{user_word_count:,} words** this year — that's about **{user_word_count / 70000:.2f} books** worth."
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Words sent", f"{user_word_count:,}")
    col2.metric("Total conversations", total_convos)
    col3.metric("Total messages", total_messages)
    col4.metric("Messages sent", len(user_messages))

    st.subheader("Your Monthly Activity")

    monthly_df = get_conversations_by_month(all_messages)
    if not monthly_df.empty:
        st.bar_chart(monthly_df.set_index("Month")["Messages"])

    longest_title, longest_count = get_longest_conversation(data)
    if longest_title and longest_count > 0:
        st.markdown(
            f"**Longest conversation:** *{longest_title}* ({longest_count} messages)"
        )

    st.subheader("📚 Your Conversation Topics")

    with st.spinner("Discovering your conversation topics..."):
        topics, _ = extract_conversation_topics(all_messages, top_n=5)

    if topics:
        st.write("Here's what you mostly talked about:")
        topics_df = pd.DataFrame(topics)
        for _, row in topics_df.iterrows():
            st.markdown(
                f"- **{row['topic']}** — {row['count']} conversations ({row['percentage']:.1f}%)"
            )
    else:
        st.write("Not enough conversations to extract topics (need at least 10).")

    # Auto-save stats and show comparison (cached so it only runs once per file hash)
    @st.cache_data(hash_funcs={type(file_hash): lambda x: x})
    def save_and_compare(file_hash, total_words, total_convos, total_messages):
        save_user_stats(file_hash, total_words, total_convos, total_messages)

        words_percentile = get_percentile(file_hash, "total_words")
        convos_percentile = get_percentile(file_hash, "total_conversations")
        messages_percentile = get_percentile(file_hash, "total_messages")
        stats_summary = get_stats_summary()

        return {
            "words_percentile": words_percentile,
            "convos_percentile": convos_percentile,
            "messages_percentile": messages_percentile,
            "stats_summary": stats_summary,
        }

    comparison = save_and_compare(
        file_hash, user_word_count, total_convos, total_messages
    )

    st.divider()
    st.subheader("How You Stack Up")

    st.write(
        f"You're in the **top {100 - comparison['words_percentile']:.0f}%** for words sent (avg: {comparison['stats_summary']['avg_words']:,.0f} words)"
    )
    st.write(
        f"You're in the **top {100 - comparison['convos_percentile']:.0f}%** for conversations (avg: {comparison['stats_summary']['avg_conversations']:.0f} convos)"
    )
    st.write(
        f"You're in the **top {100 - comparison['messages_percentile']:.0f}%** for total messages (avg: {comparison['stats_summary']['avg_messages']:.0f} messages)"
    )

    if comparison["words_percentile"] >= 90:
        st.balloons()
        st.write("**You're a ChatGPT power user!**")

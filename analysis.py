from collections import Counter
import re
import subprocess
from datetime import datetime

from wordcloud import WordCloud
from nltk.corpus import stopwords
import nltk
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter, defaultdict


def count_words_in_messages(messages):
    total_words = 0
    for msg in messages:
        if "parts" in msg:
            for part in msg["parts"]:
                if "text" in part:
                    total_words += len(part["text"].split())
    return total_words


def generate_word_cloud(messages):
    all_text = ""
    for msg in messages:
        if "parts" in msg:
            for part in msg["parts"]:
                if "text" in part:
                    all_text += " " + part["text"]

    if not all_text.strip():
        return None

    stop_words = set(stopwords.words("english"))
    stop_words.update([chr(i) for i in range(ord("a"), ord("z") + 1)])

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        stopwords=stop_words,
        colormap="viridis",
    ).generate(all_text)

    return wordcloud


def get_conversations_by_month(all_messages):
    monthly_counts = Counter()

    for msg in all_messages:
        if "timestamp" in msg and msg["timestamp"]:
            try:
                timestamp = datetime.fromtimestamp(msg["timestamp"])
                month_key = f"{timestamp.strftime('%b')}"  # "Jan", "Feb", etc.
                monthly_counts[month_key] += 1
            except:
                pass

    month_order = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    df = pd.DataFrame(
        [
            {"Month": month, "Messages": monthly_counts.get(month, 0)}
            for month in month_order
        ]
    )

    df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
    df = df.sort_values("Month")

    return df


def get_longest_conversation(conversations):
    conv_lengths = {}

    for conv in conversations:
        messages = conv.get("mapping", {})
        msg_count = sum(1 for node in messages.values() if node.get("message"))
        conv_lengths[conv.get("id")] = {
            "title": conv.get("title", "Untitled"),
            "message_count": msg_count,
        }

    if not conv_lengths:
        return None, 0

    longest_id = max(conv_lengths.items(), key=lambda x: x[1]["message_count"])
    return longest_id[1]["title"], longest_id[1]["message_count"]


def extract_conversation_topics(all_messages, top_n=5):
    try:
        nltk.data.find("taggers/averaged_perceptron_tagger")
    except:
        nltk.download("averaged_perceptron_tagger")

    try:
        nltk.data.find("tokenizers/punkt")
    except:
        nltk.download("punkt")

    conversations = {}
    for msg in all_messages:
        conv_id = msg.get("conversation_id")
        if conv_id and conv_id not in conversations:
            title = msg.get("conversation_title", "")
            if title and title != "Untitled" and len(title) > 5:
                conversations[conv_id] = title

    docs = list(conversations.values())

    if len(docs) < 10:
        return None, None

    # Extract only nouns and adjectives using NLTK
    def extract_meaningful_words(text):
        tokens = nltk.word_tokenize(text.lower())
        tagged = nltk.pos_tag(tokens)
        # Keep nouns (NN*) and adjectives (JJ*)
        words = [
            word
            for word, pos in tagged
            if (pos.startswith("NN") or pos.startswith("JJ"))
            and len(word) > 2
            and word.isalpha()
        ]
        return " ".join(words)

    # Process all docs
    processed_docs = [extract_meaningful_words(doc) for doc in docs]

    # Custom vectorizer
    vectorizer = CountVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.7)

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    topic_model = BERTopic(
        embedding_model=embedding_model,
        vectorizer_model=vectorizer,
        min_topic_size=max(5, len(docs) // 15),
        nr_topics="auto",
        verbose=False,
    )

    topics, _ = topic_model.fit_transform(docs)

    # Create better topic labels from processed docs
    topic_words = defaultdict(list)
    for i, topic_id in enumerate(topics):
        if topic_id != -1:
            topic_words[topic_id].extend(processed_docs[i].split())

    # Get top words per topic
    topic_results = []
    topic_counts = Counter(topics)

    for topic_id, count in topic_counts.most_common(top_n + 1):
        if topic_id == -1:
            continue

        words = topic_words[topic_id]
        word_counts = Counter(words)
        top_words = [w for w, _ in word_counts.most_common(3)]

        if len(top_words) >= 2:
            topic_label = " + ".join(top_words[:3])
            topic_results.append(
                {
                    "topic": topic_label,
                    "count": count,
                    "percentage": (count / len(docs)) * 100,
                }
            )

        if len(topic_results) >= top_n:
            break

    return topic_results, topic_model

from collections import Counter
import re

from wordcloud import WordCloud
from nltk.corpus import stopwords
import nltk

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


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

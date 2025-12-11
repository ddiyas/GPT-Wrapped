# GPT Wrapped

**[Live Demo](https://cgpt-wrapped.streamlit.app/)**

A personalized, Spotify Wrapped-style analysis for your ChatGPT conversation history. Get insights into your AI interaction patterns with topic modeling, sentiment analysis, and temporal pattern mining.

## Why GPT Wrapped?

Unlike simply asking ChatGPT to analyze itself (which focuses heavily on recent conversations), GPT Wrapped processes your entire export locally to provide accurate, comprehensive insights across months or years of usage.

## Features

- **Topic Discovery**: Identifies conversation themes using BERTopic with BERT embeddings
- **Temporal Patterns**: Visualizes your monthly activity and conversation trends
- **Statistics**: Word counts, longest conversations, and linguistic metrics
- **Comparative Analytics**: See how you stack up against other users (anonymized)
- **Privacy-First**: All processing happens locally; only aggregate stats are stored

## Quick Start

1. **Export your ChatGPT data**
   - Go to ChatGPT > Profile > Settings > Data Controls > Export Data
   - Download the zip from the email
   - Extract `conversations.json`

2. **Visit the app**
- Go to [cgpt-wrapped.streamlit.app](cgpt-wrapped.streamlit.app)

3. **Upload your `conversations.json` file and explore your wrapped!**


## How It Works

### Data Processing
- Parses ChatGPT's complex nested node-tree conversation structure
- Reconstructs conversation threads by walking through parent-child relationships
- Filters by year and handles multi-modal content (text, audio transcriptions, assets)

### Machine Learning
- **BERTopic**: Extracts nouns and adjectives from conversation titles using NLTK POS tagging, then applies Sentence-BERT embeddings for semantic clustering
- **UMAP + HDBSCAN**: Reduces dimensions and performs density-based clustering to identify conversation themes
- Adaptive topic sizing based on dataset size

### Database
- SQLite backend with SHA-256 hashing for anonymous user identification
- Stores only aggregate metrics (no conversation content)
- Percentile rankings and comparative statistics

## Tech Stack

- **Frontend**: Streamlit
- **ML/NLP**: BERTopic, Sentence-BERT, NLTK, scikit-learn
- **Database**: SQLite
- **Visualization**: Matplotlib, WordCloud, Pandas

## Collaborators
- [Diya Shah](https://github.com/ddiyas)
- [Dhruvi Vinchhi](https://github.com/DhruviCodes)

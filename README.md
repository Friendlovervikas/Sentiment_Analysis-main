# 🐦 Twitter Sentiment Analysis System

A comprehensive Full-Stack web application that leverages Natural Language Processing (NLP) to analyze the emotional tone of Twitter data. The system provides real-time insights from live tweets, batch processing for large datasets, and individual sentence analysis.

## 🚀 Key Features

*   **Live API Analysis:** Fetches and analyzes real-time tweets based on user-defined hashtags using the **Tweepy API**.
*   **Batch CSV Processing:** Upload large CSV datasets for bulk sentiment scoring with an automated export/download feature.
*   **Sentence Level Detection:** Instant polarity analysis for manual text input to determine emotional status.
*   **NLP Pipeline:** Robust text cleaning using Regex (to remove handles and URLs) and NLTK stopword removal.
*   **Interactive UI:** A modern, responsive frontend featuring wave animations and flip-card transitions.

---

## 🛠️ Tech Stack

**Frontend:**
*   HTML5 & CSS3 (Custom animations)
*   JavaScript (DOM Manipulation)

**Backend:**
*   Python 3.x
*   Flask (Web Framework)

**Data Science & NLP:**
*   TextBlob (Sentiment Scoring)
*   NLTK (Natural Language Toolkit)
*   Pandas (Data manipulation)
*   Tweepy (Twitter API Integration)

---

## 📋 Prerequisites

Before running the project, ensure you have:
*   Python 3.8+ installed.
*   A Twitter Developer Account with **Bearer Token** access.
*   NLTK data downloaded (Stopwords).

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory or configure your environment variables:
```env
TWITTER_BEARER_TOKEN=your_bearer_token_here
SECRET_KEY=your_flask_secret_key

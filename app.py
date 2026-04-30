import re
import time
import nltk
import pandas as pd
from io import StringIO
import tempfile
from textblob import TextBlob
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from nltk.corpus import stopwords
from dotenv import load_dotenv
import tweepy
import tweepy.errors

# Download necessary NLTK data
nltk.download('stopwords')

# Hardcoded Twitter API keys and secret key
TWITTER_CONSUMER_KEY = '3yRdJCjiYJb6elhOv1IU2AZld'
TWITTER_CONSUMER_SECRET = 'bMWW0KNISmZj5ZH4Il8rwmhOvn8yVsmusM6pxqxiIfnl7IJ4vz'
TWITTER_ACCESS_TOKEN = '1202144239099887616-8tAE0tZ9FwCZX95y28ZqOUqZ3LKVjO'
TWITTER_ACCESS_TOKEN_SECRET = 'PIgw043Qi25jmwtqGNLyZbclD9c8HLbMGMHVO088r35pe'
TWITTER_BEARER_TOKEN ='AAAAAAAAAAAAAAAAAAAAAJV8xAEAAAAA%2Fc9xsh%2B7BGnOlGEnxvXaUYnkb2s%3DXi4Py2B0dPrHcFxfwNWlHr8EtNE2NTLJW4QgsbNLuulZYqaCtx'
SECRET_KEY = '_8tel-c4bKcp7cx4hk5-PWzWe62RkQR7jDtazS3vh6b8MF_vRs'

# Flask app setup with hardcoded secret key
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.static_folder = 'static'

# ----------------------------- Utility Functions -----------------------------

def clean_tweet(tweet):
   return ' '.join(re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def get_tweet_sentiment(tweet):
    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity == 0:
        return "neutral"
    else:
        return "negative"

def preprocess_text(tweet):
    tweet = tweet.lower()
    tweet = re.sub(r'[^\w\s]', '', tweet)
    stop_words = set(stopwords.words('english'))
    tweet = ' '.join([word for word in tweet.split() if word not in stop_words])
    return tweet

def get_polarity_words(tweet):
    analysis = TextBlob(tweet)
    words = analysis.words
    word_polarities = {word: TextBlob(word).sentiment.polarity for word in words}
    sorted_words = sorted(word_polarities.items(), key=lambda item: item[1], reverse=True)
    top_words = [word for word, polarity in sorted_words[:5]]
    return ', '.join(top_words), analysis.sentiment.polarity

def get_tweets_from_csv(file_content):
    try:
        data = pd.read_csv(StringIO(file_content))
        tweets = data.to_dict(orient='records')
        for tweet in tweets:
            tweet['sentiment'] = get_tweet_sentiment(tweet['content'])
            tweet['preprocessed_content'] = preprocess_text(tweet['content'])
            top_words, polarity_score = get_polarity_words(clean_tweet(tweet['content']))
            tweet['top_polarity_words'] = top_words
            tweet['polarity_score'] = polarity_score
        return tweets
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return []

# ----------------------------- Routes -----------------------------

@app.route('/')
def home():
    return render_template("features.html")

@app.route("/predict", methods=['POST'])
def pred():
    if request.method == 'POST':
        try:
            csv_file = request.files['csv_file']
            file_content = csv_file.read().decode('utf-8')
            fetched_tweets = get_tweets_from_csv(file_content)

            processed_df = pd.DataFrame(fetched_tweets)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            processed_df.to_csv(temp_file.name, index=False)
            temp_file_path = temp_file.name
            temp_file.close()

            return render_template('result.html', result=fetched_tweets, csv_download=True, temp_file_path=temp_file_path)
        except Exception as e:
            return f"Error: {str(e)}"

@app.route('/download_csv')
def download_csv():
    temp_file_path = request.args.get('temp_file_path')
    if temp_file_path and temp_file_path and os.path.exists(temp_file_path):
        return send_file(temp_file_path, mimetype='text/csv', download_name='processed_tweets.csv', as_attachment=True)
    else:
        return "File not found", 404

@app.route("/predict1", methods=['POST'])
def pred1():
    if request.method == 'POST':
        text = request.form['txt']
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity > 0:
            text_sentiment = "positive"
        elif polarity == 0:
            text_sentiment = "neutral"
        else:
            text_sentiment = "negative"
        return render_template('result1.html', msg=text, result=text_sentiment)

@app.route("/live-streaming", methods=['GET', 'POST'])
def live_stream():
    tweets = []
    error_message = None

    if request.method == 'POST':
        keyword = request.form.get('keyword', '').strip()

        if not keyword:
            error_message = "Please enter a keyword to search."
        else:
            now = time.time()
            last_searches = session.get('last_searches', {})

            # Rate limiting per keyword
            last_time = last_searches.get(keyword, 0)
            cooldown = 60  # seconds

            if now - last_time < cooldown:
                wait_time = int(cooldown - (now - last_time))
                error_message = f"Please wait {wait_time} seconds before searching '{keyword}' again."
            else:
                try:
                    client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
                    response = client.search_recent_tweets(query=keyword, max_results=5)

                    if response.data:
                        for tweet in response.data:
                            sentiment = get_tweet_sentiment(tweet.text)
                            tweets.append({"text": tweet.text, "sentiment": sentiment})
                    else:
                        error_message = "No tweets found for this keyword."

                    last_searches[keyword] = now
                    session['last_searches'] = last_searches

                except tweepy.TooManyRequests:
                    error_message = "Rate limit exceeded. Please wait and try again later."
                except Exception as e:
                    error_message = f"Twitter API Error: {str(e)}"

    return render_template("av.html", tweets=tweets, error=error_message)

# ----------------------------- Main -----------------------------
if __name__ == '__main__':
    # Use the PORT environment variable if available, otherwise default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

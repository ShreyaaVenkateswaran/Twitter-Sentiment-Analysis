import os
import tweepy
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from textblob import TextBlob
import uvicorn
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

class TweetRequest(BaseModel):
    keyword: str
    count: int = 10 

def analyze_sentiment(text: str) -> str:
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def fetch_tweets(keyword: str, count: int):
    try:
        tweets = api.search_tweets(q=keyword, count=count, lang="en", tweet_mode="extended")
        results = []
        for tweet in tweets:
            sentiment = analyze_sentiment(tweet.full_text)
            results.append({
                "text": tweet.full_text,
                "sentiment": sentiment
            })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Sentiment Prediction API is running!"}

@app.post("/fetch_tweets/")
def get_tweets(request: TweetRequest):
    return fetch_tweets(request.keyword, request.count)

@app.get("/frontend")
def serve_frontend():
    return FileResponse("index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
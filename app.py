from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from googleapiclient.discovery import build
from textblob import TextBlob
from dotenv import load_dotenv
import os
from typing import List

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="YouTube Sentiment Analysis API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# YouTube API Setup
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Models
class AnalyzeRequest(BaseModel):
    video_id: str
    max_comments: int = 50

class SentimentResult(BaseModel):
    text: str
    polarity: float
    sentiment: str

class AnalysisResponse(BaseModel):
    video_id: str
    total_comments: int
    positive: int
    neutral: int
    negative: int
    comments: List[SentimentResult]

# Helper Functions
def analyze_sentiment(text: str) -> dict:
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    sentiment = "neutral"
    if polarity > 0.1: sentiment = "positive"
    elif polarity < -0.1: sentiment = "negative"
    return {"text": text, "polarity": polarity, "sentiment": sentiment}

def get_comments(video_id: str, max_results: int) -> List[str]:
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=min(100, max_results),
        textFormat="plainText"
    )
    while request and len(comments) < max_results:
        response = request.execute()
        comments.extend(item['snippet']['topLevelComment']['snippet']['textDisplay'] 
                       for item in response['items'])
        request = youtube.commentThreads().list_next(request, response)
    return comments[:max_results]

# API Endpoint
@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalyzeRequest):
    try:
        comments = get_comments(request.video_id, request.max_comments)
        if not comments:
            raise HTTPException(status_code=404, detail="No comments found")
        
        analyzed = [analyze_sentiment(comment) for comment in comments]
        counts = {
            "positive": sum(1 for r in analyzed if r["sentiment"] == "positive"),
            "neutral": sum(1 for r in analyzed if r["sentiment"] == "neutral"),
            "negative": sum(1 for r in analyzed if r["sentiment"] == "negative")
        }
        
        return {
            "video_id": request.video_id,
            "total_comments": len(analyzed),
            **counts,
            "comments": analyzed[:10]  # Return first 10 as samples
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
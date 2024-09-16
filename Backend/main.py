import asyncio
import aiohttp
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
story_detailed_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"

def format_time(timestamp):
    
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

async def fetch(session, url):

    async with session.get(url) as response:
        return await response.json()


async def get_story_details(session, story_id):

    story_url = story_detailed_url.format(story_id)
    story_details = await fetch(session, story_url)

    return {
        "Title": story_details.get("title"),
        "Author": story_details.get("by"),
        "URL": story_details.get("url"),
        "Score": story_details.get("score"),
        "Time": format_time(story_details.get("time", 0))
    }


@app.get('/top_news')
async def find_top_news():
    async with aiohttp.ClientSession() as session:

        top_stories_ids = await fetch(session, top_stories_url)
        tasks = [get_story_details(session, story_id) for story_id in top_stories_ids[:10]]
        
        top_stories = await asyncio.gather(*tasks)
    return top_stories
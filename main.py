

from fastapi import FastAPI, Query, HTTPException
from youtubesearchpython import VideosSearch
import yt_dlp 

app = FastAPI()

@app.get('/')
def home():
    return {"fdsfs"}

@app.get('/searchVideo')
def search(search:str):  
    videosSearch = VideosSearch(search, limit = 10)
    data = videosSearch.result()["result"]
    print(data)
    responses = []
    for entry in data:
        response = {
        "type": entry["type"],
        "id": entry["id"],
        "title": entry["title"],
        "publishedTime": entry["publishedTime"],
        "duration": entry["duration"],
        "viewCount": entry["viewCount"]["text"],
        "thumbnails": entry["thumbnails"][0],  # Taking the higher quality thumbnail
        "channelName": entry["channel"]["name"],
        "channelThumbnail": entry["channel"]["thumbnails"][0],
        "link":entry["link"]
         }
        responses.append(response)
    return responses

async def download_and_get_mp3_url(video_url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if "entries" in info:
                raise HTTPException(status_code=400, detail="Playlists are not supported")
            audio_url = info["formats"][0]["url"]
            return info

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=400, detail=f"Error downloading: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

@app.get("/download-mp3")
async def get_downloadable_mp3_url(video_url: str = Query(..., description="URL of the YouTube video")):
    mp3_url = await download_and_get_mp3_url(video_url)
    return {"download_url": mp3_url['url']}
import requests
from bs4 import BeautifulSoup
from youtubesearchpython import VideosSearch
import subprocess

def get_spotify_metadata(spotify_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(spotify_url, headers=headers)
    if response.status_code != 200:
        return None, None

    html = BeautifulSoup(response.text, 'html.parser')
    title_tag = html.find("meta", {"property": "og:title"})
    podcast_tag = html.find("meta", {"property": "og:description"})

    if title_tag and podcast_tag:
        title = title_tag["content"]
        podcast = podcast_tag["content"].split("·")[0].strip()
        return title, podcast
    return None, None

def search_youtube(query):
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        if "/watch?v=" in link["href"]:
            return "https://www.youtube.com" + link["href"]
    return None

def download_youtube_audio(url):
    command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", "downloads/%(title)s.%(ext)s",  # Asegúrate de tener la carpeta 'downloads'
        url
    ]
    result = subprocess.run(command, capture_output=True)
    return result.returncode == 0

def search_youtube_video(query: str) -> str:
    try:
        results = VideosSearch(query, limit=1).result()
        return results["result"][0]["link"] if results["result"] else None
    except Exception as e:
        print(f"Error buscando en YouTube: {e}")
        return None


import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from pytube import YouTube
import yt_dlp

API_TOKEN = "8096079559:AAFg_Yn4P4RA0RdYw4B9GQJuvdLpZoFi84s"  # Replace with your bot's API token

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def download_youtube_video(url: str) -> str:
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        file_path = video.download()
        return file_path
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return None

def download_instagram_video(url: str) -> str:
    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)
        return file_name
    except Exception as e:
        print(f"Error downloading Instagram video: {e}")
        return None

# Detect whether the URL is for YouTube or Instagram
def is_youtube_url(url: str) -> bool:
    return "youtube.com" in url or "youtu.be" in url

def is_instagram_url(url: str) -> bool:
    return "instagram.com" in url

# Command handler for /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Welcome! Send me a YouTube or Instagram video URL, and I'll download the video for you.")

# Handler for messages with video URLs
@dp.message()
async def handle_video_request(message: Message):
    url = message.text.strip()

    # Check if it's a valid YouTube or Instagram URL
    if is_youtube_url(url):
        await message.answer("Downloading YouTube video...")
        video_path = download_youtube_video(url)
        if video_path:
            await message.answer_video(open(video_path, 'rb'))
            os.remove(video_path)  # Clean up the downloaded file
        else:
            await message.answer("Failed to download the YouTube video.")
    elif is_instagram_url(url):
        await message.answer("Downloading Instagram video...")
        video_path = download_instagram_video(url)
        if video_path:
            await message.answer_video(open(video_path, 'rb'))
            os.remove(video_path)  # Clean up the downloaded file
        else:
            await message.answer("Failed to download the Instagram video.")
    else:
        await message.answer("Please send a valid YouTube or Instagram video URL.")

# Main function to start polling
async def main():
    await dp.start_polling(bot)

# Run the bot
if __name__ == "__main__":
    print("Bot started")
    asyncio.run(main())

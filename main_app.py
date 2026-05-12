import yt_dlp
import re
from openai import OpenAI
import os
import pandas as pd
import requests

# --- 1. Configure ---
API_KEY = os.getenv("SILICONFLOW_KEY")
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

#The videos' URLs we want to catch
CHANNELS = {
    "Andrej Karpathy":"https://www.youtube.com/@AndrejKarpathy/videos",
    "Matthew Berman":"https://www.youtube.com/@MatthewBerman/videos",
    "AI Explained": "https://www.youtube.com/@AIExplained/videos"
}

# --- 2. Help functions ---
def clean_vtt(vtt_text):
    """Clean VTT format, keep text content"""
    lines = vtt_text.splitlines()
    clean_lines = []
    for line in lines:
        if '-->' in line or line.isdigit() or not line.strip() or line.startswith('WEBVTT'):
            continue
        clean_content = re.sub(r'<[^>]+>', '', line).strip()
        if clean_content:
            clean_lines.append(clean_content)
    return " ".join(dict.fromkeys(clean_lines))


def get_video_data(video_url):
    ydl_opts = {
        'format': 'best',
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en.*'],
        'quiet': True,
        'no_warnings': True,
    }

    full_text = ""
    v_title = "Unknown Title"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=False)
                v_title = info.get('title', 'Unknown Title')

                subtitles = info.get('requested_subtitles')
                if subtitles and 'en' in subtitles:
                    subtitle_url = subtitles['en']['url']
                    response = requests.get(subtitle_url)
                    if response.status_code == 200:
                        full_text = clean_vtt(response.text)
            except Exception as e:
                print(f"   ⚠️ YouTube Blocked fetching for: {video_url}")
                return "Video Restricted", "Summarization failed due to YouTube bot detection. Please check the URL manually."

        if full_text:
            prompt = f"Summarize this AI video transcript into 3 key points: {full_text[:3000]}"
        else:
            prompt = f"Based on the video title '{v_title}', predict the 3 most likely key discussion points about this AI topic."

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return v_title, response.choices[0].message.content

    except Exception as e:
        return "System Busy", "Temporary service interruption. Please try again later."


# --- 3. Run main ---
def main():
    db_file = "llm_tracker_database.csv"

    #Read the processed URL
    processed_urls = []
    if os.path.exists(db_file):
        try:
            existing_df = pd.read_csv(db_file)
            processed_urls = existing_df['URL'].tolist()
        except:pass

    for author, channel_url in CHANNELS.items():
        print(f"\n--- Scanning Channel: {author} ---")

        try:
            ydl_opts = {'extract_flat': True, 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                channel_info = ydl.extract_info(channel_url, download=False)
                # Get the latest two videos of each channel
                video_entries = channel_info.get('entries', [])[:5]

            for entry in video_entries:
                v_url = f"https://www.youtube.com/watch?v={entry['id']}"

                if v_url in processed_urls:
                    print(f"⏩ Skipping (Already in DB): {v_url}")
                    continue

                print(f"🚀 Processing: {v_url}")
                v_title, v_summary = get_video_data(v_url)

                # Prepare new data
                new_entry = pd.DataFrame([{
                    "Author": author,
                    "Title": v_title,
                    "URL": v_url,
                    "Summary": v_summary
                }])

                # Write to CSV in real time to prevent data loss
                new_entry.to_csv(db_file, mode='a', index=False, header=not os.path.exists(db_file),
                                 encoding='utf-8-sig')
                processed_urls.append(v_url)
                print(f"✅ Saved to DB: {v_title}")

        except Exception as e:
            print(f"❌ Error scanning channel {author}: {e}")
            continue  # One channel error doesn't affect other channels

    print("\n🎉 All tasks finished!")



if __name__ == "__main__":
    main()

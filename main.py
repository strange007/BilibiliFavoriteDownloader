import os
import requests
import argparse
from tqdm import tqdm
import subprocess  # For merging video and audio

MEDIA_ID = "YOUR_MEDIA_ID"  # Replace with your actual media ID

BASE_API_URL = "https://api.bilibili.com/x/player/playurl"

def create_custom_headers():
    return {
        "Connection": "Keep-Alive",
        "Accept-Language": "en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3",
        "Accept": "text/html, application/xhtml+xml, */*",
        "Referer": "https://www.bilibili.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
    }

def fetch_bvids_from_media_id(media_id, headers):
    url = "https://api.bilibili.com/x/v3/fav/resource/ids"
    params = {"media_id": media_id, "platform": "web"}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    return [item['bv_id'] for item in data['data'] if 'bv_id' in item]

def fetch_video_data(bvid, headers):
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']

def fetch_video_url(bvid, cid, qn, headers):
    url = f"{BASE_API_URL}?bvid={bvid}&cid={cid}&qn={qn}&fnval=80&fnver=0&fourk=1"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    try:
       video_url = data['data']['dash']['video'][0]['baseUrl']
       audio_url = data['data']['dash']['audio'][0]['baseUrl']
       return video_url, audio_url
    except (KeyError, IndexError, TypeError) as e:
       print(f"Error extracting video URL: {e}")
       print(f"Response data: {data}")
       return None, None

def download_file(url, filename, headers):
    try:
        response = requests.get(url, stream=True, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        total_length = int(response.headers.get('content-length', 0))
        chunk_size = 8192  # Adjust chunk size as needed

        with open(filename, 'wb') as file:
            for chunk in tqdm(response.iter_content(chunk_size=chunk_size),
                              total=(total_length // chunk_size) + 1,
                              unit='KB', unit_scale=True, desc=filename):
                if chunk:
                    file.write(chunk)
        return True # Download successful

    except requests.exceptions.RequestException as e:
        print(f"Download failed for {filename}: {e}")
        return False  # Download failed

def merge_video_audio(video_file, audio_file, output_file):
    try:
        # Use ffmpeg to merge video and audio
        command = [
            'ffmpeg',
            '-i', video_file,
            '-i', audio_file,
            '-c', 'copy',  # Copy streams without re-encoding
            output_file
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)  # Ensure command success

        print(f"Successfully merged video and audio into {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error merging video and audio: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download videos from Bilibili")
    parser.add_argument("-b", "--bvids", nargs='+', help="Specific BVIDs to download")
    args = parser.parse_args()

    headers = create_custom_headers()

    video_bvids = []
    if args.bvids:
        video_bvids = args.bvids
    elif MEDIA_ID:
        video_bvids = fetch_bvids_from_media_id(MEDIA_ID, headers)
        if not video_bvids:
            print("Error: No valid BVIDs found in the media list.")
            return
    else:
        print("Error: Please provide a media ID or BVIDs.")
        return

    for bvid in video_bvids:
        video_data = fetch_video_data(bvid, headers)
        if not video_data:
            print(f"Failed to fetch video data for BVID: {bvid}")
            continue

        video_url, audio_url = fetch_video_url(bvid, video_data['cid'], qn=64, headers=headers)

        if not video_url or not audio_url:
            print(f"Skipping {bvid} due to missing video or audio URL.")
            continue

        safe_title = video_data['title'].replace('/', '-')
        safe_owner_name = video_data['owner']['name'].replace('/', '-')
        video_filename = f"{safe_title}-{safe_owner_name}_video.mp4"
        audio_filename = f"{safe_title}-{safe_owner_name}_audio.mp3"
        output_filename = f"{safe_title}-{safe_owner_name}.mp4" # Final merged video

        print(f"Downloading video: {video_data['title']}")
        video_downloaded = download_file(video_url, video_filename, headers)

        print(f"Downloading audio: {video_data['title']}")
        audio_downloaded = download_file(audio_url, audio_filename, headers)

        if video_downloaded and audio_downloaded:
           print(f"Merging video and audio for: {video_data['title']}")
           if merge_video_audio(video_filename, audio_filename, output_filename):
               print(f"Successfully downloaded and merged: {video_data['title']}")
               # Optionally remove video_filename and audio_filename
           else:
               print(f"Failed to merge video and audio for: {video_data['title']}")
        else:
           print(f"Skipping merge due to download failure for: {video_data['title']}")

if __name__ == "__main__":
    main()

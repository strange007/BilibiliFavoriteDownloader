# BilibiliFavoriteDownloader
Download all the videos in any favorite folder

## Description

This project provides a command-line tool to download videos from BiliBili. It allows you to download videos from a specified media list ( your favorite folder ) or by providing individual BVIDs (Bilibili Video IDs). The script downloads the video and audio separately and then merges them into a single MP4 file using FFmpeg.
- Here media list is a MEDIA_ID that can be get like the picture.
![image](https://github.com/user-attachments/assets/497e30e6-2a36-4d9d-be41-20362ff13fd4)

## Features

- Downloads videos from BiliBili using a media list ID or individual BVIDs.
- Downloads video and audio streams separately.
- Merges video and audio using FFmpeg.
- Includes progress bar for downloads.
- Handles errors gracefully.
- Uses `requests` for HTTP requests and `tqdm` for progress display.

## Requirements

- Python 3.x
- `requests` library
- `tqdm` library
- FFmpeg (installed and available in your system's PATH)

## Installation

1.  Install FFmpeg:

    -   On Debian/Ubuntu: `sudo apt install ffmpeg`
    -   On macOS (using Homebrew): `brew install ffmpeg`
    -   On Windows: Download a pre-built binary and add it to your PATH.

2.  Clone the repository:

    ```
    git clone [your_repository_url]
    cd [your_repository_directory]
    ```

3.  Install the Python dependencies:

    ```
    pip install -r requirements.txt
    ```

## Usage

1.  Set the `MEDIA_ID` variable in the script to the ID of the BiliBili media id (the favorite folder id) you want to download from.

2.  Run the script:

    ```
    python your_script_name.py
    ```

    Alternatively, you can specify individual BVIDs:

    ```
    python your_script_name.py -b BV1xxxx BV1yyyy
    ```

## Configuration

-   `MEDIA_ID`:  Set this variable in the script to your desired BiliBili media list ID.
-   `qn`: Adjust the `qn` variable in the `fetch_video_url` function to select different video quality (if available).


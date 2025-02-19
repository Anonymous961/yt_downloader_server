from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from flask_cors import CORS
import traceback
import os

app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "*"}}, supports_credentials=True)

@app.route('/health')
def health_check():
    return jsonify({'status': 'temp check 4'})

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Get the YouTube URL from the request body
        data = request.json
        url = data.get('url')
        user_cookies = data.get('cookies')

        # Validate the URL
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        COOKIES_PATH = os.path.join(os.getcwd(), "cookies.txt")  # Get full path

        if user_cookies:
            with open(COOKIES_PATH, "w", encoding="utf-8") as f:
                f.write(user_cookies)

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best',  # Download the best quality available
            'outtmpl': '%(title)s.%(ext)s',  # Output file name
            'noplaylist': True,  # Ensure only a single video is downloaded
            'cookies': COOKIES_PATH,  # Use full path
        }

        # Fetch video details
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # Set download=False to fetch details only
            video_title = info_dict.get('title', None)
            formats = info_dict.get('formats', [])

            # Extract available formats
            available_formats = []
            for f in formats:
                format_info = {
                    'format': f.get('format'),
                    'url': f.get('url'),
                    'filesize': f.get('filesize'),
                    'acodec': f.get('acodec'),  # Audio codec
                    'vcodec': f.get('vcodec'),  # Video codec
                }
                available_formats.append(format_info)

            # Return the video details and formats
            return jsonify({
                'title': video_title,
                'formats': available_formats,
            })

    except Exception as e:
        # Handle any errors
        error_message = traceback.format_exc()
        return jsonify({'error': str(e), 'trace': error_message,"cookies":user_cookies, "xtra": "just checking"}), 500

if __name__ == '__main__':
    app.run(debug=True)
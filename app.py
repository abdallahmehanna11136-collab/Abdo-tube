import html
from flask import Flask, request, Response
from flask_cloudflared import run_with_cloudflared
import yt_dlp
import requests

app = Flask(__name__)
run_with_cloudflared(app) # تشغيل النفق تلقائياً

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Abdo Tube - عبده تيوب</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="background-color: #000137; color: white; text-align: center; font-family: Arial; padding-top: 20px;">
        <h2>📺 عبده تيوب - Abdo Tube</h2>
        <p>Search for any video:</p>
        <br>
        <form action="/search" method="get">
            <input type="text" name="query" placeholder="Type here..." style="padding: 8px; width: 80%; font-size: 16px;"><br><br>
            <input type="submit" value="Search Now" style="padding: 10px 20px; background-color: red; color: white; border: none; font-size: 16px; font-weight: bold;">
        </form>
    </body>
    </html>
    """

@app.route('/search')
def search():
    query = request.args.get('query', '')
    videos = []
    
    ydl_opts = {
        'default_search': 'ytsearch30',
        'quiet': True,
        'extract_flat': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch30:{query}", download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('id'):
                        videos.append({
                            'title': entry.get('title', 'Video'),
                            'id': entry.get('id', '')
                        })
        except Exception as e:
            print("Search error:", e)

    output = f"""
    <html>
    <head>
        <title>Abdo Tube - Results</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="google-site-verification" content="كود_جوجل_بتاعك" />
    </head>
    <body style="background-color: #000137; color: white; text-align: center; font-family: Arial; padding: 15px;">
        <h3>Results for: {html.escape(query)}</h3>
        <p style="font-size:12px; color:gray;">Found {len(videos)} videos</p>
        <hr>
    """
    
    if not videos:
        output += "<p style='color:red;'>No videos found! Try another word.</p>"
    else:
        for vid in videos:
            output += f"""
            <div style="background-color: #112255; padding: 10px; margin: 10px auto; width: 90%; text-align: left;">
                <p style="font-size: 13px; font-weight: bold;">📺 {html.escape(vid['title'])}</p>
                <a href="/download/{vid['id']}" style="color: #00ff00; text-decoration: none; font-size: 13px; font-weight: bold;">📥 Download & Play</a>
            </div>
            """
            
    output += '<br><a href="/" style="color: red; font-weight: bold; text-decoration: none;">⬅️ Go Back</a></body></html>'
    return output

@app.route('/download/<video_id>')
def download_video(video_id):
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'format': 'worst[ext=mp4]/worst',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            direct_url = info.get('url', '')
            req = requests.get(direct_url, stream=True)
            return Response(
                req.iter_content(chunk_size=1024*1024),
                headers={
                    'Content-Disposition': f'attachment; filename="{video_id}.mp4"',
                    'Content-Type': 'video/mp4'
                }
            )
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run()

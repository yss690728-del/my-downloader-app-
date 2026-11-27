from flask import Flask, request, render_template_string
import yt_dlp
import os
import tempfile
import base64

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>برنامج التحميل</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #121212; color: white; text-align: center; padding: 20px; }
        .container { background-color: #1e1e1e; padding: 30px; border-radius: 15px; max-width: 400px; margin: auto; }
        h1 { color: #4CAF50; }
        input[type="text"] { width: 90%; padding: 10px; margin: 15px 0; border-radius: 5px; border: none; font-size: 16px; }
        button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; margin-top: 10px; }
        #status { margin-top: 15px; font-weight: bold; color: #FFC107; }
        a { display: block; margin-top: 15px; color: #4CAF50; font-weight: bold; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📥 التحميل السريع</h1>
        <input type="text" id="url" placeholder="الصق الرابط هنا...">
        <button onclick="download('video')">تحميل كفيديو 🎥</button>
        <button onclick="download('audio')" style="background-color: #2196F3;">تحميل كأغنية 🎵</button>
        <div id="status"></div>
        <div id="download-link"></div>
    </div>
    <script>
        function download(type) {
            let url = document.getElementById('url').value;
            if(!url) { alert('الرجاء إدخال رابط!'); return; }
            document.getElementById('status').innerHTML = 'جاري التحميل... قد يستغرق دقيقة ⏳';
            document.getElementById('download-link').innerHTML = '';
            
            fetch('/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url, type: type })
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    document.getElementById('status').innerHTML = 'تم التحميل بنجاح! ✅';
                    let link = document.createElement('a');
                    link.href = 'data:application/octet-stream;base64,' + data.file_data;
                    link.download = data.filename;
                    link.innerHTML = 'اضغط هنا لحفظ الملف 💾';
                    document.getElementById('download-link').appendChild(link);
                } else {
                    document.getElementById('status').innerHTML = 'حدث خطأ: ' + data.error;
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    type_ = data.get('type')
    is_audio = (type_ == 'audio')
    
    download_dir = tempfile.mkdtemp()
    
    opts = {
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }
    
    if is_audio:
        opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        })
    else:
        opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if is_audio:
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            file_path = os.path.join(download_dir, os.path.basename(filename))
            
            with open(file_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
                
            return {"success": True, "filename": os.path.basename(filename), "file_data": file_data}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

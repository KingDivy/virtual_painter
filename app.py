from flask import Flask, render_template, Response
from virtualpainter import generate_frames
import os

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    print("[INFO] /video_feed route hit")
    try:
        return Response(generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print("[ERROR] in video_feed:", e)
        return "Error occurred", 500

if __name__ == '__main__':
    print("✅ Running Flask app... URL map:\n", app.url_map)
    app.run(debug=True)

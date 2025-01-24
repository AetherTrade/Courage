import webview
from app import create_app
import threading
import sys
import os

def run_flask():
    app = create_app()
    app.run(port=5555)

def get_asset_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Create a desktop window
    webview.create_window(
        'CourageFX Trading Bot',
        'http://127.0.0.1:5555',
        width=1200,
        height=800,
        min_size=(800, 600),
        background_color='#ffffff',
        resizable=True,
        fullscreen=False,
        frameless=False,
        easy_drag=True,
        text_select=True
    )
    webview.start()

if __name__ == '__main__':
    main() 
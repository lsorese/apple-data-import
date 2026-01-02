#!/usr/bin/env python3
"""
Simple HTTP server to view the Apple Music analysis website.

This is needed because browsers block fetch() requests when opening
HTML files directly with file:// protocol.
"""

import http.server
import socketserver
import os
import sys

PORT = 8000
DIRECTORY = "outputs"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    # Check if outputs directory exists
    if not os.path.exists(DIRECTORY):
        print(f"Error: '{DIRECTORY}' directory not found")
        print("Please run the analyzer first: python3 analyze_music.py")
        sys.exit(1)

    # Check if data.json exists
    data_file = os.path.join(DIRECTORY, "data.json")
    if not os.path.exists(data_file):
        print(f"Warning: '{data_file}' not found")
        print("Please run the analyzer first: python3 analyze_music.py")
        print()

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🎵 Apple Music Analysis Server")
        print(f"================================")
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Serving files from: {DIRECTORY}/")
        print()
        print(f"Open in your browser: http://localhost:{PORT}")
        print()
        print("Press Ctrl+C to stop the server")
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()

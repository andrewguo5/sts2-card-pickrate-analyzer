#!/usr/bin/env python3
"""
Simple HTTP server for serving the frontend static files.
Used by Railway to serve the React app.
"""
import http.server
import socketserver
import os

PORT = int(os.getenv('PORT', 8000))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='.', **kwargs)

print(f"Starting frontend server on port {PORT}...")

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}")
    httpd.serve_forever()

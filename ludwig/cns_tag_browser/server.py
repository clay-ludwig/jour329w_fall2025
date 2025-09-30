#!/usr/bin/env python3
"""
Simple Python HTTP server for CNS Tag Browser
Serves the web app and provides API endpoint for tags data
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class TagBrowserHandler(SimpleHTTPRequestHandler):
    """Custom handler to serve static files and API endpoints"""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        """Add CORS headers and cache control"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Disable caching for API endpoints
        if self.path.startswith('/api/'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        
        super().end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        
        # API endpoint for tags data
        if self.path == '/api/tags':
            self.serve_tags_data()
        else:
            # Serve static files
            super().do_GET()
    
    def serve_tags_data(self):
        """Serve the tags.json file from the data directory"""
        try:
            # Path to tags.json (3 levels up, then into data/)
            tags_path = Path(__file__).parent.parent.parent / 'data' / 'tags.json'
            
            if not tags_path.exists():
                self.send_error(404, 'Tags data not found')
                return
            
            # Read and send the JSON data
            with open(tags_path, 'r', encoding='utf-8') as f:
                tags_data = json.load(f)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Write JSON data
            self.wfile.write(json.dumps(tags_data).encode('utf-8'))
            
            print(f"Served {len(tags_data)} tags")
            
        except Exception as e:
            print(f"Error serving tags: {e}")
            self.send_error(500, f'Error loading tags: {str(e)}')
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.address_string()}] {format % args}")


def run_server(port=8000):
    """Start the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, TagBrowserHandler)
    
    print(f"\n{'='*60}")
    print(f"CNS Tag Browser Server")
    print(f"{'='*60}")
    print(f"Server running at: http://localhost:{port}")
    print(f"Open your browser and navigate to the URL above")
    print(f"Press Ctrl+C to stop the server")
    print(f"{'='*60}\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    # Default port is 8000, but can be changed via environment variable
    port = int(os.environ.get('PORT', 8000))
    run_server(port)

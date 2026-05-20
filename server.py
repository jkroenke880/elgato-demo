#!/usr/bin/env python3
"""Serves the Elgato demo site on port 8082."""
import http.server
import os

PORT = int(os.environ.get('PORT', 8082))
DEMO_DIR = os.path.dirname(os.path.abspath(__file__))


class ElgatoHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DEMO_DIR, **kwargs)

    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    with http.server.HTTPServer(('', PORT), ElgatoHandler) as httpd:
        print('Elgato demo running on http://localhost:{}'.format(PORT))
        httpd.serve_forever()

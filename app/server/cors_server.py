import http.server
import socketserver
import sys
import logging


logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def log_message(self, format, *args):
        logger.fatal(f"Request: {self.client_address} - {format % args}")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    with socketserver.TCPServer(("0.0.0.0", port), CORSRequestHandler) as httpd:
        httpd.serve_forever()

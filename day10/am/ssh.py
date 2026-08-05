from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            status = 200
            body = b'{"status":"ok"}'
            logging.info("GET /health 200")


        elif self.path == "/error":
            status = 500
            body = b'{"status":"Error"}'
            logging.error("GET /Error 500 test Error")

        else:
            status = 404
            body = b'{"message":"not found"}'

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


logging.info("Server started on port 8000")
HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
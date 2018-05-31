"""
A server that resonds to requests for bounded prime sequences.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from primes import primes
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs

import logging
import redis

log = logging.getLogger("server")
logging.basicConfig(filename="logfile.txt", level=logging.DEBUG)
stderrLogger=logging.StreamHandler()
stderrLogger.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
logging.getLogger().addHandler(stderrLogger)

r = redis.Redis(host='localhost', port=6379)

class PrimeHTTPServer(ThreadingMixIn, HTTPServer):
    """ Handle requests in separate threads"""

class PrimeHTTPRequestHandler(BaseHTTPRequestHandler):
    LO = 'lo'
    HI = 'hi'
    MSG_400 = "Missing query string"
    EXP_400 = "Requests must contain queries of the following form: /?lo=<int>&hi=<int>"
    MSG_300 = "Malformed query string"
    EXP_300 = "Requests must contain queries of the following form: /?lo=<int>&hi=<int>"

    def _determine_status(self, query):
        self.status = 200

        if not query:
            self.status = 400
            self.message = self.MSG_400
            self.explain = self.EXP_400
        elif self.LO not in query or self.HI not in query:
            self.status = 300
            self.message = self.MSG_300
            self.explain = self.EXP_300

        return self.status

    def _headers(self):
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        log.info("GET Request: %s" % self.path)
        query = parse_qs(urlparse(self.path).query)
        status = self._determine_status(query)

        if status != 200:
            self.send_error(status, message=self.message, explain=self.explain)
            return

        lo = int(query[self.LO][0])
        hi = int(query[self.HI][0])

        cached = r.get((lo, hi))

        if cached is not None:
            log.info("Found answer in cache")
            response = cached
        else:
            log.info("Calculating and caching answer")
            response = ','.join(list(map(str, primes(lo, hi)))).encode()
            r.set((lo,hi), response)

        log.info("Writing back: %s" % bytes.decode(response))

        self.send_response(status)
        self._headers()
        self.wfile.write(response)

def run(port=8000):
    server = PrimeHTTPServer(('localhost', port), PrimeHTTPRequestHandler)
    log.info("Starting server")
    server.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=argv[1])
    else:
        run()

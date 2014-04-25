#!/usr/bin/env python2
# -*- coding: utf8 -*-
import os
import params
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogeneize_latex_encoding

# TODO :
# * custom port
# * allow remote

def bibtex2HTML(data):
    html = '<html><body>'
    for index in data:
        html += '<p>'+index+'</p>'
    html += '</body></html>'
    return html


PORT_NUMBER = 8080

class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if os.path.isfile(params.folder+'index.bib'):
            with open(params.folder+"index.bib", "r") as fh:
                bibtex = BibTexParser(fh, customization=homogeneize_latex_encoding)
            bibtex = bibtex.get_entry_dict()
            html = bibtex2HTML(bibtex)
        else:
            html = '<html><body><p>Not found.</p></body></html>'

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(html)
        return

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    try:
        server = HTTPServer(('127.0.0.1', PORT_NUMBER), myHandler)
        print('Webserver started : http://localhost:' + str(PORT_NUMBER))
        server.serve_forever()
    except KeyboardInterrupt:
        print('KeyboardInterrupt received, shutting down the webserver…')
        server.socket.close()

"""
MIT License

Copyright (c) 2023 thatsOven

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from qinp        import Compiler, encode
from json        import load
from flask       import *
from pathlib     import Path
from html.parser import HTMLParser
from markupsafe  import escape as _escape
import os

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

os.chdir(str(Path(__file__).parent.absolute()))

class CustomHTMLParser(HTMLParser):
    def __init__(self):
        self.compile    = False
        self.first      = True
        self.route      = False
        self.compiler   = Compiler()
        self.buf        = ""
        self.compileBuf = ""

        super().__init__()

    def __encodeBuffer(self):
        return encode(self.buf)

    def updateHtmlBuf(self):
        if self.first:
            self.first = False
            self.compiler.out += f"'{self.__encodeBuffer()}'\n"
        else:
            self.compiler.out += (" " * self.compiler.lastTabs) + f"_HTML_BUF+='{self.__encodeBuffer()}'\n"

    def handle_starttag(self, tag, attrs):
        strAttrs = " ".join([f'{x[0]}="{x[1]}"' for x in attrs])

        if tag in ("qinp!", "qinp"):
            self.updateHtmlBuf()
            if not self.route:
                dictAttrs = {x[0]:x[1] for x in attrs}
                if "route" in dictAttrs:
                    self.route = True
                    self.compiler.out = f'@pinq.route("{dictAttrs["route"]}",methods=HTTP_METHODS)\n' + self.compiler.out

            self.buf = ""
            self.compile = True
        elif self.compile:
            if strAttrs == "":
                self.compileBuf += f"<{tag}>"
            else:
                self.compileBuf += f"<{tag} {strAttrs}>"
        else:
            if strAttrs == "":
                self.buf += f"<{tag}>"
            else:
                self.buf += f"<{tag} {strAttrs}>"

    def handle_endtag(self, tag):
        if tag in ("qinp!", "qinp"):
            self.compiler.compile(self.compileBuf)
            self.compile    = False
            self.compileBuf = ""
        elif self.compile:
            self.compileBuf += f"</{tag}>"
        else:
            self.buf += f"</{tag}>"

    def handle_data(self, data):
        if self.compile:
            self.compileBuf += data
        else:
            self.buf += data.replace("\n", "")

    def reset(self):
        self.compile    = False
        self.first      = True
        self.route      = False
        self.buf        = ""
        self.compileBuf = ""
        self.compiler.reset()

        super().reset()

def escape(obj):
    return str(_escape(str(obj)))

print("pinq! runtime v2023.4.19 - thatsOven")

if __name__ == "__main__":
    parser = CustomHTMLParser()
    pinq   = Flask("pinq! runtime")
    error  = False

    for f in os.listdir("source"): 
        path = os.path.join("source", f)
        if os.path.isfile(path) and any((f.endswith(".html"), f.endswith(".htm"), f.endswith(".qinp"))):
            print(f"Loading {path}")
            with open(path, "r") as source:
                toParse = source.read()

            parser.feed(toParse)

            if parser.buf != "":
                parser.updateHtmlBuf()

            parser.compiler.out += " return _HTML_BUF"

            if not parser.route:
                route = "/" + Path(f).as_posix()
                print(f"{path}'s route was not found. assigning dummy route: {route}")

                if f.endswith(".qinp"):
                    parser.compiler.headers += f'@pinq.route("{route}",methods=HTTP_METHODS)\n'
                else:
                    parser.compiler.headers += f'@pinq.route("{route}")\n'

            if not parser.compiler.hadError:
                exec(parser.compiler.headers + parser.compiler.out)
            else:
                error = True

            parser.reset()

    with open("config.json", "r") as f:
        conf = load(f)
    
    if "ip" not in conf:
        print("Invalid IP in config.json! Using default.")
        conf["ip"] = "0.0.0.0"

    if "port" not in conf:
        print("Invalid port in config.json! Using default.")
        conf["port"] = 8080

    if not error:
        pinq.run(host = conf["ip"], port = conf["port"])
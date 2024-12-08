"""
MIT License

Copyright (c) 2023 Amari Calipso

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

# qinp!'s implementation of a basic language for MongoDB

import pymongo, colorama

class Token:
    def __init__(self, tok, line = 0, pos = 0, tokens = None):
        self.tok     : str = tok
        self.line    : int = line
        self.pos     : int = pos
        self.maxline : int = 1000

        self.tokens : Tokens = tokens

    def copy(self):
        tok = Token(self.tok, self.line, self.pos, self.tokens)
        tok.maxline = self.maxline
        return tok

    def __getlines(self):
        if self.line <= 3:
            return range(1, min(6, self.maxline))

        if self.line >= self.maxline - 3:
            return range(self.maxline - 5, self.maxline)

        return range(self.line - 3, self.line + 2)

    def __message(self, type_, color, msg):
        if self.tokens is None: print(color + f"{type_}{colorama.Style.RESET_ALL}:", msg)
        else:
            maxlineLen = len(str(self.maxline))

            print(color + f"{type_}{colorama.Style.RESET_ALL} (line {self.line - 1}, pos {self.pos}):", msg)

            for line in self.__getlines():
                if line == self.line - 1:
                    print(
                        f"{str(line).rjust(maxlineLen)} | " + self.tokens.source[line].rstrip() + "\n" +
                        (" " * maxlineLen) + " |" + (" " * (self.pos + 1)) + color + ("^" * len(self.tok)) + colorama.Style.RESET_ALL
                    )

                    continue

                print(f"{str(line).rjust(maxlineLen)} | " + self.tokens.source[line].rstrip())

    def error(self, msg):
        self.__message("error", colorama.Fore.RED, msg)

    def warning(self, msg):
        self.__message("warning", colorama.Fore.LIGHTYELLOW_EX, msg)

class Tokens:
    def __init__(self, source):
        if   type(source) is str:
            self.tokens = self.tokenize(source)
            self.source = source.split("\n")
        elif type(source) is list:
            self.tokens = source
            self.source = []

        self.pos = 0

    def copy(self):
        tmp = Tokens(self.tokens)
        tmp.pos    = self.pos
        tmp.source = self.source

        return tmp

    def isntFinished(self):
        return self.pos < len(self.tokens)

    def peek(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]

    def next(self) -> Token:
        if self.pos < len(self.tokens):
            tmp = self.tokens[self.pos]
            self.pos += 1
            return tmp

        self.tokens[self.pos - 1].error("invalid syntax: the expression wasn't properly closed. no tokens remaining")

    def last(self) -> Token:
        return self.tokens[self.pos - 1]

    @classmethod
    def verifyTok(self, tokens: list, first: Token, next: Token, opts):
        if next.tok in opts:
            first.tok += next.tok
            tokens.append(first)
            return True

        tokens.append(first)
        return False

    def join(self):
        buf = ""
        lastIsIdentifier = False
        lastIdentifier   = None
        for token in self.tokens:
            if token.tok.isidentifier() or token.tok[0].isidentifier():
                if lastIsIdentifier:
                    buf += " " + token.tok
                    lastIdentifier = token.tok
                    continue

                lastIsIdentifier = True
            else:
                lastIsIdentifier = token.tok.isdigit()

                if lastIdentifier is not None and (lastIdentifier + token.tok).isidentifier():
                    buf += " " + token.tok
                    lastIdentifier = token.tok
                    continue

            lastIdentifier = token.tok
            buf += token.tok

        return buf

    def tokenize(self, source):
        line = 1
        pos  = 0
        tmp           = [Token("", line, pos, self)]
        inLineComment = False
        inString      = False
        inStringAlt   = False
        lastSym       = False

        for ch in source:
            if inLineComment:
                if ch == "\n":
                    inLineComment = False
                    line += 1
                    pos   = 0
                    tmp.append(Token("", line, pos, self))
                    continue

                pos += 1
                continue

            match ch:
                case " " | "\t":
                    if inString or inStringAlt: tmp[-1].tok += ch
                    else:
                        tmp.append(Token("", line, pos + 1, self))
                case "#":
                    if inString or inStringAlt: tmp[-1].tok += ch
                    else:
                        inLineComment = True
                case "\n":
                    line += 1
                    pos   = 0

                    if inString or inStringAlt: tmp[-1].tok += ch
                    else:
                        tmp.append(Token("", line, pos, self))
                        continue
                case '"':
                    if inString:
                        tmp[-1].tok += ch
                        inString = False
                    elif inStringAlt:
                        tmp[-1].tok += ch
                    else:
                        tmp.append(Token(ch, line, pos, self))
                        inString = True
                case "'":
                    if inStringAlt:
                        tmp[-1].tok += ch
                        inStringAlt = False
                    elif inString:
                        tmp[-1].tok += ch
                    else:
                        tmp.append(Token(ch, line, pos, self))
                        inStringAlt = True
                case _:
                    if inString or inStringAlt:
                        tmp[-1].tok += ch
                    elif ch.isalnum() or ch == "_":
                        if lastSym:
                            lastSym = False
                            tmp.append(Token(ch, line, pos, self))
                        else:
                            tmp[-1].tok += ch
                    else:
                        lastSym = True
                        tmp.append(Token(ch, line, pos, self))

            pos += 1

        i = 0
        while i < len(tmp):
            if tmp[i].tok == "":
                tmp.pop(i)
            else:
                tmp[i].maxline = line
                i += 1

        tokens = []
        i = 0
        while i < len(tmp) - 1:
            token = tmp[i]
            i += 1

            match token.tok:
                case "!":
                    if self.verifyTok(tokens, token, tmp[i], ("=",)): i += 1
                    continue
                case "*":
                    if self.verifyTok(tokens, token, tmp[i], ("*",)): i += 1
                    continue
                case "/":
                    if self.verifyTok(tokens, token, tmp[i], ("/",)): i += 1
                    continue
                case ">":
                    if self.verifyTok(tokens, token, tmp[i], (">",)): i += 1
                    continue
                case "<":
                    if self.verifyTok(tokens, token, tmp[i], ("<",)): i += 1
                    continue
                case "f" | "r" | "b" | "fr" | "br" | "rf" | "rb":
                    if tmp[i].tok.startswith('"') or tmp[i].tok.startswith("'"):
                        token.tok += tmp[i].tok
                        i += 1
                case '""':
                    if tmp[i].tok.startswith('"'):
                        token.tok += tmp[i].tok
                        i += 1
                    elif len(tokens) > 0 and tokens[-1].tok.endswith('"'):
                        tokens[-1].tok += token.tok
                        continue
                case "''":
                    if tmp[i].tok.startswith("'"):
                        token.tok += tmp[i].tok
                        i += 1
                    elif len(tokens) > 0 and tokens[-1].tok.endswith("'"):
                        tokens[-1].tok += token.tok
                        continue

            tokens.append(token)

        if i < len(tmp):
            lastTok = tmp[len(tmp) - 1]

            match lastTok.tok:
                case '""':
                    if tokens[-1].tok.endswith('"'):
                        tokens[-1].tok += lastTok.tok
                case "''":
                    if tokens[-1].tok.endswith("'"):
                        tokens[-1].tok += lastTok.tok
                case _:
                    tokens.append(lastTok)

        return tokens

class _SortMode:
    NO, ASC, DESC = 0, 1, -1

class MonQiError(Exception): ...

class MonQi:
    def __flagsErrorNoRel(self, kw, msg):
        if self.nextCount:
            self.nextCount = False
            self.__error(f'"COUNTOF" flag cannot be used with {msg} statement', kw)

        if self.nextLimited is not None:
            self.nextLimited = None
            self.__error(f'"LIMITED" flag cannot be used with {msg} statement', kw)

        if self.nextSorted != _SortMode.NO:
            self.nextSorted = _SortMode.NO
            self.__error(f'"SORTED" flag cannot be used with {msg} statement', kw)

    def __flagsError(self, kw, msg):
        if self.nextRelative:
            self.nextRelative = False
            self.__error(f'"REL" flag cannot be used with {msg} statement', kw)

        self.__flagsErrorNoRel(kw, msg)

    def __use(self, tokens: Tokens):
        '''
        USE ["mydb"]["mycollection"];
        '''

        self.__flagsErrorNoRel(tokens.last(), "USE")
        which = self.__getUntilNotInExpr(';', tokens, True, advance = False)[1]
        if self.nextRelative:
            self.nextRelative = False
            self.current = eval("self.current" + Tokens(which).join())
        else:
            self.current = eval("self.conn" + Tokens(which).join())

    def __new(self, tokens: Tokens):
        '''
        NEW DB myDb

        NEW COLLECTION myCollection
        '''

        self.__flagsErrorNoRel(tokens.last(), "NEW")
        next = tokens.next()
        name = tokens.next()
        match next.tok.lower():
            case 'db':
                self.current = eval(f"self.conn['{name.tok}']")
            case 'collection':
                if self.nextRelative:
                    self.nextRelative = False
                    self.current[name.tok]
                else:
                    self.conn[name.tok]

    def __insert(self, tokens: Tokens):
        '''
        INSERT [
            {"name": "Amy",     "address": "Apple st 652"},
            {"name": "Hannah",  "address": "Mountain 21"},
            {"name": "Michael", "address": "Valley 345"},
            {"name": "Sandy",   "address": "Ocean blvd 2"},
        ]
        '''

        self.__flagsError(tokens.last(), "INSERT")
        self.__checkDirectNext('[', 'INSERT statement', tokens)
        values = Tokens(self.__getSameLevelParenthesis('[', ']', tokens)).join()
        self.current.insert_many(eval(f"[{values}]"))

    def __drop(self, tokens: Tokens):
        '''
        DROP
        '''

        self.__flagsError(tokens.last(), "DROP")
        if not self.current.drop():
            raise MonQiError('DROP referenced a nonexistent collection')

    def __relative(self, tokens: Tokens):
        '''
        REL
        '''

        if self.nextRelative:
            self.__error('"REL" flag was used twice, remove this flag', tokens.last())
        else:
            self.nextRelative = True

    def __count(self, tokens: Tokens):
        '''
        COUNTOF
        '''

        if self.nextCount:
            self.__error('"COUNTOF" flag was used twice, remove this flag', tokens.last())
        else:
            self.nextCount = True

    def __sorted(self, tokens: Tokens):
        '''
        SORTED ASCENDING BY "name"
        SORTED DESCENDING BY "address"
        SORTED NO
        '''

        if self.nextSorted != _SortMode.NO:
            self.__error('"SORTED" flag was used twice, remove this flag', tokens.last())
        else:
            next = tokens.next()
            match next.tok.lower():
                case "ascending" | "asc":
                    tmp = _SortMode.ASC
                case "descending" | "desc":
                    tmp = _SortMode.DESC
                case "no":
                    tmp = _SortMode.NO
                case _:
                    self.__error('unrecognized identifier for "SORTED" flag', tokens.last())
                    tmp = _SortMode.NO

            if tmp == _SortMode.NO:
                self.nextSorted = _SortMode.NO
                return

            next = tokens.peek()
            if next is not None and next.tok.lower() == "by":
                tokens.next()
                self.nextSorted = (tmp, eval(tokens.next().tok))

    def __limited(self, tokens: Tokens):
        '''
        LIMITED 100
        '''

        if self.nextLimited is not None:
            self.__error('"LIMITED" flag was used twice, remove this flag', tokens.last())
        else:
            next = tokens.next()
            try:
                tmp = int(next.tok)
            except:
                self.__error('"LIMITED" flag requires an integer', tokens.last())
            else:
                self.nextLimited = tmp

    def __all(self, *args):
        return eval('{"$and":' + str(args) + '}')

    def __nor(self, *args):
        return eval('{"$nor":' + str(args) + '}')

    def __any(self, *args):
        return eval('{"$or":' + str(args) + '}')

    def __not(self, arg):
        return eval('{"$not":' + str(arg) + '}')

    def __matchesRegex(self, attr, expr):
        return eval('{' + f'"{attr}":' + '{"$regex":' + f'"{expr}"' + '}}')

    def __eq(self, attr, value):
        return eval('{' + f'"{attr}":' + '{"$eq":' + f'"{value}"' + '}}')

    def __gt(self, attr, value):
        return eval('{' + f'"{attr}":' + '{"$gt":' + f'"{value}"' + '}}')

    def __gte(self, attr, value):
        return eval('{' + f'"{attr}":' + '{"$gte":' + f'"{value}"' + '}}')

    def __lt(self, attr, value):
        return eval('{' + f'"{attr}":' + '{"$lt":' + f'"{value}"' + '}}')

    def __lte(self, attr, value):
        return eval('{' + f'"{attr}":' + '{"$lte":' + f'"{value}"' + '}}')

    def __parseQuery(self, query):
        equal         = self.__eq
        EQUAL         = self.__eq
        greater       = self.__gt
        GREATER       = self.__gt
        greater_equal = self.__gte
        GREATER_EQUAl = self.__gte
        less          = self.__lt
        LESS          = self.__lt
        less_equal    = self.__lte
        LESS_EQUAL    = self.__lte
        all           = self.__all
        ALL           = self.__all
        any           = self.__any
        ANY           = self.__any
        nor           = self.__nor
        NOR           = self.__nor
        NOT           = self.__not
        matches_regex = self.__matchesRegex
        MATCHES_REGEX = self.__matchesRegex

        return eval(query)

    def __fetchFlags(self, query, fields, kw):
        if self.nextCount:
            self.nextCount = False

            if self.nextSorted != _SortMode.NO:
                self.nextSorted = _SortMode.NO
                self.__error('cannot use "SORTED" flag when using "COUNTOF" flag', kw)

            if self.nextLimited is not None:
                lim = self.nextLimited
                self.nextLimited = None
                return self.current.find(query, fields).limit(lim).count()
            else:
                return self.current.find(query, fields).count()
        elif self.nextLimited is not None:
            lim = self.nextLimited
            self.nextLimited = None

            if self.nextSorted != _SortMode.NO:
                  sortConfig = self.nextSorted
                  self.nextSorted = _SortMode.NO
                  return self.current.find(query, fields).limit(lim).sort(sortConfig[1], sortConfig[0])
            else: return self.current.find(query, fields).limit(lim)
        elif self.nextSorted != _SortMode.NO:
            sortConfig = self.nextSorted
            self.nextSorted = _SortMode.NO
            return self.current.find(query, fields).sort(sortConfig[1], sortConfig[0])
        else:
            return self.current.find(query, fields)

    def __fetch(self, tokens: Tokens):
        '''
        FETCH {"address", "name"}

        FETCH {"address", "name"} WITH {"address": "Valley 345"};
        '''

        kw = tokens.last()
        self.__checkDirectNext('{', 'FETCH statement', tokens)
        attrs = Tokens(self.__getSameLevelParenthesis('{', '}', tokens)).join()
        if attrs != "":
            fields = eval('{' + (':1,'.join(attrs.split(','))) + ":1}")
        else: fields = {}

        next = tokens.peek()
        if next is not None and next.tok.lower() == 'with':
            tokens.next()
            query = self.__parseQuery(Tokens(self.__getUntilNotInExpr(';', tokens, True, advance = False)[1]).join())
            return self.__fetchFlags(query, fields, kw)
        return self.__fetchFlags({}, fields, kw)

    def __editGen(self, fn):
        '''
        EDIT {"address": "Valley 345"} VALUES {"address": "Canyon 123", ...};

        EDIT_ONE {"address": "Valley 345"} VALUES {"address": "Canyon 123", ...};
        '''

        def __fn(tokens: Tokens):
            self.__flagsError(tokens.last(), "EDIT")
            query  = self.__parseQuery(Tokens(self.__getUntilNotInExpr('values', tokens, True, advance = False)[1]).join())
            values = eval(Tokens(self.__getUntilNotInExpr(';', tokens, True, advance = False)[1]).join())
            self.current.__getattr__(fn)(query, values)
        return __fn

    def __deleteGen(self, fn):
        '''
        DELETE

        DELETE WITH {"address": "Valley 345"};

        DELETE_ONE

        DELETE_ONE WITH {"address": "Valley 345"};
        '''

        def __fn(tokens: Tokens):
            self.__flagsError(tokens.last(), "DELETE")
            next = tokens.peek()
            if next is not None and next.tok.lower() == 'with':
                tokens.next()
                query = Tokens(self.__getUntilNotInExpr(';', tokens, True, advance = False)[1]).join()
                self.current.__getattr__(fn)(self.__parseQuery(query))
            self.current.__getattr__(fn)({})
        return __fn

    def __init__(self, *args, **kwargs):
        self.conn     = pymongo.MongoClient(*args, **kwargs)
        self.current  = None
        self.hadError = False

        self.nextSorted   = _SortMode.NO
        self.nextLimited  = None
        self.nextRelative = False
        self.nextCount    = False

        self.statementHandlers = {
            "use":        self.__use,
            "insert":     self.__insert,
            "new":        self.__new,
            "fetch":      self.__fetch,
            "edit_one":   self.__editGen('update_one'),
            "edit":       self.__editGen('update_many'),
            "delete_one": self.__deleteGen('delete_one'),
            "delete":     self.__deleteGen('delete_many'),
            "drop":       self.__drop,
            "sorted":     self.__sorted,
            "limited":    self.__limited,
            "rel":        self.__relative,
            "countof":    self.__count
        }

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def __error(self, msg, token : Token):
        self.hadError = True
        token.error(msg)

    def __checkDirectNext(self, ch, msg, tokens : Tokens):
        next = tokens.next()
        if next.tok != ch:
            self.__error(f'invalid syntax: expecting "{ch}" directly after {msg}', next)
            next = self.getUntil(ch, tokens)

        return next

    def __getUntilNotInExpr(self, ch, tokens : Tokens, buffer = False, errorNotFound = True, advance = True, unallowed = []):
        if type(ch) is str:
            ch = (ch, )

        rdBrack = 0
        sqBrack = 0
        crBrack = 0
        lastRdBrack = tokens.peek()
        lastSqBrack = tokens.peek()
        lastCrBrack = tokens.peek()
        next = tokens.peek()

        buf = []
        while tokens.isntFinished():
            next = tokens.next()

            match next.tok:
                case "(":
                    lastRdBrack = next
                    rdBrack += 1
                case ")":
                    lastRdBrack = next
                    rdBrack -= 1
                case "[":
                    lastSqBrack = next
                    sqBrack += 1
                case "]":
                    lastSqBrack = next
                    sqBrack -= 1
                case "{":
                    if "{" not in ch:
                        lastCrBrack = next
                        crBrack += 1
                case "}":
                    if "{" not in ch:
                        lastCrBrack = next
                        crBrack -= 1
                case "\\":
                    if tokens.isntFinished():
                        next = tokens.next()
                    else:
                        self.__error("cannot escape here", next)

                        if buffer: return next, buf
                        else:      return next

                    continue

            if next.tok in unallowed:
                if advance and tokens.isntFinished():
                    next = tokens.next()

                if buffer: return "", buf
                else:      return ""

            if rdBrack == 0 and sqBrack == 0 and crBrack == 0:
                if next.tok.lower() in ch:
                    if advance and tokens.isntFinished():
                        next = tokens.next()

                    if buffer: return next, buf
                    else:      return next

            buf.append(next)

        if rdBrack != 0:
            if lastRdBrack is None:
                self.__error("unbalanced brackets ()", tokens.tokens[-1])
            else:
                self.__error("unbalanced brackets ()", lastRdBrack)

        if sqBrack != 0:
            if lastSqBrack is None:
                self.__error("unbalanced brackets []", tokens.tokens[-1])
            else:
                self.__error("unbalanced brackets []", lastSqBrack)

        if crBrack != 0:
            if lastCrBrack is None:
                self.__error("unbalanced brackets {}", tokens.tokens[-1])
            else:
                self.__error("unbalanced brackets {}", lastCrBrack)

        if errorNotFound:
            if next is None:
                self.__error(f'expecting character(s) {ch}', Token(""))
            else:
                self.__error(f'expecting character(s) {ch}', next)

        if buffer: return "", buf
        else:      return ""

    def __getSameLevelParenthesis(self, openCh, closeCh, tokens : Tokens):
        pCount = 1
        buf = []
        lastParen = tokens.peek()
        if lastParen is None:
            self.__error('unbalanced parenthesis "' + openCh + closeCh + '"', tokens.tokens[-1])
            return []

        while tokens.isntFinished():
            next = tokens.next()

            if   next.tok == openCh:
                lastParen = next
                pCount += 1
            elif next.tok == closeCh:
                lastParen = next
                pCount -= 1

            if pCount == 0:
                return buf

            buf.append(next)

        self.__error('unbalanced parenthesis "' + openCh + closeCh + '"', lastParen)
        return buf

    def __compiler(self, tokens: Tokens):
        while tokens.isntFinished():
            next = tokens.next()

            lower = next.tok.lower()
            if lower in self.statementHandlers:
                tmp = self.statementHandlers[lower](tokens)
            else:
                self.__error("unknown statement", next)

        return tmp

    def execute(self, code):
        self.hadError = False

        self.tokens = Tokens(code)
        tmp = self.__compiler(self.tokens)

        if self.hadError:
            raise MonQiError()

        return tmp
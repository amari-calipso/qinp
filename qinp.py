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

import colorama

SET_OPS = ("+=", "-=", "**=", "//=", "*=", "/=", "%=", "&=", "|=", "^=", ">>=", "<<=", "@=", "=")

MAGIC_METHODS = {
    "new": "__init__",
    "create": "__new__",
    "delete": "__del__",
    "represent": "__repr__",
    "string": "__str__",
    "bytes": "__bytes__",
    "format": "__format__",
    "hash": "__hash__",
    "boolean": "__bool__",
    "getattribute": "__getattribute__",
    "setattribute": "__setattr__",
    "delattribute": "__delattr__",
    "setname": "__set_name__",
    "get": "__get__",
    "set": "__set__",
    "delete": "__delete__",
    "isinstance": "__instancecheck__",
    "issubclass": "__subclasscheck__",
    "call": "__call__",
    "length": "__len__",
    "iterable": "__iter__",
    "next": "__next__",
    "reverse": "__reversed__",
    "contains": "__contains__",
    "absolute": "__abs__",
    "complex": "__complex__",
    "integer": "__int__",
    "float": "__float__",
    "index": "__index__",
    "round": "__round__",
    "truncate": "__trunc__",
    "floor": "__floor__",
    "ceil": "__ceil__",
    "enter": "__enter__",
    "exit": "__exit__",
    "await": "__await__",
    "aiterable": "__aiter__",
    "anext": "__anext__",
    "aenter": "__aenter__",
    "aexit": "__aexit__"
}

OPERATORS = {
    "<": "__lt__",
    ">": "__gt__",
    "<=": "__le__",
    ">=": "__ge__",
    "==": "__eq__",
    "!=": "__ne__",
    "[]": "__getitem__",
    "[]=": "__setitem__",
    "del[]": "__delitem__",
    "+": "__add__",
    "r+": "__radd__",
    "+=": "__iadd__",
    "-": "__sub__",
    "r-": "__rsub__",
    "-=": "__isub__",
    "*": "__mul__",
    "r*": "__rmul__",
    "*=": "__imul__",
    "@": "__matmul__",
    "r@": "__rmatmul__",
    "@=": "__imatmul__",
    "/": "__truediv__",
    "r/": "__rtruediv__",
    "/=": "__itruediv__",
    "//": "__floordiv__",
    "r//": "__rfloordiv__",
    "//=": "__ifloordiv__",
    "%": "__mod__",
    "r%": "__rmod__",
    "%=": "__imod__",
    "divmod()": "__divmod__",
    "divmod(r)": "__rdivmod__",
    "**": "__pow__",
    "r**": "__rpow__",
    "**=": "__ipow__",
    "<<": "__lshift__",
    "r<<": "__rlshift__",
    "<<=": "__ilshift__",
    ">>": "__rshift__",
    "r>>": "__rrshift__",
    ">>=": "__irshift__",
    "&": "__and__",
    "r&": "__rand__",
    "&=": "__iand__",
    "^": "__xor__",
    "r^": "__rxor__",
    "^=": "__ixor__",
    "|": "__or__",
    "r|": "__ror__",
    "|=": "__ior__",
    "-x": "__neg__",
    "+x": "__pos__",
    "~": "__invert__"
}

def encode(buffer):
    return "".join(map(lambda char: rf"\u{ord(char):04x}", buffer))

class NameStack:
    def __init__(self):
        self.array = []

    def push(self, item):
        self.array.append(item)

    def pop(self):
        self.array.pop()

    def peek(self):
        if len(self.array) != 0:
            return self.array[-1]
        
        return (None, None)

    def lookfor(self, item):
        array = self.array.copy()

        while len(array) > 0:
            curr = array.pop()

            if curr[1] == item:
                return curr

    def getCurrentLocation(self):
        array = self.array.copy()
        names = [array.pop()]

        while len(array) != 0:
            curr = array.pop()
            names.append(curr)

        out = "in "
        for name in reversed(names):
            match name[1]:
                case "fn":
                    out += name[0] + "()."
                case _:
                    out += name[0] + "."

        return out.strip()[:-1]

class GenericLoop: pass

class CompLoop:
    def __init__(self, comp):
        self.comp = comp

class Token:
    def __init__(self, tok, line = 0, pos = 0, tokens = None):
        self.tok     : str = tok
        self.line    : int = line
        self.pos     : int = pos
        self.maxline : int = 1000

        self.tokens : Tokens = tokens

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
    def replaceTokens(self, tokens):
        i = 0
        while i < len(tokens):
            match tokens[i].tok:
                case "super":
                    if i + 1 < len(tokens) and tokens[i + 1].tok != "(":
                        tokens.insert(i + 1, Token("()"))
                        i += 1
            i += 1

        return tokens

    @classmethod
    def verifyTok(self, tokens: list, first: Token, next: Token, opt):
        if next.tok == opt:
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
            if token.tok.isidentifier():
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
                case "+":
                    if self.verifyTok(tokens, token, tmp[i], "="): i += 1
                    continue
                case "-":
                    if self.verifyTok(tokens, token, tmp[i], "="): i += 1
                    continue
                case "|":
                    if self.verifyTok(tokens, token, tmp[i], "="): i += 1
                    continue
                case "&":
                    if self.verifyTok(tokens, token, tmp[i], "="): i += 1
                    continue
                case "f" | "r" | "b" | "fr" | "br" | "rf" | "rb":
                    if tmp[i].tok.startswith('"') or tmp[i].tok.startswith("'"):
                        token.tok += tmp[i].tok
                        i += 1
                case "!" | ":" | "^" | "%" | "=":
                    if tmp[i].tok == "=":
                        token.tok += tmp[i].tok
                        i += 1
                case "*":
                    if tmp[i].tok in ("*", "="):
                        if tmp[i].tok == "*":
                            next = tmp[i]
                            i += 1

                            if i < len(tmp) and tmp[i].tok == "=":
                                token.tok += next.tok + tmp[i].tok
                                i += 1
                            else: 
                                token.tok += next.tok
                        else:
                            token.tok += tmp[i].tok
                            i += 1
                case "/":
                    if tmp[i].tok in ("/", "="):
                        if tmp[i].tok == "/":
                            next = tmp[i]
                            i += 1

                            if i < len(tmp) and tmp[i].tok == "=":
                                token.tok += next.tok + tmp[i].tok
                                i += 1
                            else: 
                                token.tok += next.tok
                        else:
                            token.tok += tmp[i].tok
                            i += 1
                case ">":
                    if tmp[i].tok in (">", "="):
                        if tmp[i].tok == ">":
                            next = tmp[i]
                            i += 1

                            if i < len(tmp) and tmp[i].tok == "=":
                                token.tok += next.tok + tmp[i].tok
                                i += 1
                            else: 
                                token.tok += next.tok
                        else:
                            token.tok += tmp[i].tok
                            i += 1
                case "<":
                    if tmp[i].tok in ("<", "="):
                        if tmp[i].tok == "<":
                            next = tmp[i]
                            i += 1

                            if i < len(tmp) and tmp[i].tok == "=":
                                token.tok += next.tok + tmp[i].tok
                                i += 1
                            else: 
                                token.tok += next.tok
                        else:
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

        return self.replaceTokens(tokens)

class Compiler:
    def __class(self, tokens: Tokens, tabs, loop):
        name = tokens.next()
        argsString = ""
            
        next = tokens.peek()
        if next.tok == ":":
            next = tokens.next()
            next, args = self.getUntil("{", tokens, True)
            argsString = Tokens(args).join()
                
            if self.nextAbstract:
                self.nextAbstract = False
                argsString += ",_ABSTRACT_BASE_CLASS_"
        else:
            next = self.checkDirectNext("{", "class definition", tokens)

            if self.nextAbstract:
                self.nextAbstract = False
                argsString = "_ABSTRACT_BASE_CLASS_"

        if argsString == "":
            self.out += (" " * tabs) + "class " + name.tok + ":"
        else:
            self.out += (" " * tabs) + "class " + name.tok + "(" + argsString + "):"

        block = self.getSameLevelParenthesis("{", "}", tokens)
        if len(block) == 0:
            self.out += "pass\n"
            return loop
        
        self.out += "\n"
                
        self.__nameStack.push((name.tok, "class"))
        self.__compiler(Tokens(block), tabs + 1, loop)
        self.__nameStack.pop()
        return loop
    
    def __asyncGen(self, keyw):
        def fn(tokens : Tokens, tabs, loop):
            self.out += (" " * tabs) + keyw + " "

            return loop
        
        return fn
    
    def __return(self, tokens : Tokens, tabs, loop):
        if self.__nameStack.lookfor("fn") is None:
            self.__error('cannot use "return" outside of a function', tokens.last())

        next = tokens.peek()
        if next.tok == ";":
            tokens.next()
            self.out += (" " * tabs) + "return\n"
            return loop
        
        _, val = self.getUntilNotInExpr(";", tokens, True, advance = False)

        self.out += (" " * tabs) + Tokens([Token("return")] + val).join() + "\n"
            
        return loop
    
    def __break(self, tokens : Tokens, tabs, loop):
        keyw = tokens.last()
        next = tokens.peek()
        if next.tok != ";":
            self.__error('expecting ";" after "break"', next)
        else: tokens.next()

        if loop is None:
            self.__error('cannot use "break" outside of a loop', keyw)
            return loop

        self.out += (" " * tabs) + "break\n"

        return loop
    
    def __continue(self, tokens : Tokens, tabs, loop):
        keyw = tokens.last()
        next = tokens.peek()

        if next is None:
            self.__error('expecting ";" after "continue"', keyw)
        elif next.tok != ";":
            self.__error('expecting ";" after "continue"', next)
        else: tokens.next()

        if loop is None:
            self.__error('cannot use "continue" outside of a loop', keyw)
            return loop
        elif isinstance(loop, CompLoop) and not loop.comp == "":
            self.out += (" " * tabs) + loop.comp

        self.out += (" " * tabs) + "continue\n"

        return loop
    
    def __untilEnd(self, keyw):
        def fn(tokens : Tokens, tabs, loop):
            _, val = self.getUntilNotInExpr(";", tokens, True, advance = False)

            self.out += (" " * tabs) + Tokens([Token(keyw)] + val).join() + "\n"

            return loop
    
        return fn
    
    def __abstract(self, tokens : Tokens, tabs, loop):
        self.nextAbstract = True

        if not self.flags["abstract"]:
            self.flags["abstract"] = True
            self.headers += "from abc import abstractmethod\nfrom abc import ABC as _ABSTRACT_BASE_CLASS_\n"

        return loop

    def __static(self, tokens: Tokens, tabs, loop):
        self.nextStatic = True

        return loop
        
    def __package(self, tokens : Tokens, tabs, loop):
        _, name = self.getUntilNotInExpr(":", tokens, True, advance = False)
        strName = Tokens(name).join()

        self.lastPackage = strName

        self.headers += "from " + strName + " "

        return loop
    
    def __import(self, tokens : Tokens, tabs, loop):
        keyw = tokens.last()
        _, imports = self.getUntilNotInExpr(";", tokens, True, advance = False)
        
        if len(imports) == 1 and imports[0].tok == "*":
            if self.lastPackage == "":
                self.__error('cannot use "import *" if no package is defined', keyw)
                return loop

            self.lastPackage = ""
            self.headers += "import *\n"

            return loop

        self.headers += "import " + Tokens(imports).join() + "\n"

        return loop
    
    def __simpleBlock(self, keyw, kwname, push = None):
        def fn(tokens : Tokens, tabs, loop):
            self.checkDirectNext("{", f'"{kwname}"', tokens)
            block = self.getSameLevelParenthesis("{", "}", tokens)

            self.out += (" " * tabs) + keyw

            if len(block) == 0:
                self.out += ":pass\n"
            else: 
                self.out += ":\n"

                if push is None:
                    loop = self.__compiler(Tokens(block), tabs + 1, loop)[0]
                else:
                    self.__nameStack.push(push)
                    loop = self.__compiler(Tokens(block), tabs + 1, loop)[0]
                    self.__nameStack.pop()

            return loop
        
        return fn
    
    def __block(self, keyw, inLoop = None, content = None, after = None, push = None):
        def fn(tokens : Tokens, tabs, loop):
            loopNotDef = inLoop is None
            if loopNotDef: 
                internalLoop = loop
            else:
                internalLoop = inLoop
            
            if content is None:
                _, localContent = self.getUntilNotInExpr("{", tokens, True, advance = False)
            else: localContent = content

            block = self.getSameLevelParenthesis("{", "}", tokens)

            self.out += (" " * tabs) + Tokens([Token(keyw)] + localContent).join()

            if after is not None:
                self.out += ":\n" + (" " * (tabs + 1)) + after + "\n"
            else:
                if len(block) == 0:
                    self.out += ":pass\n"
                    return loop
                 
                self.out += ":\n"

            if push is None:
                tmp = self.__compiler(Tokens(block), tabs + 1, internalLoop)[0]
            else:
                self.__nameStack.push(push)
                tmp = self.__compiler(Tokens(block), tabs + 1, internalLoop)[0]
                self.__nameStack.pop()

            if loopNotDef: loop = tmp

            return loop
        
        return fn
    
    def __do(self, tokens : Tokens, tabs, loop):
        peek = tokens.peek()

        if peek.tok == "{":
            tokens.next()
            block = self.getSameLevelParenthesis("{", "}", tokens)

            next = tokens.peek()
            if next.tok != "while":
                self.__warning('expecting "while" after a do-while loop. ignoring', next)
            else: tokens.next()

            _, condition = self.getUntilNotInExpr(";", tokens, True, advance = False)
        else:
            _, condition = self.getUntilNotInExpr("{", tokens, True, advance = False)
            block = self.getSameLevelParenthesis("{", "}", tokens)

        check = f"if not({Tokens(condition).join()}):break\n"

        self.out += (" " * tabs) + "while True:\n"
        self.__compiler(Tokens(block), tabs + 1, CompLoop(check))
        self.out += (" " * (tabs + 1)) + check

        return loop

    def __matchLoop(self, tokens : Tokens, tabs, loop):
        while tokens.isntFinished():
            next = tokens.next()
            
            if next.tok.startswith('"""') or next.tok.startswith("'''"):
                self.out += next.tok + "\n"
                continue

            match next.tok:
                case "case":
                    loop = self.__block("case")(tokens, tabs + 1, loop)
                case "default":
                    loop = self.__simpleBlock("case _", "default")(tokens, tabs + 1, loop)
                case _:
                    self.__error('invalid identifier in "match" statement body', next)

        return loop
    
    def __match(self, tokens : Tokens, tabs, loop):
        _, value = self.getUntilNotInExpr("{", tokens, True, advance = False)
        block = self.getSameLevelParenthesis("{", "}", tokens)

        if len(block) == 0:
            return loop
        
        self.out += (" " * tabs) + Tokens([Token("match")] + value).join() +":\n"

        self.__matchLoop(Tokens(block), tabs, loop)
    
    def __handleAssignmentChain(self, tabs, variablesDef):
        buf  = ""
        objs = []

        if len(variablesDef) != 0:
            variablesDef = Tokens(variablesDef)
                    
            next = variablesDef.next()

            while True:
                name = next
                next = variablesDef.peek()

                if next is None or next.tok in SET_OPS + (",", ):
                    objs += [name, Token(",")]

                    if next is None: break
                    else: variablesDef.next()
                else:
                    backPos = variablesDef.pos - 1
                    next, name = self.getUntilNotInExpr(",", variablesDef, True, False, False, SET_OPS)

                    if next == "":
                        variablesDef.pos = backPos
                        nameBuf = []
                        while variablesDef.isntFinished():
                            next = variablesDef.next()

                            if next.tok in SET_OPS:
                                break

                            nameBuf.append(next)

                        name = Token(Tokens(nameBuf).join())

                if not variablesDef.isntFinished(): break
                            
                if   next.tok in SET_OPS:
                    op = next.tok
                    next, value = self.getUntilNotInExpr(",", variablesDef, True, False)
                    value = Tokens(value).join()

                    buf += (" " * tabs) + name.tok + op + value + "\n"
                elif next.tok == ",": 
                    next = variablesDef.next()
                else:
                    self.__error('invalid syntax: expecting "," or any assignment operator', next) 

                if next == "": break

        return objs[:-1], buf 
    
    def __for(self, tokens : Tokens, tabs, loop):
        keyw = tokens.last()
        cnt = [x.tok for x in self.getUntilNotInExpr("{", tokens.copy(), True)[1]].count(";")

        match cnt:
            case 2: # C-like for
                rndBracks = tokens.peek().tok == "("
                if rndBracks: tokens.next()

                if tokens.peek().tok == ";": tokens.next()
                else:
                    _, variablesDef = self.getUntilNotInExpr(";", tokens, True, advance = False)
                    buf = self.__handleAssignmentChain(tabs, variablesDef)
                    self.out += buf

                if tokens.peek().tok == ";": 
                    tokens.next()
                    condition = [Token("True")]
                else:
                    _, condition = self.getUntilNotInExpr(";", tokens, True, advance = False)
                    if len(condition) == 0: condition = [Token("True")]

                if tokens.peek().tok == "{":
                    tokens.next()
                    increments = ""
                else:
                    if rndBracks:
                        _, increments = self.getUntilNotInExpr(")", tokens, True, advance = False)
                        self.checkDirectNext("{", "for loop", tokens)
                    else:
                        _, increments = self.getUntilNotInExpr("{", tokens, True, advance = False)

                    objNames, increments = self.__handleAssignmentChain(tabs + 1, objNames, increments)

                statement = [Token("while")] + condition
            case 0: # Python for
                _, variablesDef = self.getUntilNotInExpr("in", tokens, True, advance = False)
                variablesDef = Tokens(variablesDef)

                if len(variablesDef.tokens) == 0:
                    self.__error("no variable defined in for loop")

                _, iterable = self.getUntilNotInExpr("{", tokens, True, advance = False)
                statement  = [Token("for")] + variablesDef.tokens + [Token("in")] + iterable
                increments = ""
            case _:
                self.__error('invalid syntax: using an unrecognized amount of semicolons in a for loop', keyw)
                return loop
            
        block = self.getSameLevelParenthesis("{", "}", tokens)

        self.out += (" " * tabs) + Tokens(statement).join() + ":"

        if len(block) == 0:
            if increments == "": self.out += "pass\n"
            else:                self.out += "\n" + increments

            return loop
        
        self.out += "\n"
        self.__compiler(Tokens(block), tabs + 1, CompLoop(increments.lstrip()))

        if increments != "": self.out += increments
            
        return loop
    
    def __enum(self, tokens : Tokens, tabs, loop):
        _, value = self.getUntilNotInExpr("{", tokens, True, advance = False)
        block = self.getSameLevelParenthesis("{", "}", tokens)

        if len(value) == 0:
            if len(block) == 0:
                return loop
            
            inTabs = tabs
        else:
            if len(value) > 1:
                self.__error('enum name should contain only one token', value[0])

            self.out += (" " * tabs) + Tokens([Token("class"), value[0]]).join() + ":"

            if len(block) == 0:
                self.out += "pass\n"
                return loop
            
            self.out += "\n"

            inTabs = tabs + 1

        objs, assignments = self.__handleAssignmentChain(inTabs, block, False)
        self.out += (" " * inTabs) + Tokens(objs).join() + f"=range({str(len([x for x in objs if x.tok != ',']))})\n" + assignments
        
        return loop
    
    def __dbGen(self, flag, command, name):
        def __fn(tokens: Tokens, tabs, loop):
            _, content = self.getUntilNotInExpr("{", tokens, True, advance = False)
            block = self.getSameLevelParenthesis("{", "}", tokens)

            if not self.flags[flag]:
                self.flags[flag] = True
                self.headers += command + "\n"

            self.out += (" " * tabs) + Tokens([Token(f"with {name}(")] + content + [Token(")as db")]).join()

            if len(block) == 0:
                self.out += ":pass\n"
                return loop
                
            self.out += ":\n"

            self.__nameStack.push((None, "db"))
            self.__compiler(Tokens(block), tabs + 1, loop)[0]
            self.__nameStack.pop()

            return loop
        return __fn
    
    def __query(self, tokens : Tokens, tabs, loop):           
        kw = tokens.last()

        next = tokens.peek()
        if next is not None and next.tok == "(":
            tokens.next()
            resultIn = Tokens(self.getSameLevelParenthesis("(", ")", tokens)).join() + "="
        else: resultIn = ""

        _, content = self.getUntilNotInExpr("{", tokens, True, advance = False)
        block = self.getSameLevelParenthesis("{", "}", tokens)

        if not self.__nameStack.lookfor("db"):
            self.__error('"query" statement cannot be used outside of a DB block', kw)

        self.out += (" " * tabs) + resultIn + Tokens(
            [Token("db.execute(f'"), Token(encode(Tokens(block).join())), Token("',")] + content + [Token(")")]
        ).join() + "\n"

        return loop
    
    def __terminate(self, tokens: Tokens, tabs, loop):
        keyw = tokens.last()
        next = tokens.peek()

        if next is None:
            self.__error('expecting ";" after "terminate"', keyw)
        elif next.tok != ";":
            self.__error('expecting ";" after "terminate"', next)
        else: tokens.next()

        self.out += (" " * tabs) + "return _HTML_BUF\n"

        return loop
            
    def __init__(self):
        self.__entryPoint = -1

        self.reset()

        self.statementHandlers = {
            "class":     self.__class,
            "package":   self.__package,
            "import":    self.__import,
            "async":     self.__asyncGen("async"),
            "await":     self.__asyncGen("await"),
            "return":    self.__return,
            "break":     self.__break,
            "continue":  self.__continue,
            "@":         self.__untilEnd("@"),
            "throw":     self.__untilEnd("raise"),
            "super":     self.__untilEnd("super"),
            "del":       self.__untilEnd("del"),
            "assert":    self.__untilEnd("assert"),
            "yield":     self.__untilEnd("yield"),
            "external":  self.__untilEnd("nonlocal"),
            "try":       self.__simpleBlock("try", "try"),
            "catch":     self.__block("except", "catch"),
            "success":   self.__simpleBlock("else", "success"),
            "else":      self.__simpleBlock("else", "else"),
            "if":        self.__block("if"),
            "elif":      self.__block("elif"),
            "while":     self.__block("while", GenericLoop()),
            "with":      self.__block("with"),
            "do":        self.__do,
            "for":       self.__for,
            "match":     self.__match,
            "enum":      self.__enum,
            "abstract":  self.__abstract,
            "static":    self.__static,
            "MySQL":     self.__dbGen('mysql', 'from MySQL import MySQL', 'MySQL'),
            "MonQi":     self.__dbGen('monqi', 'from MonQi import MonQi', 'MonQi'),
            "query":     self.__query,
            "echo":      self.__untilEnd("_HTML_BUF+="),
            "reply":     self.__untilEnd("return"),
            "terminate": self.__terminate
        }

    def __error(self, msg, token : Token):
        self.hadError = True
        token.error(msg)

    def __warning(self, msg, token : Token):
        token.warning(msg)

    def reset(self):
        self.__entryPoint += 1
        self.headers = ""
        self.out     = f"def qinpEntryPoint{self.__entryPoint}(*args,**kwargs):\n _HTML_BUF="
        self.__nameStack = NameStack()

        self.hadError = False        
        self.flags = {
            "abstract": False,
            "markup": False,
            "mysql": False,
            "monqi": False
        }

    def newObj(self, objNames, nameToken : Token):
        if not nameToken.tok.isidentifier():
            self.__error(f'invalid identifier name "{nameToken.tok}"', nameToken)
            return

        else: objNames[nameToken.tok] = None

    def checkDirectNext(self, ch, msg, tokens : Tokens):
        next = tokens.next()
        if next.tok != ch:
            self.__error(f'invalid syntax: expecting "{ch}" directly after {msg}. ignoring.', next)
            next = self.getUntil(ch, tokens)

        return next
    
    def getUntil(self, ch, tokens : Tokens, buffer = False):
        buf = []
        while tokens.isntFinished():
            next = tokens.next()

            if next.tok == "\\":
                tokens.next()
                continue

            if next.tok == ch:
                if buffer: return next, buf
                else:      return next

            buf.append(next)

        self.__error(f'expecting character "{ch}"', next)

        if buffer: return "", buf
        else:      return ""
    
    def getUntilNotInExpr(self, ch, tokens : Tokens, buffer = False, errorNotFound = True, advance = True, unallowed = []):
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
                    if ch != "{":
                        lastCrBrack = next
                        crBrack += 1
                case "}":
                    if ch != "{":
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
                if next.tok == ch:
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
                self.__error(f'expecting character "{ch}"', Token(""))
            else:
                self.__error(f'expecting character "{ch}"', next)

        if buffer: return "", buf
        else:      return ""

    def getSameLevelParenthesis(self, openCh, closeCh, tokens : Tokens):
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

    def __handleFn(self, tokens: Tokens, tabs, name, op, msg, loop):
        next = tokens.peek()
        if next is None:
            self.__error('invalid syntax: expecting "(" after method name', tokens.last())
        elif next.tok != "(":
            self.__error('invalid syntax: expecting "(" after method name', next)
        else: tokens.next()

        args = self.getSameLevelParenthesis("(", ")", tokens)

        next = tokens.peek()
        if next is not None and next.tok == "{":
            tokens.next()

            notInClass = self.__nameStack.peek()[1] != "class"
            if notInClass: 
                self.__error(f"{msg} can only be used inside a class", name)

            if len(args) == 0:
                args = [Token("this")]
            else:
                args = [Token("this"), Token(",")] + args

            argsString = Tokens(args).join()
                                        
            if self.nextAbstract:
                self.nextAbstract = False

                if notInClass:
                    self.__error("cannot create abstract method outside of a class", name)
                else:
                    self.out += (" " * tabs) + "@abstractmethod\n"

            if self.nextStatic:
                self.nextStatic = False

                if notInClass:
                    self.__error("cannot create static method outside of a class", name)
                else:
                    self.out += (" " * tabs) + "@classmethod\n"
                                                
            if next is None:
                self.__error('invalid syntax: expecting "{"')
                return

            block = self.getSameLevelParenthesis("{", "}", tokens)
                                    
            self.out += (" " * tabs) + "def " + op + f"({argsString}):"

            if len(block) == 0:
                self.out += "pass\n"
                return
            
            self.out += "\n" + (" " * (tabs + 1)) + "nonlocal _HTML_BUF\n"
            self.__nameStack.push((name.tok, "fn"))
            self.__compiler(Tokens(block), tabs + 1, loop)
            self.__nameStack.pop()
    
    def __compiler(self, tokens : Tokens, tabs, loop):  
        while tokens.isntFinished():
            next = tokens.next()

            if next.tok.startswith('"""') or next.tok.startswith("'''"):
                self.out += next.tok + "\n"
                continue

            if next.tok in self.statementHandlers:
                loop = self.statementHandlers[next.tok](tokens, tabs, loop)
            else:
                name = next
                next = tokens.peek()
                if next is not None and next.tok in SET_OPS + (",", "(", "!", "."):
                    match next.tok:
                        case "(":
                            backpos = tokens.pos
                            tokens.next()
                            args = self.getSameLevelParenthesis("(", ")", tokens)

                            next = tokens.peek()
                            if next is not None and next.tok == "{": # function definition
                                tokens.next()

                                inClass = self.__nameStack.peek()[1] == "class"
                                if inClass: 
                                    if len(args) == 0:
                                        args = [Token("this")]
                                    else:
                                        args = [Token("this"), Token(",")] + args

                                argsString = Tokens(args).join()
                                    
                                if self.nextAbstract:
                                    self.nextAbstract = False

                                    if not inClass:
                                        self.__error("cannot create abstract method outside of a class", name)
                                    else:
                                        self.out += (" " * tabs) + "@abstractmethod\n"

                                if self.nextStatic:
                                    self.nextStatic = False

                                    if not inClass:
                                        self.__error("cannot create static method outside of a class", name)
                                    else:
                                        self.out += (" " * tabs) + "@classmethod\n"
                                                
                                if next is None:
                                    self.__error('invalid syntax: expecting "{"')
                                    continue
                                
                                block = self.getSameLevelParenthesis("{", "}", tokens)
                                    
                                self.out += (" " * tabs) + "def " + name.tok + f"({argsString}):"

                                if len(block) == 0:
                                    self.out += "pass\n"
                                    continue

                                self.out += "\n" + (" " * (tabs + 1)) + "nonlocal _HTML_BUF\n"
                                self.__nameStack.push((name.tok, "fn"))
                                self.__compiler(Tokens(block), tabs + 1, loop)
                                self.__nameStack.pop()
                            else: # function call
                                tokens.pos = backpos - 1
                                _, expr = self.getUntilNotInExpr(";", tokens, True, advance = False)
                                self.out += (" " * tabs) + Tokens(expr).join() + "\n"
                        case "!": # magic method definition
                            tokens.next()

                            if name.tok == "operator":
                                next = tokens.peek()
                                
                                if next is None:
                                    self.__error('expecting "[" after "operator!"', name)
                                elif next.tok != "[":
                                    self.__error('expecting "[" after "operator!"', next)
                                else:
                                    next = tokens.next()

                                op = Tokens(self.getSameLevelParenthesis("[", "]", tokens)).join()

                                if op not in OPERATORS:
                                    next.tok = op
                                    self.__error('unknown operator', next)
                                    op = "__add__"
                                else:
                                    op = OPERATORS[op]

                                self.__handleFn(tokens, tabs, name, op, "operator overloading", loop)
                            elif name.tok in MAGIC_METHODS:
                                if name.tok not in MAGIC_METHODS:
                                    self.__error('unknown magic method', name)
                                    op = "__init__"
                                else:
                                    op = MAGIC_METHODS[name.tok]

                                self.__handleFn(tokens, tabs, name, op, "magic methods", loop)
                            else:
                                self.__error('unknown identifier. expecting magic method or operator overloading', name)
                        case _: # assignment
                            tokens.pos -= 1
                            _, expr = self.getUntilNotInExpr(";", tokens, True, advance = False)
                            self.out += (" " * tabs) + Tokens(expr).join() + "\n"
                else:
                    self.__error("unknown statement or identifier", name)

        return loop, tabs

    def readFile(self, fileName, rep = False):
        with open(fileName, "r") as txt:
            content = txt.read()
        return content.replace("\t", " " if rep else "")

    def compile(self, section):
        self.nextAbstract = False
        self.nextStatic   = False
        self.lastPackage  = ""
        self.lastTabs     = 1
        
        self.lastTabs = self.__compiler(Tokens(section), 1, None)[1]

if __name__ == "__main__":
    print("qinp! compiler v2023.4.19 - thatsOven\nThis file is not meant to be ran.")
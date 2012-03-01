#!/usr/bin/env python

import ast
import astPrint

def parse(code, filename):
    return ASTWrapper(ast.parse(code, filename))

class ASTWrapper:
    def __init__(self, ast, printFunc = astPrint.Print_python):
        self._content = ast
        self._printFunc = printFunc

    def __str__(self): return str(self._printFunc(self._content))

    def visitWith(self, visitor):
        self._content = visitor.visit(self._content)

#__EOF__

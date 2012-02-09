#!/usr/bin/env python
import sys
import lang.python.ast2simple.parsePython as parse

#True, False and None are variables

if __name__ == "__main__":

  print sys.argv
  f = sys.argv[1]

  content = open(f).read()

  visitor = parse.PythonAst2Simple()
  #print visitor
  a = parse.parse(content, f)
  #print '#####################  before  #####################'
  print a

  a.visitWith(parse.ForIntoWhile())
  a.visitWith(parse.WhileRemoveElse())
  a.visitWith(visitor)
  print '#####################  after  #####################'
  print parse.PrintElement(a._content)

#__EOF__

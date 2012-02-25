#!/usr/bin/env python
import sys

from lang.python.ast2simple.parsePython import parse

from lang.python.ast2simple.transform.forIntoWhile import ForIntoWhile
from lang.python.ast2simple.transform.whileSimplifier import WhileSimplifier
from lang.python.ast2simple.transform.cleanJumps import CleanJumps
from lang.python.ast2simple.ast2simple import PythonAst2Simple

from simple.simple import dump as dumpSimple


#True, False and None are variables

if __name__ == "__main__":

  print sys.argv
  f = sys.argv[1]
  contentStr = open(f).read()

  content = parse(contentStr, f)
  print content

  #do the visitors on it
  content.visitWith(ForIntoWhile())
  content.visitWith(WhileSimplifier())
  content.visitWith(CleanJumps())
  print content

  #do the transformation
  content.visitWith(PythonAst2Simple())
  simpleAst = content._content
  print dumpSimple(simpleAst)

#__EOF__

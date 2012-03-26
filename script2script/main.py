#!/usr/bin/env python
import sys

from script2script.lang.python.ast2simple.parsePython import parse

from script2script.lang.python.ast2simple.transform.containerEmulate import ContainerEmulate
from script2script.lang.python.ast2simple.transform.forIntoWhile import ForIntoWhile
from script2script.lang.python.ast2simple.transform.whileSimplifier import WhileSimplifier
from script2script.lang.python.ast2simple.transform.cleanJumps import CleanJumps
from script2script.lang.python.ast2simple.transform.trySimplifier import TrySimplifier

from script2script.lang.python.ast2simple.transform.rmSyntaxicSugar import DeleteOnlyOne, AssignOnlyOne
from script2script.lang.python.ast2simple.transform.simplifying import Simplifying


from script2script.lang.python.ast2simple.ast2simple import PythonAst2Simple

from script2script.simple.simple import dumpSimple, dumpJson

def processFile(f):
  contentStr = open(f).read()

  content = parse(contentStr, f)
  print content

  #do the visitors on it
  for m in [
      ForIntoWhile, WhileSimplifier, CleanJumps, TrySimplifier, ContainerEmulate,
      DeleteOnlyOne, AssignOnlyOne, TrySimplifier, Simplifying
  ]: content.visitWith(m())

  print content

  #do the transformation
  content.visitWith(PythonAst2Simple())
  simpleAst = content._content
  print dumpSimple(simpleAst)
  print dumpJson(simpleAst)

if __name__ == "__main__":

  print sys.argv
  processFile(sys.argv[1])


#__EOF__


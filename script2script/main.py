#!/usr/bin/env python
import sys
from script2script.lang.python.ast2simple.parsePython import *
from script2script.lang.javascript.ast2source.ast2source import *

def processFile(fPath):
  """
  transform a python file to javascript
  """
  with open(fPath) as flink: print flink.read()
  lp = loadPython(fPath)
  print ast2str(lp, 'siAst_simple')
  print simple2javascript(lp)

if __name__ == "__main__":
  processFile(sys.argv[1])


#__EOF__


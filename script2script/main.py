#!/usr/bin/env python
import sys
from script2script.lang.python.ast2simple.parsePython import *

def processFile(fPath):
  with open(fPath) as flink: print flink.read()
  print ast2str(loadPython(fPath), 'siAst_simple')

if __name__ == "__main__":
  processFile(sys.argv[1])


#__EOF__


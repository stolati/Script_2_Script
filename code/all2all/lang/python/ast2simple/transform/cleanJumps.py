#!/usr/bin/env python
import itertools

#Remove dead code :
# The code immediatly after thoses can't execute :
# after return
# after break
# after continue

# redefine visitList function

class CleanJumps(NodeTransformer):

  def visitList(self, nodeList):
    res = super(NodeTransformer, self).visitList(nodeList)
    return itertools.takewhile(lambda x: not isintance(x, ast.Break), res)


  def visitList(self, nodeList):
    res = []
    for node in nodeList



















#__EOF__

#!/usr/bin/env python
import ast
from nodeTransformer import NodeTransformer

#Remove jumps command dead code :
# The code immediatly after thoses can't execute :
# after return
# after break
# after continue

# redefine visitList function


Module(stmt* body) #do nothing
Interactive(stmt* body) #do nothing
Expression(expr body) #do nothing
Suite(stmt* body) #do nothing
FunctionDef(
    identifier name,
    argumetsn args,
    stmt* body,
    expr* decorator_list, #to put 
)












class CleanJumps(NodeTransformer):

  #each node containing code have it in list form
  #so we filter code-containing-node by entering in the visitList fct
  #more node have list than only statements, but they should not contain return/continue/break
  def visitList(self, nodeList):
    res = NodeTransformer.visitList(self, nodeList)

    resBis = []
    for node in res:
      resBis.append(node)
      if isinstance(node, ast.Return): return resBis
      if isinstance(node, ast.Continue): return resBis
      if isinstance(node, ast.Break): return resBis

    return resBis



#__EOF__

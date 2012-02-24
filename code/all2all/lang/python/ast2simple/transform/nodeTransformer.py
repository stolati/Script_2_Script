#!/usr/bin/env python
import ast

#declare a node transformer for inheritance
class NodeTransformer(object):

  #generate a unique variable for temporaly use
  def geneVariable(self):
    if not hasattr(self, 'varNum'): self.varNum = 0
    self.varNum += 1
    return 'genVar_%s_%s' % (self.__class__.__name__, self.varNum)

  #when visiting node, group collection of statement
  #used for the "body" "orelse" and stuffs like that groups
  def visitList(self, nodeList):
    res = []
    for node in nodeList:
      tmpRes = self.visit(node)
      if isinstance(tmpRes, ast.AST):
          res.append(tmpRes)
      elif isinstance(tmpRes, list):
          res += tmpRes
      else:
          raise Exception("bad node type, waiting for list or node")
    return res


  #redefined this because of the list no-taken into account
  def visit(self, node):
      if isinstance(node, list):
          return self.visitList(node)

      nodeName = 'visit_' + node.__class__.__name__
      if hasattr(self, nodeName):
          return getattr(self, nodeName)(node)
      else:
          return self.generic_visit(node)

  def generic_visit(self, node):
    if isinstance(node, ast.AST):
      for f in node._fields:
          attr = getattr(node, f)
          self.visit(attr)
          setattr(node, f, attr)
      return node
    elif isinstance(node, str):
      return node


#__EOF__

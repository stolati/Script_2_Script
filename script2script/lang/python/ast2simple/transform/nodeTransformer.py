#!/usr/bin/env python
import ast

class VariableGenerator(object):
  __varNum = 0

  #generate a unique variable for temporaly use
  def geneVariable(self, name=''):
    if name : name = '_' + str(name)
    n = VariableGenerator.__varNum; VariableGenerator.__varNum += 1
    klassName = self.__class__.__name__
    return 'gv%s_%s_%s' % (name, n, klassName)

class NodeVisitor(object):

  def _specific_visit(self, node):
    if node is None: return
    if isinstance(node, str): return
    if isinstance(node, int): return
    if hasattr(node, '__iter__'):
      for n in node: self.visit(n)
      return
    raise Exception('node type not known %s for element %s' % (node.__class__, node))

  def visit(self, node):
    if not isinstance(node, ast.AST): return self._specific_visit(node)
    nodeName = 'visit_' + node.__class__.__name__
    if hasattr(self, nodeName): getattr(self, nodeName)(node)
    self.generic_visit(node)


  def generic_visit(self, node):
    assert isinstance(node, ast.AST)
    #special case for Raise which has not so many elements it say
    if isinstance(node, ast.Raise):
      for f in node._fields:
        try:
          self.visit(getattr(node, f))
        except AttributeError: pass
      return node

    for f in node._fields:
        self.visit(getattr(node, f))


class __iter_nodes(NodeVisitor):

  def __init__(self): self._nodes = []

  def generic_visit(self, node):
    self._nodes.append(node)
    NodeVisitor.generic_visit(self, node)

  def __call__(self, node):
    self.visit(node)
    return self._nodes

def iter_nodes(node):
  return __iter_nodes()(node)





#declare a node transformer for inheritance
class NodeTransformer(VariableGenerator, NodeVisitor):

  #when visiting node, group collection of statement
  #used for the "body" "orelse" and stuffs like that groups
  def visitList(self, nodeList):
    res = [self.visit(n) for n in nodeList]
    return self.flattenNodeList(res)

  def _specific_visit(self, node):
    if node is None: return node
    if isinstance(node, str): return node
    if isinstance(node, int): return node
    if hasattr(node, '__iter__'): return self.visitList(node)
    raise Exception('node type not known %s for element %s' % (node.__class__, node))

  #more powerful than node.visit because it take the list into account
  def visit(self, node):
    if not isinstance(node, ast.AST): return self._specific_visit(node)

    nodeName = 'visit_' + node.__class__.__name__
    if hasattr(self, nodeName):
      return getattr(self, nodeName)(node)
    return self.generic_visit(node)

  def generic_visit(self, node):
    assert isinstance(node, ast.AST)
    #special case for Raise which has not so many elements it say
    if isinstance(node, ast.Raise):
      for f in node._fields:
        try:
          setattr(node, f, self.visit(getattr(node, f)))
        except AttributeError: pass
      return node

    for f in node._fields:
        setattr(node, f, self.visit(getattr(node, f)))
    return node

  #return True if the node do nothing
  def isEmpty(self, node):
    if not node: return True
    if not hasattr(node, '__iter__'): return False
    return len(node) == 1 and isinstance(node[0], ast.Pass)

  #because transformer can return a list of nodes inside a body => list nested
  def flattenNodeList(self, nodeList):
    res = []
    for n in nodeList:
      if isinstance(n, ast.AST):
        res.append(n)
      elif hasattr(n, '__iter__'):
        res += self.flattenNodeList(n)
      else :
        raise Exception("bad node type, waiting for list or node")

    return res




class NodeTransformerWithSmartInside(NodeTransformer):

  def __init__(self):
    self.bodyToAddBefore = [] #a list of statement list to add before the current 

  def statementToAdd(self, stm): self.bodyToAddBefore[-1].append(stm)
  def statementsToAdd(self, stms): self.bodyToAddBefore[-1] += stms

  def popLevel(self): return self.bodyToAddBefore.pop()
  def addLevel(self): self.bodyToAddBefore.append([])

  #get a single statement, return a list of statements
  def visit_a_Statement(self, stm):
    self.addLevel()
    res = self.visit(stm)
    return self.popLevel() + [res]

  def visit_a_StatementList(self, stmList):
    res = [self.visit_a_Statement(s) for s in stmList]
    return self.flattenNodeList(res)

  def generic_visit(self, node):
    bodyContainer = {
          ast.Module :      ['body'],
          ast.Interactive : ['body'],
          ast.Expression :  ['body'],
          ast.Suite :       ['body'],
          ast.FunctionDef : ['body'],
          ast.ClassDef :    ['body'],
          ast.For :         ['body', 'orelse'],
          ast.While :       ['body', 'orelse'],
          ast.If :          ['body', 'orelse'],
          ast.With :        ['body'],
          ast.TryExcept :   ['body', 'orelse'],
          ast.TryFinally :  ['body', 'finalbody'],
        }

    for k, fieldsName in bodyContainer.iteritems():
      if isinstance(node, k): break
    else:
      return NodeTransformer.generic_visit(self, node)

    for f in node._fields:
      val = getattr(node, f)
      if f in fieldsName:
        newVal = self.visit_a_StatementList(val)
      else:
        self.visit(val)
      setattr(node, f, newVal)

    return node

#__EOF__

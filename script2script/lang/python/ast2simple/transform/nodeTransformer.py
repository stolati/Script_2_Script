#!/usr/bin/env python
import ast, re


__all__ = ['str2ast', 'VariableGenerator', 'NodeVisitor', 'node2json', 'nodeCopy', 'iter_nodes', 'NodeTransformer', 'NodeTransformerAddedStmt']





class VariableGenerator(object):
  """
  Generator a unique variable name
  """
  __varNum = 0

  #generate a unique variable for temporaly use
  def geneVariable(self, name=''):
    """
    Generate a uniq variable name, using incremental variables
    @param name: a facultativ name to give to the variable, will be added to the beginning of it
    @return: a string of the varible name
    """

    if name : name = '_' + str(name)
    n = VariableGenerator.__varNum; VariableGenerator.__varNum += 1
    klassName = self.__class__.__name__
    return 'gv%s_%s_%s' % (name, n, klassName)

  #generate a variable object that can give ast tree for most common uses
  def genVar(self, name=''):
    return AstVariable( self.geneVariable(name) )


class AstVariable(object):

  def __init__(self, name): self.name = name

  def store(self, name=''):
    if name == '': return ast.Name(self.name, ast.Store())
    return ast.Attribute(self.load(), name, ast.Store() )

  def load(self, name=''):
    if name == '': return ast.Name(self.name, ast.Load())
    return ast.Attribute(self.load(), name, ast.Load() )

  def assign(self, val, name=''):
    return ast.Assign([self.store(name=name)], val)

  def param(self):
    return ast.Name(self.name, ast.Param())

  def __str__(self): return self.name




class NodeVisitor(object):
  """
  Subclass to have a node visitor
  Work the same way as the NodeVisitor of the ast module
  """

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
      return

    for f in node._fields:
        self.visit(getattr(node, f))



def node2json(node):
  return Node2Json().visit(node)


class Node2Json:
  """Transform a node tree into a json dict/list structure"""

  def _specific_visit(self, node):
    if node is None: return 'None'
    if isinstance(node, str): return node
    if isinstance(node, int): return str(node)
    if hasattr(node, '__iter__'):
      return [self.visit(n) for n in node]
    raise Exception('node type not known %s for element %s' % (node.__class__, node))

  def visit(self, node):
    if not isinstance(node, ast.AST): return self._specific_visit(node)
    return self.generic_visit(node)


  def generic_visit(self, node):
    assert isinstance(node, ast.AST)
    res = { '__class__':node.__class__.__name__ }

    #special case for Raise which has not so many elements it say
    if isinstance(node, ast.Raise):
      for f in node._fields:
        try:
          res[f] = self.visit(getattr(node, f))
        except AttributeError: pass
      res['__class__'] = node.__class__.__name__
      return res

    for f in node._fields:
      res[f] = self.visit(getattr(node, f))
    return res


def nodeCopy(node):
  return NodeCopy().visit(node)


class NodeCopy:

  def _specific_visit(self, node):
    if node is None: return None
    if isinstance(node, str): return node #str are immutable
    if isinstance(node, int): return node #int are immutable
    if hasattr(node, '__iter__'):
      return [self.visit(n) for n in node]
    raise Exception('node type not known %s for element %s' % (node.__class__, node))

  def visit(self, node):
    if not isinstance(node, ast.AST): return self._specific_visit(node)
    return self.generic_visit(node)


  def generic_visit(self, node):
    assert isinstance(node, ast.AST)
    #special case for Raise which has not so many elements it say

    params = {f:self.visit(getattr(node, f)) for f in node._fields}
    return node.__class__(**params)





class IterNodes(NodeVisitor):

  def __init__(self): self._nodes = []

  def generic_visit(self, node):
    self._nodes.append(node)
    NodeVisitor.generic_visit(self, node)

  def __call__(self, node):
    self.visit(node)
    return self._nodes

def iter_nodes(node):
  """
  return a node iterator, parsing all the nodes one by one
  """
  return IterNodes()(node)








#declare a node transformer for inheritance
class NodeTransformer(VariableGenerator, NodeVisitor):
  """
  Node transformer class, to subclass:
  (You have to call the generic_visit function to continue to subnodes for each functions)
  def visit<nodeName>(self, node) to visit a node, the return will be the new node
  def visit(self, node) to visit all nodes
  def generic_visit(self, node) to change the way a node is found

  Take care, the node passed into visit is changed, it's not a new set of nodes
  """

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




class NodeTransformerAddedStmt(NodeTransformer):
  """
  Like the NodeTransformer
  but add a possibility :
  to add before the current statement others statements.

  to add a single statement : self.statementToAdd( <stmt> )
  to add multiple statements : self.statementsToAdd( <stmt list> )

  when using an element with body elements, use this on the body part :
  not this one => self.generic_visit(node)
  this one year => self.visit_a_StatementList(node)
  """

  def __init__(self):
    self.bodyToAddBefore = [] #a list of statement list to add before the current 

  def statementToAdd(self, stm): self.bodyToAddBefore[-1].append(stm)
  def statementsToAdd(self, stms): self.bodyToAddBefore[-1] += stms

  def _popLevel(self): return self.bodyToAddBefore.pop()
  def _addLevel(self): self.bodyToAddBefore.append([])

  #get a single statement, return a list of statements
  def visit_a_Statement(self, stm):
    self._addLevel()
    res = self.visit(stm)
    return self._popLevel() + [res]

  def visit_a_StatementList(self, stmList):
    res = [self.visit_a_Statement(s) for s in stmList]
    return self.flattenNodeList(res)

  def generic_visit(self, node):
    #list the body insides all the ast parts
    bodyContainer = {
          ast.Module :       ['body'],
          ast.Interactive :  ['body'],
          ast.Expression :   ['body'],
          ast.Suite :        ['body'],
          ast.FunctionDef :  ['body'],
          ast.ClassDef :     ['body'],
          ast.For :          ['body', 'orelse'],
          ast.While :        ['body', 'orelse'],
          ast.If :           ['body', 'orelse'],
          ast.With :         ['body'],
          ast.TryExcept :    ['body', 'orelse'],
          ast.TryFinally :   ['body', 'finalbody'],
          ast.excepthandler: ['body'],
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
        newVal = self.visit(val)
      setattr(node, f, newVal)

    return node



#return the same code
#but remove any previous indentation
def cleanCode(s):
  """
  return a string of code
  removing any previous indentation
  """
  sarr = s.split('\n')
  while(len(sarr) > 0):
    if sarr[0] != '': break
    sarr.pop(0)

  if len(sarr) == 0: return ''
  header = re.compile('^\s*')
  spaces = header.search(sarr[0]).group()

  codearr = []
  for l in sarr:
    if l[:len(spaces)] == spaces:
      l = l[len(spaces):]
    codearr.append(l)

  return '\n'.join(codearr)



def str2ast(s, **kargs):
  """
  Transform a string of code into an ast tree
  Can get kargs, they are elements to change in the code
  It's the old variable name => new variable name
  """
  s = cleanCode(s)
  #return the Module.body
  module = ast.parse(s, '', 'exec')
  if kargs: module = ChangeNames(kargs).visit(module)
  return module.body


class ChangeNames(NodeTransformer):
  def __init__(self, namesDir):
    self.namesDir = namesDir

  def visit_Name(self, node):
    node.id = self.namesDir.get(node.id, node.id)
    return node

  def visit_ClassDef(self, node):
    node.name = self.namesDir.get(node.name, node.name)
    return self.generic_visit(node)

  def visit_FunctionDef(self, node):
    node.name = self.namesDir.get(node.name, node.name)
    return self.generic_visit(node)


#__EOF__



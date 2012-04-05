#!/usr/bin/env python

from ast import *
import ast
import sys
import nodeTransformer
import os.path, os

#Imports variations :
#   import X => ok, have a variable = module object
#   import X.Y => ok, have a variable = module object
#   import X.Y as titi => ok, have a variable = module object
#   import X as titi => ok, have a variable = module object
#   from X import * => not ok, TODO when we will have dir()
#   from X import a, b, c => ok, variabel = module + assignation
#   from X import a as toto => ok, variabel = module + assignation
#   X = import('X')
#   X = __import__('X')

from script2script.lang.python.ast2simple.parsePython import ast2str


class MoreImport(nodeTransformer.NodeTransformer):

  def __init__(self, path=sys.path):
    self.path = path

  def visit(self, node):
    res = NoMoreImport(self.path).visit(node)
    print ast2str(res, 'pyAst_python')
    return res


class NoMoreImport(nodeTransformer.NodeTransformerAddedStmt):

  def __init__(self, path):
    nodeTransformer.NodeTransformerAddedStmt.__init__(self)

    self.resolver = SysPathFinder(path).getCodeFromName
    self.loadedModules = {}

  def visit_Import(self, node):
    for alias in node.names:
      name = alias.name
      asname = alias.asname or name

      fct = self.resolver(name)
      fctName = fct.name

      return [
          fct,
          Assign([Name(asname, Store())], Call(Name(fctName, Load()), [], [], None, None)),
      ]



class SysPathFinder(object):

  def __init__(self, path=sys.path):
    self.path = sys.path

  def getCodeFromName(self, name):
    filePath = self.getFileFromName(name)
    if filePath is None: return None

    content = open(filePath).read()
    contentAst = ast.parse(content, filePath, 'exec')
    return CreateModule(filePath, name).visit(contentAst)


  def getFileFromName(self, name):
    for dirPath in self.path:
      for filePath in os.listdir(dirPath):
        #TODO directory

        fname = os.path.basename(filePath)
        root, ext = os.path.splitext(fname)
        if ext not in ['.py']: continue
        if root != name: continue

        #found it
        return os.path.join(dirPath, filePath)

    return None


class CreateModule(nodeTransformer.NodeTransformer):
  """
  Create a module object from a module ast
  """



  def __init__(self, filePath, moduleName):
    self.filePath = filePath
    self.moduleName = moduleName

    self.moduleFctVariable = self.genVar('moduleFct')

    self.moduleVar = self.genVar('module')


  def visit_Module(self, node):

    args = arguments([], None, None, [])

    init = [
        ClassDef('Module', [], [Pass()], []),
        self.moduleVar.assign( Call(Name('Module', Load()), [], [], None, None)  ),
    ]

    res = [
        Return( self.moduleVar.load() ),
    ]

    return FunctionDef(self.moduleFctVariable.name, args,
        init + self.visit(node.body) + res
    , [])

  def _genAffect(self, node, name):
    return [
        node,
        self.moduleVar.assign(name=name, val=Name(name, Load())),
    ]

  def visit_Assign(self, node):

    assert len(node.targets) == 1
    assert isinstance(node.targets[0], Name)

    return self._genAffect(node, node.targets[0].id)


  def visit_ClassDef(self, node):
    return self._genAffect(node, node.name)

  def visit_FunctionDef(self, node):
    return self._genAffect(node, node.name)


#__EOF__

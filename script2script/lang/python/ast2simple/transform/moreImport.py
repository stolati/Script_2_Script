#!/usr/bin/env python

from ast import *
import ast
import sys
import nodeTransformer
import os.path, os
from nodeTransformer import str2ast


#TODO for the future, add a list of import to include (for the __import__('name') def)
#TODO for the future, add a list of import to not include (because they are in a if)

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
    res = NoMoreImport(self.path).visit_withAdd(node)
    print ast2str(res, 'pyAst_python')
    return res


class NoMoreImport(nodeTransformer.NodeTransformer):
  init_code = """
  class Module(object): pass

  class DictModule(object):
    def __init__(self):
      self.content = {}
    
    def add(self, name, fct):
      self.content[name] = (False, fct)

    def getModule(self, name):
      l, v = self.content[name]
      if not l:
        v = v()
        self.content[name] = (True, v)
      return v
      
  dictModule = DictModule()
  __import__ = dictModule.getModule
  """

  def __init__(self, path):
    nodeTransformer.NodeTransformer.__init__(self)

    self.resolver = SysPathFinder(path).getModuleFromName
    self.resolver_near = SysPathFinder(path, ['']).getModuleFromName

    self.dict_imports = {}
    self.dict_imports_near = {} #the imports of files just at the same place that __file__


  def visit_withAdd(self, node):
    res = self.visit(node)
    toAdd = []

    dict_var = self.genVar('dict_import').name

    klassName = self.genVar('klass').name

    toAdd = str2ast(self.init_code,
        DictModule = self.genVar('klass').name,
        dictModule = dict_var
    )


    for k, (vname, vast) in self.dict_imports.iteritems():
      toAdd += vast + str2ast("dict_var.add('%s', fct)" % k,
              dict_var = dict_var,
              fct = vname
      )

    for k, (vname, vast) in self.dict_imports_near.iteritems():
      toAdd += vast + str2ast("dict_var.add('%s', fct)" % k,
              dict_var = dict_var,
              fct = vname
      )


    if isinstance(res, Module):
      res.body = toAdd + res.body
      return res

    if isinstance(res, list):
      return toAdd + res

    assert False, "type of master ast unknown"


  def visit_Import(self, node):

    for alias in node.names:
      name = alias.name
      asname = alias.asname or name

      #test if the name is componsed
      #if '.' in name:
      #  curName = name.split('.')[0]
      #  leftName = name.split('.')[1:]


      if name not in self.dict_imports_near and \
            name not in self.dict_imports:

        m = self.resolver_near(name)
        if isinstance(m, ErrorModule):
          m = self.resolver(name)
        self.dict_imports[name] = (m.getName(), m.getAst())

      return [
          str2ast("asname = __import__('%s')" % name, asname = asname),
      ]



class SysPathFinder(object):

  def __init__(self, path=sys.path, cur_path=os.getcwd()):
    self.path = sys.path
    self.cur_path = cur_path

  def haveDirModule(self, name, dirPath):
    #test if it's have a directory module
    iniFile = os.path.join(dirPath, name, '__init__.py')
    if os.path.isfile(iniFile):
      return CreateModuleFromFile(iniFile, name)
    return None

  def haveFileModule(self, name, dirPath):
    #test if it's a file module
    modFile = os.path.join(dirPath, name + '.py')
    if os.path.isfile(modFile):
      return CreateModuleFromFile(modFile, name)
    return None


  def getNameFromDir(self, name, dirPath):
    if dirPath == '': dirPath = self.cur_path
    if not os.path.isdir(dirPath): return None

    #TODO take care of zip files
    return self.haveDirModule(name, dirPath) or \
          self.haveFileModule(name, dirPath)


  def getModuleFromName(self, name):
    for dirPath in self.path:
      m = self.getNameFromDir(name, dirPath)
      if m is not None: return m

    return ErrorModule(name)



class ErrorModule(nodeTransformer.VariableGenerator):

  def __init__(self, name):
    self.name = name

    self.fctName = self.genVar().name

  def getAst(self):

    code = """
      def fctName():
        raise ImportError("No module named %s")
    """ % self.name

    return str2ast(code, fctName = self.fctName)

  def getName(self): return self.fctName





class CreateModuleFromFile(nodeTransformer.NodeTransformer):
  """
  Create a module object from a module file
  """


  def __init__(self, filePath, moduleName):
    self.filePath = filePath
    self.moduleName = moduleName

    self.moduleFctVariable = self.genVar('moduleFct')

    self.moduleVar = self.genVar('module')


  def getAst(self):
    with open(self.filePath) as f:
      contentAst = ast.parse(f.read(), self.filePath, 'exec')
    return [self.visit(contentAst)]

  def getName(self):
    return self.moduleFctVariable.name


  def visit_Module(self, node):

    args = arguments([], None, None, [])

    init =  [
        self.moduleVar.assign( Call(Name('Module', Load()), [], [], None, None)  ),
    ]

    res = [
        Return( self.moduleVar.load() ),
    ]

    #add __name__ = and __file__ = in the module
    node.body = [
        Assign([Name('__name__', Store())], Str(self.moduleName)),
        Assign([Name('__file__', Store())], Str(self.filePath)),

    ] + node.body

    return FunctionDef(self.moduleFctVariable.name, args,
        init + self.visit(node.body) + res
    , [])

  def _genAffect(self, name):
    return [ self.moduleVar.assign(name=name, val=Name(name, Load())), ]


  def getAllNames(self, node):
    if isinstance(node, Name):
      return [node.id]

    if isinstance(node, List) or isinstance(node, Tuple):
      res = []
      for e in node.elts:
        res += self.getAllNames(e)
      return e

    return []


  def visit_Assign(self, node):
    assert len(node.targets) == 1
    assert isinstance(node.targets[0], Name)

    names = []
    for t in node.targets:
      names += self.getAllNames(t)

    resAst = [node]
    for name in names:
      resAst += self._genAffect(name)

    return resAst


  def visit_ClassDef(self, node):
    return [node] + self._genAffect(node.name)

  def visit_FunctionDef(self, node):
    return [node] + self._genAffect(node.name)


#__EOF__

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

#  from . import echo
#  from .. import formats
#  from ..filters import equalizer

from script2script.lang.python.ast2simple.parsePython import ast2str


#class MoreImport(nodeTransformer.NodeTransformer):
#
#  def __init__(self, path=sys.path):
#    self.path = path
#
#  def visit(self, node):
#    res = NoMoreImport(self.path).visit_withAdd(node)
#    print ast2str(res, 'pyAst_python')
#    return res
#
#
#class NoMoreImport(nodeTransformer.NodeTransformer):
#  init_code = """
#  class Module(object): pass
#
#  class DictModule(object):
#    def __init__(self):
#      self.content = {}
#    
#    def add(self, name, fct):
#      self.content[name] = (False, fct)
#
#    def getModule(self, name):
#      l, v = self.content[name]
#      if not l:
#        v = v()
#        self.content[name] = (True, v)
#      return v
#      
#  dictModule = DictModule()
#  __import__ = dictModule.getModule
#  """
#
#  def __init__(self, path):
#    nodeTransformer.NodeTransformer.__init__(self)
#
#    self.resolver = SysPathFinder(path).getModuleFromName
#    self.resolver_near = SysPathFinder(path, ['']).getModuleFromName
#
#    self.dict_imports = {}
#    self.dict_imports_near = {} #the imports of files just at the same place that __file__
#
#
#  def visit_withAdd(self, node):
#    res = self.visit(node)
#    toAdd = []
#
#    dict_var = self.genVar('dict_import').name
#
#    klassName = self.genVar('klass').name
#
#    toAdd = str2ast(self.init_code,
#        DictModule = self.genVar('klass').name,
#        dictModule = dict_var
#    )
#
#
#    for k, (vname, vast) in self.dict_imports.iteritems():
#      toAdd += vast + str2ast("dict_var.add('%s', fct)" % k,
#              dict_var = dict_var,
#              fct = vname
#      )
#
#    for k, (vname, vast) in self.dict_imports_near.iteritems():
#      toAdd += vast + str2ast("dict_var.add('%s', fct)" % k,
#              dict_var = dict_var,
#              fct = vname
#      )
#
#
#    if isinstance(res, Module):
#      res.body = toAdd + res.body
#      return res
#
#    if isinstance(res, list):
#      return toAdd + res
#
#    assert False, "type of master ast unknown"
#
#
#  def visit_Import(self, node):
#
#    for alias in node.names:
#      name = alias.name
#      asname = alias.asname or name
#
#      #test if the name is componsed
#      #if '.' in name:
#      #  curName = name.split('.')[0]
#      #  leftName = name.split('.')[1:]
#
#
#      if name not in self.dict_imports_near and \
#            name not in self.dict_imports:
#
#        m = self.resolver_near(name)
#        if isinstance(m, ErrorModule):
#          m = self.resolver(name)
#        self.dict_imports[name] = (m.getName(), m.getAst())
#
#      return [
#          str2ast("asname = __import__('%s')" % name, asname = asname),
#      ]
#
#
#
#class SysPathFinder(object):
#
#  def __init__(self, path=sys.path, cur_path=os.getcwd()):
#    self.path = sys.path
#    self.cur_path = cur_path
#
#  def haveDirModule(self, name, dirPath):
#    #test if it's have a directory module
#    iniFile = os.path.join(dirPath, name, '__init__.py')
#    if os.path.isfile(iniFile):
#      return CreateModuleFromFile(iniFile, name)
#    return None
#
#  def haveFileModule(self, name, dirPath):
#    #test if it's a file module
#    modFile = os.path.join(dirPath, name + '.py')
#    if os.path.isfile(modFile):
#      return CreateModuleFromFile(modFile, name)
#    return None
#
#
#  def getNameFromDir(self, name, dirPath):
#    if dirPath == '': dirPath = self.cur_path
#    if not os.path.isdir(dirPath): return None
#
#    #TODO take care of zip files
#    return self.haveDirModule(name, dirPath) or \
#          self.haveFileModule(name, dirPath)
#
#
#  def getModuleFromName(self, name):
#    for dirPath in self.path:
#      m = self.getNameFromDir(name, dirPath)
#      if m is not None: return m
#
#    return ErrorModule(name)
#
#
#
#class ErrorModule(nodeTransformer.VariableGenerator):
#
#  def __init__(self, name):
#    self.name = name
#
#    self.fctName = self.genVar().name
#
#  def getAst(self):
#
#    code = """
#      def fctName():
#        raise ImportError("No module named %s")
#    """ % self.name
#
#    return str2ast(code, fctName = self.fctName)
#
#  def getName(self): return self.fctName
#
#
#
#
#
#class CreateModuleFromFile(nodeTransformer.NodeTransformer):
#  """
#  Create a module object from a module file
#  """
#
#
#  def __init__(self, filePath, moduleName):
#    self.filePath = filePath
#    self.moduleName = moduleName
#
#    self.moduleFctVariable = self.genVar('moduleFct')
#
#    self.moduleVar = self.genVar('module')
#
#
#  def getAst(self):
#    with open(self.filePath) as f:
#      contentAst = ast.parse(f.read(), self.filePath, 'exec')
#    return [self.visit(contentAst)]
#
#  def getName(self):
#    return self.moduleFctVariable.name
#
#
#  def visit_Module(self, node):
#
#    args = arguments([], None, None, [])
#
#    init =  [
#        self.moduleVar.assign( Call(Name('Module', Load()), [], [], None, None)  ),
#    ]
#
#    res = [
#        Return( self.moduleVar.load() ),
#    ]
#
#    #add __name__ = and __file__ = in the module
#    node.body = [
#        Assign([Name('__name__', Store())], Str(self.moduleName)),
#        Assign([Name('__file__', Store())], Str(self.filePath)),
#
#    ] + node.body
#
#    return FunctionDef(self.moduleFctVariable.name, args,
#        init + self.visit(node.body) + res
#    , [])
#
#  def _genAffect(self, name):
#    return [ self.moduleVar.assign(name=name, val=Name(name, Load())), ]
#
#
#  def getAllNames(self, node):
#    if isinstance(node, Name):
#      return [node.id]
#
#    if isinstance(node, List) or isinstance(node, Tuple):
#      res = []
#      for e in node.elts:
#        res += self.getAllNames(e)
#      return e
#
#    return []
#
#
#  def visit_Assign(self, node):
#    assert len(node.targets) == 1
#    assert isinstance(node.targets[0], Name)
#
#    names = []
#    for t in node.targets:
#      names += self.getAllNames(t)
#
#    resAst = [node]
#    for name in names:
#      resAst += self._genAffect(name)
#
#    return resAst
#
#
#  def visit_ClassDef(self, node):
#    return [node] + self._genAffect(node.name)
#
#  def visit_FunctionDef(self, node):
#    return [node] + self._genAffect(node.name)
#
#
#
#
#def Resolver:
#
#  self.content = [] #list of dictonnary of dictionary
#
#
#
#
#def ModuleAst:
#
#  self.name
#  self.subModules = {}
#
#  self.filepath
#  self.package
#
#
#
#def FileResolver:
#  get(from = (id, name), search = name) => foundKlass
#
#
#def FoundResolver:
#  get(from = (id, name), search = name) => foundKlass
#  __getitem__[(id, name)]
#
#def FoundKlass:
#  self.moduleFound
#  self.FoundOnTheWay
#
#
#
# - path of the current module/package
# - path of the main path
# - PYTHONPATH
# - python lib



#class Resolver(object):





#class Resolver




class SimpleFileResolver(object):

  def __init__(self, file_system):
    self.fs = file_system

  def simpleFind(self, fromPath, strPath):
    self.setFrom(fromPath.split('.'))
    return self.get(strPath.split('.'))

  def setFrom(self, fromPath):
    #because we always take the path from up one element
    self.fromPath = fromPath[:-1]
    return self


  def get(self, goalPath):
    """
    Calcul the path from a file system
    @return None or the complete path found
    """

    #path can only be one of both
    validPath = []
    if self.fromPath : validPath.append(self.fromPath + goalPath)
    validPath.append( goalPath )

    for path in validPath:
      res = self._callPythonPath(path)
      if res != None:
        return res

    return None


  def _callPythonPath(self, path):
    """
    Return the file object from path
    If the path is not valid, return None
    """

    result = []
    curFile = self.fs

    for name in path[:-1]: #all but last
      try:
        curFile = curFile['%s/' % name]
        curFile['__init__.py']
      except KeyError:
        return None
      result.append('%s/' % name)

    name = path[-1]
    #for the last element, could be a single file module

    try : #test for a directory module first
      curDirFile = curFile['%s/' % name]
      curDirFile['__init__.py']
    except KeyError:
      pass
    else:
      return result + ['%s/' % name , '__init__.py']

    #test for a single file module
    try:
      curFileFile = curFile['%s.py' % name]
    except KeyError:
      pass
    else:
      return result + ['%s.py' % name]

    return None


  def _path2file(self, path):
    """from a path, return the file object"""
    curFO = self.fs
    for e in path:
      curFO = curFO[e]
    return curFO


  #path of a module change
  # if __init__.py it's the directory name (as path)
  # if XXXX.py it's the name without .py









class FileSystemFile(object):
  """
  Replace a file system with a dictionary-like
  It's like a dict of dict

  - To get a file, just get dict.getFile(), then open it or whatever
  - Directory are named with a '/' at the end
  """

  def __init__(self, path):
    self.path = path

  def __getitem__(self, name): raise KeyError("File don't have a file list")
  def __contins__(self, name): return False
  def __iter__(self, name): raise KeyError("File don't have a file list")
  def __str__(self): return "'%s'" % os.path.basename(self.path)



class FileSystemDir(FileSystemFile):

  def __init__(self, root):
    self.root = root
    self.chiblings = None

  def _genChiblings(self):
    if self.chiblings is not None: return

    self.chiblings = {}
    for f in os.listdir(self.root):
      fpath = os.path.join(self.root, f)

      if os.path.isfile(fpath):
        self.chiblings[f] = FileSystemFile(fpath)
      elif os.path.isdir(fpath):
        self.chiblings['%s/' % f] = FileSystemDir(fpath)
      else:
        assert False, "what is this file %s ??" % fpath

  def __getitem__(self, name): self._genChiblings() ; return self.chiblings[name]
  def __contains__(self, name): self._genChiblings() ;  return name in self.chiblings
  def __iter__(self): self._genChiblings() ; return iter(self.chiblings)

  def __str__(self):
    res = []
    for name in self:
      res.append( str(self[name]))
    return '%s/ : {%s}' % (os.path.basename(self.root), ', '.join(res))



#__EOF__

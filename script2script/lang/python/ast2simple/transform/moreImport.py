#!/usr/bin/env python

from ast import *
import ast, md5
import sys
import nodeTransformer
import os.path, os
import zipfile
from nodeTransformer import str2ast


#TODO for the future, add a list of import to include (for the __import__('name') def)
#TODO for the future, add a list of import to not include (because they are in a if)
#TODO do a PythonModule for .zip files
#TODO do a test on pyc and pyo files, saying it don't take them

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



class SimpleFileResolver(object):

  def __init__(self, pythonModule):
    self.pm = pythonModule


  def find(self, toStr, fromStr=''):
    """
    helper function to get the content of the result
    """
    return self.getModule(toStr.split('.'), fromStr.split('.'))

  def getModule(self, toPath, fromPath=''):

    #test from the relative path
    if fromPath:
      try:
        return self.pm.getNamesRel(fromPath, toPath)
      except NoModuleFound:
        pass

    #test from the absolute path
    try:
      print toPath
      return self.pm.getNamesAbs(toPath)
    except NoModuleFound:
      pass

    return None



class NoModuleFound(Exception): pass

class PythonModule(object):
  """
  Represent an abstract python module
  """

  def __init__(self, name='', up=None):
    self._name = name
    self._up = up

  def getContent(self): raise NotImplemented
  def getChild(self, name): raise NotImplemented
  def getChilds(self): raise NotImplemented
  def getNamesRel(self, nameListFrom, nameListTo): raise NotImplemented

  def getName(self): return self._name
  def __hash__(self): return hash(self._name)

  def __getitem__(self, name): return self.getChild(name)
  def __iter__(self): return iter(self.getChilds())

  def getUp(self): return self._up
  def setUp(self, up): self._up = up

  def getNamesAbs(self, nameList):
    return reduce(lambda e, n: e[n] , nameList, self)

  def getNames(self):
    if self._up is None: return []
    return self._up.getNames() + [self._name]

  def __str__(self):
    return '%s.%s' % (str(self._up), self._name)

  def _forRepr(self):
    hash_str = md5.new(self.getContent()).hexdigest()
    dict_repr = {c.getName():c._forRepr() for c in self}
    return (hash_str, dict_repr)

  def __repr__(self):
    """
    Return a couple :
    (hash, {})
    - The first element is the hash of the content
    - The second element is a dict of the childs {name : repr()}
    """
    return repr(self._forRepr())



class PythonModuleList(PythonModule):
  """
  Represent a list of concrete modules
  """

  def __init__(self, name='', up=None):
    PythonModule.__init__(self, name, up)
    self._modules = [] #order is important

  def addModule(self, fct):
    """
    fct should wait for parameters : name
    """
    res = fct(str(len(self._modules)))
    self._modules.append(res)
    res.setUp(self)


  def getContent(self): return ''

  def getChild(self, name):
    print self, name
    try:
      return self._modules[int(name)]
    except ValueError:
      raise NoModuleFound('Not a int value')
    except IndexError:
      raise NoModuleFound()

  def getChilds(self): return list(self._modules)



  def getNamesAbs(self, nameList):
    print nameList
    try: #if nameList contain the digit
      i, nameListTemp = int(nameList[0]), nameList[1:]
      print 'is a number'

      m = self._modules[i]
      m.getNamesAbs(nameListTemp)

    except ValueError: pass
    except IndexError: pass

    #test for each modules
    for m in self._modules:
      res = m.getNamesAbs(nameList)
      if res is not None: return res

    return None


  def getNamesRel(self, nameListTo, nameListFrom):
    if len(nameListFrom) == 0: return self.getNamesAbs(nameListTo)

    fromElement = self.getNamesAbs(nameListFrom)
    if fromElement is None: return None

    return fromElement.getNamesAbs(nameListTo)



class PythonModuleFile(PythonModule):
  """
  Represent a python module on file system
  Could be any file system, this class must be inherited
  """
  TYPE_ROOT, TYPE_FILE, TYPE_DIR = ('root', 'file', 'dir')

  def __init__(self, up_path, name='', up=None):
    PythonModule.__init__(self, name, up)

    if self._up is None:
      self._type, self._contentFile, self._base_dir = (self.TYPE_ROOT, None, up_path)
      self._content = ''
    else:
      infos = self._findRepModule(up_path) or self._findFileModule(up_path)
      if infos is None: raise NoModuleFound('No module with name %s in path %s' % (self._name, up_path))
      self._type, self._contentFile, self._base_dir = infos
      self._content = self._f_content(self._contentFile)


  def _findRepModule(self, up_path):
    dirPath = self._f_join(up_path, self._name)
    filePath = self._f_join(dirPath, '__init__.py')
    if not self._f_isfile(filePath): return None
    return (self.TYPE_DIR, filePath, dirPath)

  def _findFileModule(self, up_path):
    filePath = self._f_join(up_path, '%s.py' % self._name)
    if not self._f_isfile(filePath): return None
    return (self.TYPE_FILE, filePath, up_path)

  def getContent(self): return self._content

  def getChild(self, name):
    if '.' in name: raise NoModuleFound('no dots allowed in module name')
    if self._type == self.TYPE_FILE : raise NoModuleFound('file module has no childs')
    if name == '__init__': raise NoModuleFound('__init__ are reserved for dir elements')
    return self._f_new(self._base_dir, name, self)

  def getChilds(self):
    if self._type == self.TYPE_FILE : return []
    res = []
    for name in self._f_listfiles(self._base_dir):
      if name[-3:] == '.py': name = name[:-3]

      try:
        mod = self.getChild(name)
      except NoModuleFound:
        pass
      else:
        res.append(mod)

    return res

  def getNamesRel(self, nameListFrom, nameListTo):
    moduleFrom = self.getNamesAbs(nameListFrom)
    if moduleFrom._type == self.TYPE_FILE:
      moduleFrom = moduleFrom.getUp()
    return moduleFrom.getNamesAbs(nameListTo)

  def getPath(self):
    return self._contentFile

  #Function that the class must implement
  def _f_listfiles(self, path): raise NotImplemented
  def _f_join(self, *args): raise NotImplemented
  def _f_isfile(self, path): raise NotImplemented
  def _f_isdir(self, path): raise NotImplemented
  def _f_content(self, path): raise NotImplemented
  def _f_new(self, base_dir, name, up): raise NotImplemented








class PythonModuleOnDisk(PythonModuleFile):
  """
  Represent a python module on file system
  """
  TYPE_ROOT, TYPE_FILE, TYPE_DIR = ('root', 'file', 'dir')

  def _f_listfiles(self, path): return os.listdir(path)
  def _f_join(self, *args): return os.path.join(*args)
  def _f_isfile(self, path): return os.path.isfile(path)
  def _f_isdir(self, path): return os.path.isdir(path)
  def _f_content(self, path):
    with open(path) as f:
      return f.read()
  def _f_new(self, base_dir, name, up):
    return PythonModuleOnDisk(base_dir, name, up)




class PythonModuleStatic(PythonModuleFile):

  def __init__(self, diskContent, up_path = '', name='', up=None):
    if up is None: #useful for test
      up_path = name = name or up_path or '' #force if the name/up_path is not ''
      diskContent = diskContent if name in diskContent else {name:diskContent}
    self._diskContent = diskContent

    PythonModuleFile.__init__(self, up_path, name, up)

  def _s_getPathElement(self, path):
    try:
      return reduce(lambda r, n : r[n], path.split('/'), self._diskContent)
    except KeyError:
      return None

  def _f_listfiles(self, path):
    pathElem = self._s_getPathElement(path)
    if pathElem is None : return []
    return list(pathElem.iterkeys())

  def _f_join(self, *args): return '/'.join(args)
  def _f_isfile(self, path): return isinstance(self._s_getPathElement(path), str)
  def _f_isdir(self, path): return isinstance(self._s_getPathElement(path), dict)
  def _f_content(self, path): return self._s_getPathElement(path)
  def _f_new(self, base_dir, name, up):
    return PythonModuleStatic(self._diskContent, base_dir, name, up)


#class PythonModuleZip(PythonModuleFile):
#
#  def __init__(self, ziplink, up_path = '', name='', up=None):
#    if not isinstance(ziplink, zipfile.ZipFile):
#      ziplink = zipfile.ZipFile(ziplink, 'r')
#    self._zip = ziplink
#
#    PythonModuleFile.__init__(self, up_path, name, up)
#
#
#  def _f_listfiles(self, path):
#    res = []
#    for zipinfo in self._zip.infolist:
#      fn = zipinfo.filename
#
#
#
#    return []
#    names = [
#      for self._zip.infolist
#
#
#
#  def _f_join(self, *args): raise NotImplemented
#  def _f_isfile(self, path): raise NotImplemented
#  def _f_isdir(self, path): raise NotImplemented
#  def _f_content(self, path):
#
#
#
#  def _f_new(self, base_dir, name, up): raise NotImplemented






#__EOF__

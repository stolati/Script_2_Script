#!/usr/bin/env python

from ast import *
import ast, md5
import sys
import nodeTransformer
import os.path, os
import zipfile
from nodeTransformer import str2ast, AstVariable

#TODO don't forget the With ast stuff


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


class MoreImport(nodeTransformer.NodeTransformer):

  def __init__(self, path=sys.path):
    self.path = path

  def visit(self, node):
    pml = PythonModuleList()
    for path in self.path:
      moduleFact = lambda name : PythonModuleOnDisk(path, name=name)
      pml.addModule(moduleFact)

    sfr = SimpleFileResolver(pml)

    res = NoMoreImport(sfr).main_visit(node)
    return res


class NoMoreImport(nodeTransformer.NodeTransformer):
  init_code = """
  class Module(object): pass

  class DictModule(object):
    def __init__(self):
      self.content = {}

    def add(self, name, fct):
      self.content[name] = (False, fct)

    #TODO do it for recursive module
    def getModule(self, name):
      if name not in self.content:
        raise ImportError("No module named %s" % name)

      l, v = self.content[name]
      if l: return v #v is the module

      m = Module()
      self.content[name] = (True, m)
      v(m)
      return m

  dictModule = DictModule()
  __import__ = dictModule.getModule
  """

  def __init__(self, moduleRef, curPath=''):
    NodeTransformer.__init__(self)

    self.dict_imports = {} #import in a dict form

    self._moduleRef = moduleRef
    self._curPath = curPath



  def main_visit(self, node):
    #the node should be a module
    res = self.visit(node)

    dictModule_klass = self.genVar('DictModule')
    dictModule_inst = self.genVar('dictModule')
    before = str2ast(self.init_code, DictModule=dictModule_klass.name, dictModule=dictModule_inst.name)


    for k, (vname, vast) in self.dict_imports.iteritems():
      before += vast
      before += str2ast("dictModule.add('%s', moduleFctVar)" % k, dictModule = dictModule_inst.name, moduleFctVar=vname.name)
      pass

    node.body = before + node.body
    return node


  def genImport(self, module, fctName):
    """
    Generate the import function for this name
    The import function is in the form :
    def fctName(genVar_398_module):
      genVar_398_module.__file__ = "/my/module/file/path/toto/tutu"
      genVar_398_module.__name__ = "toto.tutu"

    It dont' return a module, just affection values to the parameter module
    """

    contentAst = ast.parse(module.getContent(), module.getPath(), 'exec').body
    moduleVar = self.genVar('module')

    contentAst = [
        moduleVar.assign(Str(module.getPath()), '__file__'),
        moduleVar.assign(Str('.'.join(module.getNames()[1:])), '__name__'), #TODO remove the [1:]
    ] + ModuleAffectation(moduleVar.name).visit(contentAst)

    arguments = ast.arguments([moduleVar.param()], None, None, [])
    return [FunctionDef(fctName, arguments , contentAst, [] )]


  def addImport(self, name):
    """
    from a name (and searching the reference of the current object)
    return an absolute name for the import.
    Put the module result into the inter dict
    """

    resModule = self._moduleRef.find(name, self._curPath)

    fctName = self.genVar('importfct')

    if resModule is None: #error case
      codeAst = str2ast("""
            def fctName(moduleVar):
              raise ImportError("No module named %s")
          """ % name, fctName = fctName.name)

      self.dict_imports[name] = (fctName, codeAst)

      return name

    newName = '.'.join(resModule.getNames()[1:]) #TODO remove the [1:]
    codeAst = self.genImport(resModule, fctName.name)

    self.dict_imports[newName]  = (fctName, codeAst)

    return newName


  def visit_Import(self, node):
    res = []

    for alias in node.names:
      name = alias.name
      asname = alias.asname or name

      #2 cases
      # - import toto.tutu.titi as tralala => this is tralal = toto.tutu.titi => lo see after
      # - import toto.tutu.titi => toto = toto, toto.tutu = toto.tutu, toto.tutu.titi = toto.tutu.titi
      absName = self.addImport(name)

      res += [
        str2ast("asname = __import__('%s')" % absName, asname = asname)
      ]

    return res




class ModuleAffectation(nodeTransformer.NodeTransformer):
  """
  For each affectation in the ast,
  do another one for the variable name in the form
  toto = 'tutu'
  myVar.toto = toto

  It's used in the module part to have the module.var acess
  """

  #TODO to complete

  def __init__(self, varName):
    NodeTransformer.__init__(self)
    self._varName = AstVariable(varName)

  def _genAffect(self, name):
    return [self._varName.assign( ast.Name(name, Load()), name)]

  @staticmethod
  def getAllNames(eList):
    """
    Return all the names inside a tuple/list assignment
    Don't return object attribute assigment
    """
    if isinstance(eList, ast.Name): return [eList.id]
    if isinstance(eList, ast.List) or isinstance(eList, ast.Tuple):
      res = []
      for e in eList.elts:
        res += ModuleAffectation.getAllNames(e)
      return res

    #in attribute case
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


















class SimpleFileResolver(object):

  def __init__(self, pythonModule):
    self.pm = pythonModule

  def find(self, toStr, fromStr=''):
    """
    helper function to get the content of the result
    """
    return self.getModule(self._str2names(toStr), self._str2names(fromStr))

  @staticmethod
  def _str2names(s): return s.split('.') if s else []

  def getModule(self, toPath, fromPath=''):

    #test from the relative path
    if fromPath:
      try:
        return self.pm.getNamesRel(toPath, fromPath)
      except NoModuleFound:
        pass

    #test from the absolute path
    try:
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
    try:
      return self._modules[int(name)]
    except ValueError:
      raise NoModuleFound('Not a int value')
    except IndexError:
      raise NoModuleFound()

  def getChilds(self): return list(self._modules)


  def getNamesAbs(self, nameList):
    if not nameList: return self

    try: #if nameList contain the digit
      i, nameListTemp = int(nameList[0]), nameList[1:]

      m = self._modules[i]
      res = m.getNamesAbs(nameListTemp)

      return res

    except ValueError: pass
    except IndexError: pass
    except NoModuleFound: pass

    #test for each modules
    for m in self._modules:
      try:
        res = m.getNamesAbs(nameList)
        return res
      except NoModuleFound:
        pass

    return None


  def getNamesRel(self, nameListTo, nameListFrom):
    #TODO to remove
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
      except NoModuleFound as e:
        pass
      else:
        res.append(mod)

    return res

  def getNamesRel(self, nameListTo, nameListFrom):
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

  def _f_listfiles(self, path):
    return os.listdir(path)

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




class PythonModuleStatic(PythonModuleFile):
  """
  The root element should be unamed,
  If it's have a name, it should be taken care with the upper element
  """

  def __init__(self, diskContent, up_path = '', name='', up=None):
    if up is None: #useful for test
      up_path = name = name or up_path or '' #force if the name/up_path is not ''
      self._diskContent = diskContent #diskContent if name in diskContent else {name:diskContent}
      self._root = self
    else:
      self._root = up._root
      self._diskContent = diskContent

    PythonModuleFile.__init__(self, up_path, name, up)

  def _s_getPathElement(self, path):
    try:
      return reduce( lambda r, n : r[n], path.split('/')[1:], self._diskContent)
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
















#TODO do for zip
#class PythonModuleZip(PythonModuleFile):
#
#  def __init__(self, ziplink, up_path = '', name='', up=None):
#    if not isinstance(ziplink, zipfile.ZipFile):
#      up_path = os.path.basename(ziplink)[:-4]
#      ziplink = zipfile.ZipFile(ziplink, 'r')
#    self._zip = ziplink
#
#
#    PythonModuleFile.__init__(self, up_path, name, up)
#
#
#  def __del__(self):
#    self._zip.close()
#
#  def _f_listfiles(self, path):
#    res = []
#    for name in self._zip.namelist():
#      if name[-1] == '/' : name = name[:-1] #remove the last / char
#      if name[:len(path)] != path: continue
#
#    #  if name[:len(path)] == path:
#    #  else:
#    #    'ko'
#
#    #res = []
#    #for zipinfo in self._zip.infolist:
#    #  fn = zipinfo.filename
#
#
##
##    return []
##    names = [
##      for self._zip.infolist
#
#  def _f_join(self, *args): return '/'.join(args)
#
#  def _f_isfile(self, path):
#    return any((name == path for n in self._zip.namelist()))
#
#  def _f_isdir(self, path):
#    return any((name == path+'/' for n in self._zip.namelist()))
#
##  def _f_content(self, path):
##  def _f_new(self, base_dir, name, up): raise NotImplemented






#__EOF__

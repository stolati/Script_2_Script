#!/usr/bin/env python

from ast import *
import ast, md5
import sys
import nodeTransformer
import os.path, os
import zipfile
from nodeTransformer import str2ast, AstVariable
from pyModule import *

from script2script.tools import echo

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
  """
  Transform each import to be ready for transforming to Simple
  The visit function of MoreImport should have the '__main__' module
  """

  def __init__(self, paths=sys.path):
    """
    paths should not contain the '' path,
    it should be changed by the current path
    """
    self.paths = paths
    self.module = PythonModuleList()
    for path in paths:
      self.module.addModule( PythonModuleOnDisk(path) )

    self.moduleResolver = SimpleModuleResolver(self.module)

    self.needed_modules = {}

  def addModule(self, name):
    """
    add a module to the module list
    if the module is already here, don't add it
    the name should be the absolute name of the module
    """
    if name in self.needed_modules: return
    self.needed_modules[name] = True #avoid circular references

    module = self.moduleResolver.find(name)
    ast = ast.parse(module.getContent(), module.getPath(), 'exec').body
    self.needed_modules[name] = ImportOneModule(self.getModule(name), ast, self).getModuleBody()


  @echo
  def getAbsName(self, path, fromPath):
    res = self.moduleResolver.find(path, fromPath)
    return '.'.join(res.getNames()) if res else None

  def visit(self, node):
    assert isinstance(node, ast.Module)
    module = PythonModuleStatic('', '', '__main__')
    node.body = ImportOneModule(module, node.body, self).getModuleBody()

    #do stuffs
    return node


class ImportOneModule(nodeTransformer.NodeTransformer):
  """
  Load a module body list and return it with :
    - __name__ and __file__ variable set
    - Module object construct and variable affectation
  Return a list, the first element is the module affectation :
    genModuleVar = type('Module', (), {})
  """

  def __init__(self, module, ast, moreImportObject):
    self._module = module
    self._ast = ast
    self._moreImportObject = moreImportObject
    self._moduleVar = self.genVar('moduleObject')


  def getModuleBody(self):
    ast = [
        Assign([Name('__name__', Store())], Str(self._module.getName())),
        Assign([Name('__file__', Store())], Str(self._module.getPath() or '')),
    ] + self._ast

    #replace the import statements
    res = str2ast('from importlib import import_module') + self.visit(ast)

    #affect values to the module
    moduleAffectation = str2ast("moduleObject = type('Module', (), {})()", moduleObject = self._moduleVar.name)
    res = moduleAffectation + ModuleAffectation(self._moduleVar).visit(res)

    print ast2str(res)

    return res

  def visit_Import(self, node):
    res = []

    for aliaselem in node.names:
      name, asname = aliaselem.name, aliaselem.asname

      if asname:
        res += self.genImportWithAsName(name, asname)
      else:
        res += self.genImportWithoutAsName(name)

    return res


  def genImportWithAsName(self, name, asname):
    """
    Import, the imported element is the last of the list toto.titi.tutu => tutu
    """
    name = self._moreImportObject.getAbsName(name, '.'.join(self._module.getNames()))
    pass

  def genImportWithoutAsName(self, name):
    """
    Import, the imported element is the first of the list toto.titi.tutu => toto
    """
    objectName = name.split('.')[0]
    absName = self._moreImportObject.getAbsName(name, '.'.join(self._module.getNames()))
    #if absName is None:
    #  return str2ast('raise ImportError("no module named %s")' % name)
    return str2ast("name = import_module('%s', None)" % absName, name = objectName)



class ModuleAffectation(nodeTransformer.NodeTransformer):
  """
  For each affectation in the ast,
  create a do another one for the variable name in the form
  toto = 'tutu'
  myVar.toto = toto

  It's used in the module part to have the module.var acess
  It's not used for import ast element
  """

  #TODO to complete

  def __init__(self, var):
    NodeTransformer.__init__(self)
    self._var = var if isinstance(var, AstVariable) else AstVariable(var)

  def _genAffect(self, name):
    """
    generate affectation value
    """
    return [self._var.assign( ast.Name(name, Load()), name)]

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
#    #TODO do it for recursive module
#    def getModule(self, name):
#      if name not in self.content:
#        raise ImportError("No module named %s" % name)
#
#      l, v = self.content[name]
#      if l: return v #v is the module
#
#      m = Module()
#      self.content[name] = (True, m)
#      v(m)
#      return m
#
#  dictModule = DictModule()
#  __import__ = dictModule.getModule
#  """
#
#  def __init__(self, moduleRef, curPath=''):
#    NodeTransformer.__init__(self)
#
#    self.dict_imports = {} #import in a dict form
#
#    self._moduleRef = moduleRef
#    self._curPath = curPath
#
#
#
#  def main_visit(self, node):
#    #the node should be a module
#    res = self.visit(node)
#
#    dictModule_klass = self.genVar('DictModule')
#    dictModule_inst = self.genVar('dictModule')
#    before = str2ast(self.init_code, DictModule=dictModule_klass.name, dictModule=dictModule_inst.name)
#
#
#    for k, (vname, vast) in self.dict_imports.iteritems():
#      before += vast
#      before += str2ast("dictModule.add('%s', moduleFctVar)" % k, dictModule = dictModule_inst.name, moduleFctVar=vname.name)
#      pass
#
#    node.body = before + node.body
#    return node
#
#
#  def genImport(self, module, fctName):
#    """
#    Generate the import function for this name
#    The import function is in the form :
#    def fctName(genVar_398_module):
#      genVar_398_module.__file__ = "/my/module/file/path/toto/tutu"
#      genVar_398_module.__name__ = "toto.tutu"
#
#    It dont' return a module, just affection values to the parameter module
#    """
#
#    contentAst = ast.parse(module.getContent(), module.getPath(), 'exec').body
#    moduleVar = self.genVar('module')
#
#    contentAst = [
#        moduleVar.assign(Str(module.getPath()), '__file__'),
#        moduleVar.assign(Str('.'.join(module.getNames()[1:])), '__name__'), #TODO remove the [1:]
#    ] + ModuleAffectation(moduleVar.name).visit(contentAst)
#
#    arguments = ast.arguments([moduleVar.param()], None, None, [])
#    return [FunctionDef(fctName, arguments , contentAst, [] )]
#
#
#  def addImport(self, name):
#    """
#    from a name (and searching the reference of the current object)
#    return an absolute name for the import.
#    Put the module result into the inter dict
#    """
#
#    resModule = self._moduleRef.find(name, self._curPath)
#
#    fctName = self.genVar('importfct')
#
#    if resModule is None: #error case
#      codeAst = str2ast("""
#            def fctName(moduleVar):
#              raise ImportError("No module named %s")
#          """ % name, fctName = fctName.name)
#
#      self.dict_imports[name] = (fctName, codeAst)
#
#      return name
#
#    newName = '.'.join(resModule.getNames()[1:]) #TODO remove the [1:]
#    codeAst = self.genImport(resModule, fctName.name)
#
#    self.dict_imports[newName]  = (fctName, codeAst)
#
#    return newName
#
#
#  def visit_Import(self, node):
#    res = []
#
#    for alias in node.names:
#      name = alias.name
#      asname = alias.asname or name
#
#      #2 cases
#      # - import toto.tutu.titi as tralala => this is tralal = toto.tutu.titi => lo see after
#      # - import toto.tutu.titi => toto = toto, toto.tutu = toto.tutu, toto.tutu.titi = toto.tutu.titi
#      absName = self.addImport(name)
#
#      res += [
#        str2ast("asname = __import__('%s')" % absName, asname = asname)
#      ]
#
#    return res
#
#
#
#


#__EOF__

#!/usr/bin/env python

from ast import *
import ast, md5
import sys
import nodeTransformer
import os.path, os
import zipfile
from nodeTransformer import str2ast, AstVariable


#TODO for the future, add a list of import to include (for the __import__('name') def)
#TODO for the future, add a list of import to not include (because they are in a if)
#TODO do a PythonModule for .zip files
#TODO do a test on pyc and pyo files, saying it don't take them


class SimpleModuleResolver(object):

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
  def setName(self, name): self._name = name
  def __hash__(self): return hash(self._name)

  def __getitem__(self, name): return self.getChild(name)
  def __iter__(self): return iter(self.getChilds())

  def getUp(self): return self._up
  def setUp(self, up): self._up = up

  def getNamesAbs(self, nameList):
    return reduce(lambda e, n: e[n] , nameList, self)

  def getNames(self):
    if self._up is None:
      return [self._name] if self._name else list()
    return self._up.getNames() + [self._name]

  def __str__(self):
    return ('%(_up)s.%(_name)s' if self._up else '%(_name)s') % self.__dict__

  def __repr__(self):
    return '<%s content="%s">' % (self.__class__.__name__, str(self))


  def dump(self):
    """
    Return a couple :
    (hash, {})
    - The first element is the hash of the content
    - The second element is a dict of the childs {name : repr()}
    """
    hash_str = md5.new(self.getContent()).hexdigest()
    dict_repr = {c.getName():c.dump() for c in self}
    return (hash_str, dict_repr)


class PythonModuleList(PythonModule):
  """
  Represent a list of concrete modules
  As in python, each name is only found once (no same name at differents places)
  So it's like a single module with childs as all the modules togethers
  """

  def __init__(self, name='', up=None):
    PythonModule.__init__(self, name, up)
    self._modules = [] #order is important
    self._childs = {} #childs

  def addModule(self, mod):
    """
    get a module
    """
    self._modules.append(mod)

    for modChild in mod:
      name = modChild.getName()
      if name not in self._childs:
        self._childs[name] = modChild
        modChild.setUp(self._up)

  def getContent(self): return ''

  def getChild(self, name):
    try:
      return self._childs[name]
    except KeyError:
      raise NoModuleFound()

  def getChilds(self):
    return list(self._childs.iteritems())

  def getNamesAbs(self, nameList):
    if not nameList: return self

    curName = nameList[0]
    if curName in self._childs:
      return self._childs[curName].getNamesAbs(nameList[1:])

    return None

  def getNamesRel(self, nameListTo, nameListFrom):
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

  def getPathRel(self):
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
    return os.listdir(path) if self._f_isdir(path) else []

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
      return reduce( lambda r, n : r[n], path.split(os.path.sep)[1:], self._diskContent)
    except KeyError:
      return None

  def _f_listfiles(self, path):
    pathElem = self._s_getPathElement(path)
    if pathElem is None : return []
    return list(pathElem.iterkeys())

  def _f_join(self, *args): return os.path.sep.join(args)
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

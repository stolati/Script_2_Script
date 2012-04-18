#!/usr/bin/env python
import unittest, types, mock
import sys
import os.path

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

from methodVisitUtil import MethodVisitUtil, callOnBoth, AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.moreImport import *

testPath = os.path.join(os.path.dirname(__file__), 'importTest')


#class TestPythonModuleFile(unittest.TestCase):
#
#  def test_construction(self):
#    pmf = PythonModuleOnDisk(testPath)
#
#    waiting_for = ("('d41d8cd98f00b204e9800998ecf8427e', {"
#      "'importTest_complex': ('8f1fe1ae1a4c96bf0b748ce844749ebc', {"
#        "'toto': ('8173c640b6c07b3f0d47c9a8f45875b3', {}), "
#        "'tutu': ('8f134b982b689ecfb87ac0a03c7d774c', {})"
#      "}), "
#        "'importTest_first': ('15677e4928e7fe59a4da3544371a1895', {"
#        "'import_first': ('6f4114b0b9e2e71f075cb867b2ce8443', {})"
#      "}), "
#      "'importTest_simple': ('3a0008caa56ac47f82d9d19e07473efa', {})"
#    "})")
#
#    self.assertEquals(repr(pmf), waiting_for)
#
#
#class TestPythonModuleStatic(unittest.TestCase):
#
#  def test_construction(self):
#    paths = {
#      'importTest_complex' : {
#        'tutu.py': 'importTest_complex/tutu.py',
#        'toto.py': 'importTest_complex/toto.py',
#        '__init__.py': 'importTest_complex/__init__.py',
#      },
#      'importTest_first' :  {
#        'import_first.py' : 'importTest_first/import_first.py',
#        '__init__.py': 'importTest_first/__init__.py',
#      },
#      'importTest_empty': {},
#      'importTest_simple.py': 'importTest_simple.py',
#    }
#
#    pms = PythonModuleStatic(paths)
#
#    waiting_for = ("('d41d8cd98f00b204e9800998ecf8427e', {"
#      "'importTest_complex': ('9679640927855358ac46d17a76a10b5d', {"
#        "'toto': ('266020d79799fa1356744ff4af5d4869', {}), "
#        "'tutu': ('dc97b1a2e8269293e02aed087ff39cdc', {})"
#      "}), "
#      "'importTest_first': ('49c275c5921913e3c3fe90f08de0f9b7', {"
#        "'import_first': ('d714ffce32994cf49e1a05ea3d2c4e44', {})"
#      "}), "
#      "'importTest_simple': ('d5b1e8321944d1377924dd34bfbadf3d', {})"
#    "})")
#
#    self.assertEquals(repr(pms), waiting_for)
#
#
#class TestSimpleFileResolver(unittest.TestCase):
#
#  def setUp(self):
#    self.paths = {
#      'importTest_complex' : {
#        'tutu.py': 'importTest_complex/tutu.py',
#        'toto.py': 'importTest_complex/toto.py',
#        '__init__.py': 'importTest_complex/__init__.py',
#        'tyty': {
#          'trala.py': 'importTest_complex/tyty/trala.py',
#          '__init__.py': 'importTest_complex/tyty/__init__.py',
#        },
#      },
#      'importTest_first' :  {
#        'import_first.py' : 'importTest_first/import_first.py',
#        '__init__.py': 'importTest_first/__init__.py',
#      },
#      'imporTest_empty': {},
#      'importTest_simple.py': 'importTest_simple.py',
#    }
#
#
#  def test_simpleResolver(self):
#
#    testVals = [
#      #abs path
#      (('toto', ''), None),
#      (('importTest_simple', ''), 'importTest_simple.py'),
#      (('importTest_complex', ''), 'importTest_complex/__init__.py'),
#      (('importTest_complex.tutu', ''), 'importTest_complex/tutu.py'),
#
#      (('toto', 'importTest_first'), None),
#      (('importTest_simple', 'importTest_first'), 'importTest_simple.py'),
#      (('importTest_complex', 'importTest_first'), 'importTest_complex/__init__.py'),
#      (('importTest_complex.tutu', 'importTest_first'), 'importTest_complex/tutu.py'),
#
#      #rel path
#      (('import_first', 'importTest_first'), 'importTest_first/import_first.py'),
#      (('tutu', 'importTest_complex'), 'importTest_complex/tutu.py'),
#      (('tutu', 'importTest_complex.toto'), 'importTest_complex/tutu.py'),
#      (('toto', 'importTest_complex.tutu'), 'importTest_complex/toto.py'),
#      (('tyty.trala', 'importTest_complex.toto'), 'importTest_complex/tyty/trala.py'),
#    ]
#
#    pms = PythonModuleStatic(self.paths)
#    sfr = SimpleFileResolver(pms)
#
#    for (strTo, strFrom), resWait in testVals:
#      m = sfr.find(strTo, strFrom)
#      resReal = m.getContent() if m is not None else None
#      self.assertEquals(resWait, resReal)
#
#
#
#class TestMultipleModuleList(unittest.TestCase):
#
#  def setUp(self):
#    self.test_static = [
#      {
#        'a1' : {
#          'a.py': 'a1/a.py',
#          'b.py': 'a1/b.py',
#          '__init__.py': 'a1/__init__.py',
#          'c': {
#            'a.py': 'a/c/a.py',
#            '__init__.py': 'a/c/__init__.py',
#          },
#        },
#        'a2' :  {
#          'a.py' : 'a2/a.py',
#          '__init__.py': 'a2/__init__.py',
#        },
#        'a3.py': 'a3.py',
#      },
#      {
#        'a4' : {
#          'a.py': 'a4/a.py',
#          'b.py': 'a4/b.py',
#          '__init__.py': 'a4/__init__.py',
#          'c': {
#            'a.py': 'a4/c/a.py',
#            '__init__.py': 'a4/c/__init__.py',
#          },
#        },
#        'a5' :  {
#          'a.py' : 'a5/a.py',
#          '__init__.py': 'a5/__init__.py',
#        },
#        'a6.py': 'a6.py',
#      }
#    ]
#
#
#    place = os.path.join(testPath, 'onModule')
#
#    self.test_ondisk = [
#      os.path.join(place, 'importA'),
#      os.path.join(place, 'importB'),
#    ]
#
#    self.test_zip = [
#      os.path.join(place, 'importA.zip'),
#      os.path.join(place, 'importB.zip'),
#    ]
#
#    self.testVals = [
#      (('a1', ''), ('0/a1/__init__.py', '0.a1')), #load a module dir
#      (('a1.a', ''), ('0/a1/a.py', '0.a1.a')), #load a module file
#      (('a4', '0.a1'), ('1/a4/__init__.py', '1.a4')), #load a dir module from the other side
#      (('a4.a', '0.a1'), ('1/a4/a.py', '1.a4.a')), #load a file module from the other side
#      (('a', '0.a1'), ('0/a1/a.py', '0.a1.a')), #load a file from inside
#      (('c', '0.a1'), ('0/a1/c/__init__.py', '0.a1.c')), #load a dir from inside
#      (('c.a', '0.a1'), ('0/a1/c/a.py', '0.a1.c.a')), #load a dir/file from inside
#      (('a1.c.a', ''), ('0/a1/c/a.py', '0.a1.c.a')), #load a dir/file from base
#      (('a1.c.a', '1.a4.c.a'), ('0/a1/c/a.py', '0.a1.c.a')), #load a dir/file from other side
#      (('a', '0.a1.c'), ('0/a1/c/a.py', '0.a1.c.a')), #acces 'a' from a stuff
#      (('a', '0.a2'), ('0/a2/a.py', '0.a2.a')), #acess 'a' from another stuff
#
#      ##same as previous, the other way around
#      (('a4', ''), ('1/a4/__init__.py', '1.a4')), #load a module dir
#      (('a4.a', ''), ('1/a4/a.py', '1.a4.a')), #load a module file
#      (('a1', '1.a4'), ('0/a1/__init__.py', '0.a1')), #load a dir module from the other side
#      (('a1.a', '1.a4'), ('0/a1/a.py', '0.a1.a')), #load a file module from the other side
#      (('a', '1.a4'), ('1/a4/a.py', '1.a4.a')), #load a file from inside
#      (('c', '1.a4'), ('1/a4/c/__init__.py', '1.a4.c')), #load a dir from inside
#      (('c.a', '1.a4'), ('1/a4/c/a.py', '1.a4.c.a')), #load a dir/file from inside
#      (('a4.c.a', ''), ('1/a4/c/a.py', '1.a4.c.a')), #load a dir/file from base
#      (('a4.c.a', '0.a1.c.a'), ('1/a4/c/a.py', '1.a4.c.a')), #load a dir/file from other side
#      (('a', '1.a4.c'), ('1/a4/c/a.py', '1.a4.c.a')), #acces 'a' from a stuff
#      (('a', '1.a5'), ('1/a5/a.py', '1.a5.a')), #acess 'a' from another stuff
#    ]
#
#
#  def loopTestsOn(self, (moduleAFct, resAFct), (moduleBFct, resBFct)):
#
#    pml = PythonModuleList()
#
#    pml.addModule(moduleAFct)
#    pml.addModule(moduleBFct)
#
#    sfr = SimpleFileResolver(pml)
#
#    for (toStr, fromStr), (pathRes, nameRes) in self.testVals:
#      res = sfr.find(toStr, fromStr)
#      if res is None:
#        pathResReal, nameResReal = (None, None)
#      else:
#        pathResReal, nameResReal = res.getPath(), '.'.join(res.getNames())
#        pathResReal = resAFct(resBFct(pathResReal))
#
#      self.assertEquals((pathRes, nameRes), (pathResReal, nameResReal))
#
#
#  def testStaticStatic(self):
#
#    staticNewA = lambda name : PythonModuleStatic(self.test_static[0], name=name)
#    staticResA = lambda x:x
#    onDiskNewA = lambda name : PythonModuleOnDisk(self.test_ondisk[0], name=name)
#    onDiskResA = lambda s : s.replace(self.test_ondisk[0], '0')
#
#    staticNewB = lambda name : PythonModuleStatic(self.test_static[1], name=name)
#    staticResB = lambda x:x
#    onDiskNewB = lambda name : PythonModuleOnDisk(self.test_ondisk[1], name=name)
#    onDiskResB = lambda s : s.replace(self.test_ondisk[1], '1')
#
#    As = [(staticNewA, staticResA), (onDiskNewA, onDiskResA)]
#    Bs = [(staticNewB, staticResB), (onDiskNewB, onDiskResB)]
#
#    for a in As:
#      for b in Bs:
#        self.loopTestsOn(a, b)
#
#


class TestMoreImport(AstTransformerTestClass):


  def setUp(self):
    self.test_files = os.path.join(os.path.dirname(__file__), 'importTest')
    self.old_path = sys.path

    sys.path = [self.test_files] + sys.path

  def tearDown(self):
    sys.path = self.old_path


  def test_Import(self):

    def test_SimpleImport(m):
      m('begin')
      import importTest_simple
      m(importTest_simple.v)
      m(importTest_simple.f.__name__)
      m(importTest_simple.c.__name__)
      m(importTest_simple.__name__)
      m(importTest_simple.__file__)
      m('end')

    self.checkFctOnLocals(locals(), MoreImport(sys.path), mock.Mock)


#  def test_empty(self):
#
#    def test_empty(m):
#      m('begin')
#      try:
#        import importTest_empty
#      except ImportError:
#        m('ImportError error')
#      m('end')
#
#    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)
#
#
#  def test_directory(self):
#
#    def test_dir(m):
#      m('begin')
#      import importTest_complex
#      m(importTest_complex.v)
#      m(importTest_complex.f.__name__)
#      m(importTest_complex.c.__name__)
#      m(importTest_complex.__name__)
#      m(importTest_complex.__file__)
#      m('end')
#
#    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)
#
#
#  def test_first(self):
#
#    def test_first(m):
#      m('begin')
#      import importTest_first
#      m(importTest_first.a)
#      m('end')
#
#    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)
#
#
#  def test_importMultiple(self):
#
#    def test_importMultiple(m):
#      m('begin')
#      import importTest_first
#      m(importTest_first.a)
#      importTest_first.a = 1
#      m(importTest_first.a)
#
#      import importTest_first
#      m(importTest_first.a)
#      importTest_first.a = 2
#      m(importTest_first.a)
#
#      importTest_first = __import__('importTest_first')
#      m(importTest_first.a)
#      importTest_first.a = 3
#      m(importTest_first.a)
#
#      import importTest_first as toto
#      m(importTest_first.a, toto.a)
#      importTest_first.a = 4
#      m(importTest_first.a, toto.a)
#      m('end')
#
#    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)
#
#
#  def test_subImport(self):
#
#    def test_subImport(m):
#      m('begin')
#
#      #import importTest_complex.toto
#      import importTest_complex.tutu
#
#      m('end')
#
#    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)



#TODO test import in import
#TODO test import a.b.c
#TODO test import in import in a.b.c
#TODO test multi same import ( a.b then a, a the a, a then a.b )


if __name__ == "__main__":
  unittest.main()



#__EOF__

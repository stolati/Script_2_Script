#!/usr/bin/env python
import unittest, types, mock
import sys
import os.path

from methodVisitUtil import MethodVisitUtil, callOnBoth, AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.moreImport import *

testPath = os.path.join(os.path.dirname(__file__), 'importTest')


class TestPythonModuleFile(unittest.TestCase):

  def test_construction(self):
    pmf = PythonModuleOnDisk(testPath)

    waiting_for = ("('d41d8cd98f00b204e9800998ecf8427e', {"
      "'importTest_complex': ('8f1fe1ae1a4c96bf0b748ce844749ebc', {"
        "'toto': ('8173c640b6c07b3f0d47c9a8f45875b3', {}), "
        "'tutu': ('8f134b982b689ecfb87ac0a03c7d774c', {})"
      "}), "
        "'importTest_first': ('15677e4928e7fe59a4da3544371a1895', {"
        "'import_first': ('6f4114b0b9e2e71f075cb867b2ce8443', {})"
      "}), "
      "'importTest_simple': ('3a0008caa56ac47f82d9d19e07473efa', {})"
    "})")

    self.assertEquals(repr(pmf), waiting_for)


class TestSimpleFileResolver(unittest.TestCase):

  def setUp(self):
    self.paths = ('', {
      'importTest_complex' : ('importTest_complex/__init__.py', {
        'tutu': ('importTest_complex/tutu.py', {}),
        'toto': ('importTest_complex/toto.py', {}),
        #'__init__': None,
      }),
      'importTest_first' : ('importTest_first/__init__.py', {
        'import_first' : ('importTest_first/import_first.py', {}),
        #'__init__': None,
      }),
      'importTest_simple': ('importTest_simple.py', {}),
    })

  def test_simpleResolver(self):

    pms = PythonModuleStatic(self.paths)

    #self.assertEquals(
    #    pms.sfr.getModule('importTest_complex'),
    #    ['importTest_complex/', '__init__.py']
    #)


#    self.assertEquals(sfr._callPythonPath(['importTest_complex/']), None)
#    self.assertEquals(sfr._callPythonPath(['importTest_complex', 'toto']), ['importTest_complex/', 'toto.py'])
#    self.assertEquals(sfr._callPythonPath(['importTest_complex', 'titi']), None)
#    self.assertEquals(sfr._callPythonPath(['importTest_simple']), ['importTest_simple.py'])
#
#  def test_getFileObjectFromPath(self):
#
#    sfr = SimpleFileResolver(self.paths)
#
#    self.assertEquals(sfr._path2file(['importTest_complex/', '__init__.py']), 'importTest_complex/__init__.py content')
#    self.assertEquals(sfr._path2file(['importTest_complex/', 'toto.py']), 'importTest_complex/toto.py content')
#    self.assertEquals(sfr._path2file(['importTest_simple.py']), 'importTest_simple.py content')
#
#
#  def test_simpleResolve(self):
#
#    sfr = SimpleFileResolver(self.paths)
#
#    self.assertEquals(sfr.simpleFind('', 'importTest_simple'), ['importTest_simple.py'])
#    self.assertEquals(sfr.simpleFind('', 'titi'), None)
#    self.assertEquals(sfr.simpleFind('toto', 'titi'), None)
#    self.assertEquals(sfr.simpleFind('importTest_simple', 'importTest_simple'), ['importTest_simple.py'])
#
#    self.assertEquals(sfr.simpleFind('importTest_complex.__init__', 'titi'), None)
#    self.assertEquals(sfr.simpleFind('importTest_complex.__init__', 'toto'), ['importTest_complex/', 'toto.py'])


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








#class TestMoreImport(AstTransformerTestClass):
#
#
#  def setUp(self):
#    self.test_files = os.path.join(os.path.dirname(__file__), 'importTest')
#    self.old_path = sys.path
#
#    sys.path = [self.test_files] + sys.path
#
#  def tearDown(self):
#    sys.path = self.old_path
#
#
#  def test_Import(self):
#
#    def test_SimpleImport(m):
#      m('begin')
#      import importTest_simple
#      m(importTest_simple.v)
#      m(importTest_simple.f.__name__)
#      m(importTest_simple.c.__name__)
#      m(importTest_simple.__name__)
#      m(importTest_simple.__file__)
#      m('end')
#
#    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)
#
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

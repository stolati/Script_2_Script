#!/usr/bin/env python
import unittest, types, mock
import sys
import os.path

from methodVisitUtil import MethodVisitUtil, callOnBoth, AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.moreImport import MoreImport

#working import
#import failing (both for elements)

print __file__




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

    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)

  def test_empty(self):

    def test_empty(m):
      m('begin')
      try:
        import importTest_empty
      except ImportError:
        m('ImportError error')
      m('end')

    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)


  def test_directory(self):

    def test_dir(m):
      m('begin')
      import importTest_complex
      m(importTest_complex.v)
      m(importTest_complex.f.__name__)
      m(importTest_complex.c.__name__)
      m(importTest_complex.__name__)
      m(importTest_complex.__file__)
      m('end')

    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)


  def test_first(self):

    def test_first(m):
      m('begin')
      import importTest_first
      m(importTest_first.a)
      m('end')

    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)


  def test_importMultiple(self):

    def test_importMultiple(m):
      m('begin')
      import importTest_first
      m(importTest_first.a)
      importTest_first.a = 1
      m(importTest_first.a)

      import importTest_first
      m(importTest_first.a)
      importTest_first.a = 2
      m(importTest_first.a)

      importTest_first = __import__('importTest_first')
      m(importTest_first.a)
      importTest_first.a = 3
      m(importTest_first.a)

      import importTest_first as toto
      m(importTest_first.a, toto.a)
      importTest_first.a = 4
      m(importTest_first.a, toto.a)
      m('end')

    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)


  def test_subImport(self):

    def test_subImport(m):
      m('begin')

      #import importTest_complex.toto
      import importTest_complex.tutu

      m('end')

    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)



#TODO test import in import
#TODO test import a.b.c
#TODO test import in import in a.b.c
#TODO test multi same import ( a.b then a, a the a, a then a.b )


if __name__ == "__main__":
  unittest.main()



#__EOF__

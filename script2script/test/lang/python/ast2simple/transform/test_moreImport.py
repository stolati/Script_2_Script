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
      m('end')

    #def test_DoubleImport(m):
    #  m('begin')
    #  import importTest_simple
    #  #m(importTest_simple.a)
    #  m('end')

    self.checkFctOnLocals(locals(), MoreImport(), mock.Mock)



#class TestTrySimplifier(AstTransformerTestClass):
#
#  def test_simpleTry(self):
#
#    def test_simple_tryExcept(m, e):
#      m('begin')
#      try:
#        m('try')
#      except:
#        m('except')
#      m('end')
#
#    def test_simple_tryFinally(m, e):
#      m('begin')
#      try:
#        m('try')
#      finally:
#        m('finally')
#      m('end')
#
#    def test_complex_tryExceptFinally(m, e):
#      m('begin')
#      try:
#        m('try')
#      except:
#        m('except')
#      else:
#        m('else')
#      finally:
#        m('finally')
#      m('end')
#
#    def test_complex_named(m, e):
#      m('begin')
#      try:
#        m('before ve')
#        raise ValueError('toto')
#        m('after ve')
#      except ValueError as ve:
#        m('value err')
#      else:
#        m('else')
#      finally:
#        m('finally')
#      m('end')
#
#    def test_complex_named_exceptAll(m, e):
#      m('begin')
#      try:
#        m('before ve')
#        raise ValueError('toto')
#        m('after ve')
#      except:
#        m('value err')
#      else:
#        m('else')
#      finally:
#        m('finally')
#      m('end')
#
#    def test_complex_named_not_waited(m, e):
#      m('begin')
#      try:
#        m('before ve')
#        raise e
#        m('after ve')
#      except ValueError as ve:
#        m('value err')
#      except ValueError:
#        m('tutu')
#      except :
#        m('tralala')
#      else:
#        m('else')
#      finally:
#        m('finally')
#      m('end')
#
#    def test_empty_try(m, e):
#      m('begin')
#      try:
#        pass
#      except:
#        m('except')
#      else:
#        m('else')
#      finally:
#        m('finally')
#      m('end')
#
#    def test_else_noFinally(m, e):
#      m('begin')
#      try:
#        m('try')
#      except:
#        m('except')
#      else:
#        m('else')
#      m('end')
#
#    def test_else_noFinally(m, e):
#      m('begin')
#      try:
#        pass
#      except:
#        m('except')
#      else:
#        m('else')
#      m('end')
#
#    def test_else_noFinally(m, e):
#      m('begin')
#      try:
#        m('try')
#      except:
#        m('except')
#      else:
#        m('else')
#        raise e
#        m('error')
#      finally:
#        m('finally')
#      m('end')
#
#    self.checkFctOnLocals(locals(), TrySimplifier(), mock.Mock, Exception())



if __name__ == "__main__":
  unittest.main()



#__EOF__

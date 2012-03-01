#!/usr/bin/env python
import unittest, types, mock
import sys

from methodVisitUtil import MethodVisitUtil, callOnBoth
from script2script.lang.python.ast2simple.transform.trySimplifier import TrySimplifier


class TestTrySimplifier(unittest.TestCase):

  def dualTestFct(self, fctOri, *args):
    resOri, resVisited = callOnBoth(fctOri, TrySimplifier(), *args)
    if resOri != resVisited:
      print "differents : "
      print resOri
      print resVisited
    self.assertEqual(resOri, resVisited, "error on function %s" % fctOri.func_name)

  def checkFctOnLocals(self, locals_values, *args):
    for k, v in locals_values.iteritems():
      if k.startswith('test_') and isinstance(v, types.FunctionType):
        self.dualTestFct(v, *args)

  def test_simpleTry(self):

    def test_simple_tryExcept(m, e):
      m('begin')
      try:
        m('try')
      except:
        m('except')
      m('end')

    def test_simple_tryFinally(m, e):
      m('begin')
      try:
        m('try')
      finally:
        m('finally')
      m('end')

    def test_complex_tryExceptFinally(m, e):
      m('begin')
      try:
        m('try')
      except:
        m('except')
      else:
        m('else')
      finally:
        m('finally')
      m('end')

    def test_complex_named(m, e):
      m('begin')
      try:
        m('before ve')
        raise ValueError('toto')
        m('after ve')
      except ValueError as ve:
        m('value err')
      else:
        m('else')
      finally:
        m('finally')
      m('end')

    def test_complex_named_exceptAll(m, e):
      m('begin')
      try:
        m('before ve')
        raise ValueError('toto')
        m('after ve')
      except:
        m('value err')
      else:
        m('else')
      finally:
        m('finally')
      m('end')

    def test_complex_named_not_waited(m, e):
      m('begin')
      try:
        m('before ve')
        raise e
        m('after ve')
      except ValueError as ve:
        m('value err')
      except ValueError:
        m('tutu')
      except :
        m('tralala')
      else:
        m('else')
      finally:
        m('finally')
      m('end')

    def test_empty_try(m, e):
      m('begin')
      try:
        pass
      except:
        m('except')
      else:
        m('else')
      finally:
        m('finally')
      m('end')

    def test_else_noFinally(m, e):
      m('begin')
      try:
        m('try')
      except:
        m('except')
      else:
        m('else')
      m('end')

    def test_else_noFinally(m, e):
      m('begin')
      try:
        pass
      except:
        m('except')
      else:
        m('else')
      m('end')

    def test_else_noFinally(m, e):
      m('begin')
      try:
        m('try')
      except:
        m('except')
      else:
        m('else')
        raise e
        m('error')
      finally:
        m('finally')
      m('end')

    self.checkFctOnLocals(locals(), Exception())



if __name__ == "__main__":
  unittest.main()



#__EOF__

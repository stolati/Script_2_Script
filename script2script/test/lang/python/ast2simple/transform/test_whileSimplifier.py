#!/usr/bin/env python
import unittest, types
import sys
from script2script.test import mock

from methodVisitUtil import MethodVisitUtil, callOnBoth, AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.whileSimplifier import WhileSimplifier, HaveBreak

#util function, true the firsts n times, then false
class Cdt:
  """Helper class in a function form, is true n times, then false"""

  def __init__(self, n):
    """
    set the number of trues
    @param n: the number of true before false
    """
    self._n = n
    self._c = 0

  def __call__(self):
    """
    @return: true or false, depending of the number of calls
    """
    self._c +=1
    return self._n <= self._c


class TestHaveBreak(unittest.TestCase):
  #test functions, not created to be launched
  def whileWithElse():
    while a():
      b()
    else: c()

  def whileWithBreak():
    while a(): b(); break

  def whileWithBoth():
    while a(): b(); break
    else: c()

  def whileComplexeWithout():
    while a():
      for i in vi:
        if a : break
      while c:
        if f: break;
    else: d()

  def test_haveBreak(self):
    testCases = [
        (TestHaveBreak.whileWithElse, False),
        (TestHaveBreak.whileWithBreak, True),
        (TestHaveBreak.whileWithBoth, True),
        (TestHaveBreak.whileComplexeWithout, False),
    ]

    for k, expectedRes in testCases:
      mvu = MethodVisitUtil(k)
      for_ast = mvu.getAst().body[0].body[0]
      res = HaveBreak.inside(for_ast)
      self.assertEqual(res, expectedRes, "failed on function %s" % k.func_name)


class TestWhileSimplifier(AstTransformerTestClass):

  def test_breakNElse(self):
    testCases = [
        (TestHaveBreak.whileWithElse, False),
        (TestHaveBreak.whileWithBreak, False),
        (TestHaveBreak.whileWithBoth, True),
        (TestHaveBreak.whileComplexeWithout, False),
    ]

    for k, expectedRes in testCases:
      mvu = MethodVisitUtil(k)
      while_ast = mvu.getAst().body[0].body[0]
      res = WhileSimplifier().breakNElse(while_ast)
      self.assertEqual(res, expectedRes, "failed on function %s" % k.func_name)

  #test differents flow
  def test_simpleWhile_flow(self):

    def test_while_empty(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c(): pass
      m('end')

    def test_while_simple(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c(): m()
      m('end')

    def test_whilefor_emptyElse(m, Cdt):
      m('begin')
      for i in range(10): pass
      else: m('else')
      m('end')

    def test_while_nilElse(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c(): m()
      else: m('else')
      m('end')

    def test_while_simpleElse(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c(): m()
      else: m('else')
      m('end')

    def test_while_break(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c > 5: break
        m(c._c)
      m('end')

    def test_while_continue(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c < 2: continue
        m(c._c)
        if i > 5: continue
        m(c._c)
      m('end')

    def test_while_continue_break(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if i < 2: continue
        m(c._c)
        if i > 5: break
        m(c._c)
      m('end')

    def test_while_multi(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(i, 'begin')
        c1 = Cdt(10)
        while c1():
          m(c._c, c1._c)
        m(c._c, 'end')
      m('end')

    self.checkFctOnLocals(locals(), WhileSimplifier(), mock.Mock, Cdt)

  def test_complexWhile(self):

    def test_while_empty(m, Cdt):
      m('begin')
      while True:
          m('break')
          break
          m('ko')
      else: m('else')
      m('end')

    def test_while_nil(m, Cdt):
      m('begin')
      while False:
          m('break')
          break
          m('ko')
      else: m('else')
      m('end')

    def test_while_simple(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if False: break
      else: m('else')
      m('end')

    def test_while_break(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c > 5: m('break'); break; m('ko')
        m(c._c)
      else: m('titi')
      m('end')

    def test_while_continue(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c < 2: m('continue'); continue
        if False: m('break'); break; m('ko')
        m(c._c)
        if c._c > 5: m('continue'); continue
        m(c._c)
      else:
        m('tutu')
      m('end')

    def test_while_continue_break(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c < 2: continue
        m(c._c)
        if c._c > 5: break
        m(c._c)
      else: m('else')
      m('end')

    def test_while_multi_onlyBreak(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c, 'begin')
        if c._c > 5: m('break 2'); break
        m('no break')
        c1 = Cdt(10)
        while c1():
          if c1._c > 4: m('break 2'); break
          m(c._c, c1._c)
        else: m('else 2')
        m(c1._c, 'end')
      else: m('else 1')
      m('end')

    def test_while_multi_oneBreak1(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c, 'begin')
        if c._c > 5: m('break 2'); break
        m('no break')
        c1 = Cdt(10)
        while c1():
          if False: m('break 2'); break
          m(c._c, c1._c)
        else: m('else 2')
        m(c._c, 'end')
      else: m('else 1')
      m('end')

    def test_while_multi_oneBreak2(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c, 'begin')
        if False: m('break 2'); break
        m('no break')
        c1 = Cdt(10)
        while c1():
          if c1._c > 4: m('break 2'); break
          m(c._c, c1._c)
        else: m('else 2')
        m(c._c, 'end')
      else: m('else 1')
      m('end')

    def test_while_multi_noBreak(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c, 'begin')
        if False: m('break 2'); break
        m('no break')
        c1 = Cdt(10)
        while c1():
          if False: m('break 2'); break
          m(c._c, c1._c)
        else: m('else 2')
        m(c._c, 'end')
      else: m('else 1')
      m('end')

    self.checkFctOnLocals(locals(), WhileSimplifier(), mock.Mock, Cdt)

if __name__ == "__main__":
  unittest.main()



#__EOF__

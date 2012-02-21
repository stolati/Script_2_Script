#!/usr/bin/env python
import unittest, types, mock
import sys

from methodVisitUtil import MethodVisitUtil, callOnBoth
from all2all.lang.python.ast2simple.transform.whileSimplifier import WhileSimplifier, HaveBreak

#util function, true the firsts n times, then false
class Cdt:
    def __init__(self, n):
        self._n = n
        self._c = 0
  
    def __call__(self):
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


class TestWhileSimplifier(unittest.TestCase):

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

  def dualTestFct(self, fctOri, *args):
    resOri, resVisited = callOnBoth(fctOri, WhileSimplifier(), *args)

    if resOri != resVisited:
      print 'testing %s' % fctOri.func_name
      print 'result : %s \n %s' % (resOri, resVisited) #TODO remove

    self.assertEqual(resOri, resVisited, "error on function %s" % fctOri.func_name)

  def checkFctOnLocals(self, locals_values, *args):
    for k, v in locals_values.iteritems():
      if k.startswith('while_') and isinstance(v, types.FunctionType):
        self.dualTestFct(v, *args)

        
  #test differents flow
  def test_simpleWhile_flow(self):

    def while_empty(m, Cdt):
      m('begin')
      c = Cdt(10) 
      while c(): pass
      m('end')

    def while_simple(m, Cdt):
      m('begin')
      c = Cdt(10) 
      while c(): m()
      m('end')

    def whilefor_emptyElse(m, Cdt):
      m('begin')
      for i in range(10): pass
      else: m('else')
      m('end')

    def while_nilElse(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c(): m()
      else: m('else')
      m('end')

    def while_simpleElse(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c(): m()
      else: m('else')
      m('end')

    def while_break(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c > 5: break
        m(c._c)
      m('end')

    def while_continue(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c < 2: continue
        m(c._c)
        if i > 5: continue
        m(c._c)
      m('end')

    def while_continue_break(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if i < 2: continue
        m(c._c)
        if i > 5: break
        m(c._c)
      m('end')

    def while_multi(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(i, 'begin')
        c1 = Cdt(10)
        while c1():
          m(c._c, c1._c)
        m(c._c, 'end')
      m('end')

    self.checkFctOnLocals(locals(), Cdt)

  def test_complexWhile(self):

    def while_empty(m, Cdt):
      m('begin')
      while True:
          m('break')
          break
          m('ko')
      else: m('else')
      m('end')

    def while_nil(m, Cdt):
      m('begin')
      while False:
          m('break')
          break
          m('ko')
      else: m('else')
      m('end')

    def while_simple(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if False: break
      else: m('else')
      m('end')

    def while_break(m, Cdt):
      m('begin')
      c = Cdt(10)
      while c():
        m(c._c)
        if c._c > 5: m('break'); break; m('ko')
        m(c._c)
      else: m('titi')
      m('end')

    def while_continue(m, Cdt):
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

    def while_continue_break(m, Cdt):
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

    def while_multi_onlyBreak(m, Cdt):
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

    def while_multi_oneBreak1(m, Cdt):
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

    def while_multi_oneBreak2(m, Cdt):
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

    def while_multi_noBreak(m, Cdt):
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

    self.checkFctOnLocals(locals(), Cdt)

if __name__ == "__main__":
  unittest.main()



#__EOF__

#!/usr/bin/env python
import unittest, types, mock

from methodVisitUtil import MethodVisitUtil, callOnBoth
from forIntoWhile import ForIntoWhile, HaveBreak

class TestHaveBreak(unittest.TestCase):

  #test functions, not created to be launched
  def forWithElse():
    for e in v: d()
    else: d()

  def forWithBreak():
    for e in ve: d(); break

  def forWithBoth():
    for e in ve: d(); break
    else: d()

  def forComplexeWithout():
    for e in ve:
      for i in vi:
        if a : break
      while c:
        if f: break;
    else: d()

  def test_haveBreak(self):
    testCases = [
        (TestHaveBreak.forWithElse, False),
        (TestHaveBreak.forWithBreak, True),
        (TestHaveBreak.forWithBoth, True),
        (TestHaveBreak.forComplexeWithout, False),
    ]

    for k, expectedRes in testCases:
      mvu = MethodVisitUtil(k)
      for_ast = mvu.getAst().body[0].body[0]
      res = HaveBreak.inside(for_ast)
      self.assertEqual(res, expectedRes, "failed on function %s" % k.func_name)


class TestForIntoWhile(unittest.TestCase):

  def test_breakNElse(self):
    testCases = [
        (TestHaveBreak.forWithElse, False),
        (TestHaveBreak.forWithBreak, False),
        (TestHaveBreak.forWithBoth, True),
        (TestHaveBreak.forComplexeWithout, False),
    ]

    for k, expectedRes in testCases:
      mvu = MethodVisitUtil(k)
      for_ast = mvu.getAst().body[0].body[0]
      res = ForIntoWhile().breakNElse(for_ast)
      self.assertEqual(res, expectedRes, "failed on function %s" % k.func_name)

  def dualTestFct(self, fctOri, *args):
    print 'testing %s' % fctOri.func_name
    resOri, resVisited = callOnBoth(fctOri, ForIntoWhile(), *args)
    if resOri == resVisited : print 'All is OK'
    else: print 'result : %s \n %s' % (resOri, resVisited)
    self.assertEqual(resOri, resVisited, "error on function %s" % fctOri.func_name)

  def checkFctOnLocals(self, locals_values, *args):
    for k, v in locals_values.iteritems():
      if k.startswith('for_') and isinstance(v, types.FunctionType):
        self.dualTestFct(v, *args)


  #test different iterator in for
  def test_simpleFor_iter(self): #TODO

    def for_simple(m, l):
      m('begin')
      for e in l:
        m(e)
      else: m('else')
      m('end')

    def for_continue(m, l):
      m('begin')
      for e in l:
        m(e)
        continue
        m('ko')
      else: m('else')
      m('end')


    self.checkFctOnLocals(locals(), range(10))
    self.checkFctOnLocals(locals(), list())

  def test_complexFor_iter(self): #TODO

    def for_simple(m, l):
      m('begin')
      for e in l:
        m(e)
        if False: break
        m(e)
      else: m('else')
      m('end')

    def for_continue(m, l):
      m('begin')
      for e in l:
        m(e)
        if False: break
        m(e)
        continue
        m('ko')
      else: m('else')
      m('end')

    self.checkFctOnLocals(locals(), range(10))
    self.checkFctOnLocals(locals(), list())


  #test differents flow
  def test_simpleFor_flow(self):

    def for_empty(m):
      m('begin')
      for i in range(10): pass
      m('end')

    def for_nil(m):
      m('begin')
      for i in []: m()
      m('end')

    def for_simple(m):
      m('begin')
      for i in range(10): m(i)
      m('end')

    def for_emptyElse(m):
      m('begin')
      for i in range(10): pass
      else: m('else')
      m('end')

    def for_nilElse(m):
      m('begin')
      for i in []: m()
      else: m('else')
      m('end')

    def for_simpleElse(m):
      m('begin')
      for i in range(10): m(i)
      else: m('else')
      m('end')

    def for_break(m):
      m('begin')
      for i in range(10):
        m(i)
        if i > 5: break
        m(i)
      m('end')

    def for_continue(m):
      m('begin')
      for i in range(10):
        m(i)
        if i < 2: continue
        m(i)
        if i > 5: continue
        m(i)
      m('end')

    def for_continue_break(m):
      m('begin')
      for i in range(10):
        m(i)
        if i < 2: continue
        m(i)
        if i > 5: break
        m(i)
      m('end')

    def for_multi(m):
      m('begin')
      for i in range(10):
        m(i, 'begin')
        for j in range(10):
          m(i, j)
        m(i, 'end')
      m('end')

    self.checkFctOnLocals(locals())

  def test_complexFor(self):

    def for_empty(m):
      m('begin')
      for i in range(10): m('break'); break; m('ko')
      else: m('else')
      m('end')

    def for_nil(m):
      m('begin')
      for i in []: m(); break; m('ko')
      else: m('else')
      m('end')

    def for_simple(m):
      m('begin')
      for i in range(10):
        m(i)
        if False: break
      else: m('else')
      m('end')

    def for_break(m):
      m('begin')
      for i in range(10):
        m(i)
        if i > 5: m('break'); break; m('ko')
        m(i)
      else: m('titi')
      m('end')

    def for_continue(m):
      m('begin')
      for i in range(10):
        m(i)
        if i < 2: m('continue'); continue
        if False: m('break'); break; m('ko')
        m(i)
        if i > 5: m('continue'); continue
        m(i)
      else:
        m('tutu')
      m('end')

    def for_continue_break(m):
      m('begin')
      for i in range(10):
        m(i)
        if i < 2: continue
        m(i)
        if i > 5: break
        m(i)
      else: m('else')
      m('end')

    def for_multi_onlyBreak(m):
      m('begin')
      for i in range(10):
        m(i, 'begin')
        if i > 5: m('break 2'); break
        m('no break')
        for j in range(10):
          if j > 4: m('break 2'); break
          m(i, j)
        else: m('else 2')
        m(i, 'end')
      else: m('else 1')
      m('end')

    def for_multi_oneBreak1(m):
      m('begin')
      for i in range(10):
        m(i, 'begin')
        if i > 5: m('break 2'); break
        m('no break')
        for j in range(10):
          if False: m('break 2'); break
          m(i, j)
        else: m('else 2')
        m(i, 'end')
      else: m('else 1')
      m('end')

    def for_multi_oneBreak2(m):
      m('begin')
      for i in range(10):
        m(i, 'begin')
        if False: m('break 2'); break
        m('no break')
        for j in range(10):
          if j > 4: m('break 2'); break
          m(i, j)
        else: m('else 2')
        m(i, 'end')
      else: m('else 1')
      m('end')

    def for_multi_noBreak(m):
      m('begin')
      for i in range(10):
        m(i, 'begin')
        if False: m('break 2'); break
        m('no break')
        for j in range(10):
          if False: m('break 2'); break
          m(i, j)
        else: m('else 2')
        m(i, 'end')
      else: m('else 1')
      m('end')

    self.checkFctOnLocals(locals())

    #TODO test with a multiple values assign


if __name__ == "__main__":
  unittest.main()



#__EOF__

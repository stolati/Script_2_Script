#!/usr/bin/env python
import unittest, mock

from methodVisitUtil import AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.rmSyntaxicSugar import *


class TestDeleteOnlyOne(AstTransformerTestClass):

  def test_delete(self):

    def test_singleDel(m):
      class O: pass

      a = 3
      o = O()
      o.titi = 'titi'
      o.tutu = 'tutu'
      l = range(10)
      d = {'a': 3, 'b': 10}

      del a
      del o.titi
      del l[3]
      del d['a']

      m('a' in locals())
      m(hasattr(o, 'titi'))
      m(hasattr(o, 'tutu'))
      m(l)
      m(d)

    def test_multipleDel(m):
      class O: pass

      a = 3
      o = O()
      o.titi = 'titi'
      o.tutu = 'tutu'
      l = range(10)
      d = {'a': 3, 'b': 10}

      del a, o.titi, l[3], d['a']

      m('a' in locals())
      m(hasattr(o, 'titi'))
      m(hasattr(o, 'tutu'))
      m(l)
      m(d)

    self.checkFctOnLocals(locals(), DeleteOnlyOne(), mock.Mock)


class TestAssignOnlyOne(AstTransformerTestClass):


  def test_Assign(self):

    def test_singleAssign(m):
      class O: pass
      a = 3
      b = (2928, 3298)
      o = O()
      o.toto = 234897
      m(a, b, o.toto)

    def test_multipeAssign_simple(m):
      a, b, c = range(3)
      (a, b, c) = range(3)
      [a, b, c] = range(3)

    def test_multipeAssign_slicing(m):
      l = range(10)
      l[1], l[2], l[3] = range(3)
      (l[4], l[5], l[6]) = range(3)
      [l[7], l[8], l[9]] = range(3)

    def test_multipeAssign_slicing(m):
      class O: pass
      o = O()
      o.t1, o.t2, o.t3 = range(3)
      (o.t1, o.t2, o.t3) = range(3)
      [o.t1, o.t2, o.t3] = range(3)

    def test_assignRecursive(m):
      (a, [b, (c), d], e), f = [[[], [3, [4], 5], 10], 11]
      m(a, b, c, d, e, f)
      (a, [b, (c), d], e), f = (((), (3, (4,), 5), 10), 11)
      m(a, b, c, d, e, f)

    def test_assignError(m):
      m('begin')
      try:
        m('before a,b = 5')
        a, b = 5
        m('after a,b = 5')
      except TypeError:
        m('error type error')

      try:
        m('before a,b = ()')
        a, b = ()
        m('after a,b = ()')
      except ValueError:
        m('error ValueError to few')

      try:
        m('before a,b = range(10)')
        a, b = range(10)
        m('after a,b = range(10)')
      except ValueError:
        m('error ValueError to many')

    def test_assignErrorRecursive(m):
      m('begin')
      try:
        m('before TypeError')
        (a, [b, (c), d], e), f = [[[], [3, 4, 5], 10], 11]
        m('after TypeError')
      except TypeError:
        m('error type error')

      try:
        m('before too few')
        (a, [b, (c, d), e], f), f = [[[], [3, [4], 5], 10], 11]
        m('after too few')
      except ValueError:
        m('error ValueError to few')

      try:
        m('before too much')
        (a, [b, (c), d], e), f = [[[], [3, [4, 6], 5], 10], 11]
        m('after too much')
      except ValueError:
        m('error ValueError to many')


    self.checkFctOnLocals(locals(), AssignOnlyOne(), mock.Mock)



if __name__ == "__main__":
  unittest.main()



#__EOF__

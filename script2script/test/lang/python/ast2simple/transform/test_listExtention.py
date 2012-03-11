#!/usr/bin/env python
import unittest, mock

from methodVisitUtil import AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.listExtention import *


class TestListExtention(AstTransformerTestClass):

  def test_empty(self):
    def test_emptyList(m):
      m('begin')
      a = []
      m(a)
      m([])
      m('end')

    self.checkFctOnLocals(locals(), ListExtention(), mock.Mock)


class TestTupleExtention(AstTransformerTestClass):

  def test_empty(self):
    def test_emptyList(m):
      m('begin')
      a = ()
      m(a)
      m(())
      m((((),),))
      m('end')

    self.checkFctOnLocals(locals(), TupleExtention(), mock.Mock)


class TestDictExtention(AstTransformerTestClass):

  def test_empty(self):
    def test_emptyDict(m):
      m('begin')
      a = {}
      m(a)
      m([{}])
      m('end')

    self.checkFctOnLocals(locals(), DictExtention(), mock.Mock)



if __name__ == "__main__":
  unittest.main()



#__EOF__

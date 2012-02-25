#!/usr/bin/env python
import unittest, types, mock
import sys

from all2all.lang.python.ast2simple.transform.cleanJumps import CleanJumps
from methodVisitUtil import callOnBoth

class Test_CleanJumps(unittest.TestCase):

  def dualTestFct(self, fctOri, *args):
    resOri, resVisited = callOnBoth(fctOri, CleanJumps(), *args)

    if resOri != resVisited:
      print 'testing %s' % fctOri.func_name
      print 'result : %s \n %s' % (resOri, resVisited) #TODO remove

    self.assertEqual(resOri, resVisited, "error on function %s" % fctOri.func_name)

  def checkFctOnLocals(self, locals_values, *args):
    for k, v in locals_values.iteritems():
      if k.startswith('test_') and isinstance(v, types.FunctionType):
        self.dualTestFct(v, *args)

  def test_return(self):
    """ """

    def test_empty(m): pass

    def test_no_return(m): m('no_return')

    def test_simple_return(m): m('1'); return; m('2')

    def test_return_value(m): m('1'); return 3; m('2')

    self.checkFctOnLocals(locals())

  def test_continue(self):

    def test_no_continue(m): pass

    def test_continue(m):
      m('begin')
      for i in range(10):
        m(i); continue; m(i)
      m('end')

    def test_continue_if(m):
      m('begin')
      for i in range(10):
        m(i)
        if False: continue
        m(i)
      m('middle')
      for j in range(10):
        m(i)
        if True: continue
        m(i)
      m('end')

    self.checkFctOnLocals(locals())

  def test_break(self):

    def test_no_break(m): pass

    def test_break(m):
      m('begin')
      for i in range(10):
        m(i); break; m(i)
      m('end')

    def test_break_if(m):
      m('begin')
      for i in range(10):
        m(i)
        if False: break
        m(i)
      m('middle')
      for j in range(10):
        m(i)
        if True: break
        m(i)
      m('end')

    self.checkFctOnLocals(locals())

if __name__ == "__main__":
  unittest.main()

#__EOF__

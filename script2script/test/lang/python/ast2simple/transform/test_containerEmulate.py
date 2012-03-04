#!/usr/bin/env python
import unittest, types, mock
import sys

from methodVisitUtil import MethodVisitUtil, callOnBoth, visitMethod
from script2script.lang.python.ast2simple.transform.containerEmulate import ContainerEmulate


class SimuContainer:
  """
  A mock container, englobing a mock object
  can be used as a real dictionary (and a list similar to range for slices)
  
  """

  def __init__(self, mockObject):
    """
    @param mockObject: the mock object to be called when something appends

    """
    self.m = mockObject
    self.c = {}

  def __getitem__(self, key):
    self.m('__getitem__', key)
    return self.c[key]

  def __setitem__(self, key, val):
    self.m('__setitem__', key, val)
    self.c[key] = val

  def __delitem__(self, key):
    self.m('__delitem__', key)
    del self.c[key]

  def __contains__(self, item):
    self.m('__contains__', item)
    return item in self.c

  def __getattr__(self, *args, **kargs): return getattr(self.m, *args, **kargs)



class TestContainerEmulate(unittest.TestCase):

  def dualTestFct(self, fctOri, *args):
    resOri, resVisited = self.callOnBoth(fctOri, ContainerEmulate(), *args)

    if resOri != resVisited:
      print 'testing %s' % fctOri.func_name
      print 'result : %s \n %s' % (resOri, resVisited) #TODO remove

    self.assertEqual(resOri, resVisited, "error on function %s" % fctOri.func_name)

  def checkFctOnLocals(self, locals_values, *args):
    for k, v in locals_values.iteritems():
      if k.startswith('test_') and isinstance(v, types.FunctionType):
        self.dualTestFct(v, *args)

  def callOnBoth(self, fctOri, visitor, *args):
    mOri = SimuContainer(mock.Mock())
    try:
      fctOri(mOri, *args) #test the original function
    except Exception as e:
      mOri(e)
    resOri = mOri.call_args_list

    mGoal = SimuContainer(mock.Mock())
    fctGoal = visitMethod(fctOri, visitor)
    try:
      fctGoal(mGoal, *args)
    except Exception as e:
      mGoal(e)
    resGoal = mGoal.call_args_list

    return (resOri, resGoal)


  #test different iterator in for
  def test_withDic(self):

    def test_simpleAssign(m):
      m('begin')
      m['a'] = 10
      m(m['a'])
      del m['a']
      m['b'] = 11
      m['b'] += 12
      m(m['b'])
      m('end')

    #def test_simpleAssign(m):
    #  m('begin')
    #  m['a'] = 'b'
    #  m['b'] = 'c'
    #  m( m[m['a']] )
    #  m('end')

    #def test_simpleAssign(m):
    #  m('begin')
    #  m.__setitem__('a', 10)
    #  m(m.__getitem__('a'))
    #  m.__delitem__('a')
    #  m('end')

    #def test_keyError(m):
    #  m('begin')
    #  try:
    #    m['a']
    #  except KeyError:
    #    m('key error')
    #  m('end')

    #def test_dic_errors(m): pass

    self.checkFctOnLocals(locals())

  def test_withList(self):
    #TODO

    self.checkFctOnLocals(locals())




if __name__ == "__main__":
  unittest.main()



#__EOF__

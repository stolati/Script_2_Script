#!/usr/bin/env python
import unittest, mock

from methodVisitUtil import AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.containerEmulate import ContainerEmulate

class MockNothing:
  def __getattr__(self, *args, **kargs): return self
  def __call__(self, *args, **kargs): return self


class SimuContainer:
  """
  A mock container, englobing a mock object
  can be used as a real dictionary (and a list similar to range for slices)
  
  """

  def __init__(self, container):
    self.m = mock.Mock()
    self.c = container

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

  def __getattr__(self, attr): return getattr(self.m, attr)



class TestContainerEmulate(AstTransformerTestClass):

  #test different iterator in for
  def test_withDic(self):

    def test_simple(m):
      m('begin')
      m['a'] = 10
      m(m['a'])
      del m['a']
      m['b'] = 11
      m['b'] += 12
      m(m['b'])
      m('b' in m)
      m(m['b'] in m)
      if 'a' in m: m('toto');
      m('b' not in m)
      m(m['b'] not in m)
      if 'a' not in m: m('toto');
      if m is m: m('titi')
      m('end')

    def test_Assign(m):
      m('begin')
      m['a'] = 'b'
      m['b'] = 'c'
      m( m[m['a']] )
      m('end')

    def test_simpleAssign(m):
      m('begin')
      m.__setitem__('a', 10)
      m(m.__getitem__('a'))
      m.__delitem__('a')
      m('end')

    def test_keyError(m):
      m('begin')
      try:
        m['a']
      except KeyError:
        m('key error')
      m('end')

    self.checkFctOnLocals(locals(), ContainerEmulate(), lambda : SimuContainer(dict()) )

  def test_withList(self):

    def test_simpleAssign(m):
      m('begin')
      m[2] = 10
      m(m[2])
      del m[2]
      m[2] = 11
      m[2] += 12
      m(m[2])
      m(12 in m)
      m(12 not in m)
      m(13 in m)
      m(13 not in m)
      m('end')

    self.checkFctOnLocals(locals(), ContainerEmulate(), lambda: SimuContainer(range(10)) )

  def test_slices(self):

    def test_slice_getattr(m):
      m('begin')
      v = range(10)
      m( v[3:] )
      m( v[3:8] )
      m( v[3:8:2] )
      m( v[:8:2] )
      m( v[3::2] )
      m( v[3::] )
      m( v[3:8:] )
      m( v[::2] )
      m( v[:8:] )
      m( v[::] )
      m('end')

    def test_slice_setattr(m):
      m('begin')
      v = range(10); v[3:] = range(5); m(v)
      v = range(10); v[3:8] = range(5); m(v)
      v = range(10); v[3:8:2] = range(3); m(v)
      v = range(10); v[:8:2] = range(4); m(v)
      v = range(10); v[3::2] = range(4); m(v)
      v = range(10); v[3::] = range(4); m(v)
      v = range(10); v[3:8:] = range(5); m(v)
      v = range(10); v[::2] = range(5); m(v)
      v = range(10); v[:8:] = range(5); m(v)
      v = range(10); v[::] = range(5); m(v)
      m('end')

    def test_slice_delattr(m):
      v = range(10); del v[3:] ; m(v)
      v = range(10); del v[3:8] ; m(v)
      v = range(10); del v[3:8:2] ; m(v)
      v = range(10); del v[:8:2] ; m(v)
      v = range(10); del v[3::2] ; m(v)
      v = range(10); del v[3::] ; m(v)
      v = range(10); del v[3:8:] ; m(v)
      v = range(10); del v[::2] ; m(v)
      v = range(10); del v[:8:] ; m(v)
      v = range(10); del v[::] ; m(v)
      m('end')

    self.checkFctOnLocals(locals(), ContainerEmulate(), mock.Mock)

  def test_multiSlices(self):

    def test_extslice(m):
      m('begin')
      m[3:, ...]
      m[3:, ..., 3:5:8, ...] = 10
      m('end')

    self.checkFctOnLocals(locals(), ContainerEmulate(), lambda: SimuContainer(MockNothing()))

  def test_augassign(self):

    def test_augassign_digit(m):
      m('begin')
      m['a'] = 4
      m(m['a'])
      m['a'] += 5
      m(m['a'])

    def test_augassign_list(m):
      m('begin')
      m['a'] = range(10)
      m(m['a'])
      m['a'] += range(5)
      m(m['a'])

    self.checkFctOnLocals(locals(), ContainerEmulate(), lambda: SimuContainer({}))


if __name__ == "__main__":
  unittest.main()



#__EOF__

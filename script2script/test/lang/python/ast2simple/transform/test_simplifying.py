#!/usr/bin/env python
import unittest, types, mock
import sys

from methodVisitUtil import MethodVisitUtil, callOnBoth, AstTransformerTestClass
from script2script.lang.python.ast2simple.transform.simplifying import Simplifying

#helper function return the first elements, and have *args for nothing
def ret(r, *args): return r



class TestSimplifier(AstTransformerTestClass):

  #def test_boolOp(self):
  #
  #  def test_simpleBoolOp(m):
  #    return ret(True, m('toto')) and ret(False, m('titi'))
  #
  #  self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_binOp(self):

    def test_simpleBinOp(m):
      def ret(r, *args): return r
      for i in range(10):
        for j in range(10):
          m( ret(i, m('left', i)) + ret(j, m('right', j)) ) #Add
          m( ret(i, m('left', i)) - ret(j, m('right', j)) ) #Sub
          m( ret(i, m('left', i)) * ret(j, m('right', j)) ) #Mult
          try:
            m( ret(i, m('left', i)) / ret(j, m('right', j)) ) #Div
          except ZeroDivisionError: m('zeroDivErr')
          try:
            m( ret(i, m('left', i)) % ret(j, m('right', j)) ) #Mod
          except ZeroDivisionError: m('zeroDivErr')
          m( ret(i, m('left', i)) ** ret(j, m('right', j)) ) #Pow
          m( ret(i, m('left', i)) << ret(j, m('right', j)) ) #LShift
          m( ret(i, m('left', i)) >> ret(j, m('right', j)) ) #RShift
          m( ret(i, m('left', i)) | ret(j, m('right', j)) ) #BitOr
          m( ret(i, m('left', i)) ^ ret(j, m('right', j)) ) #BitXor
          m( ret(i, m('left', i)) & ret(j, m('right', j)) ) #BitAnd
          try:
            m( ret(i, m('left', i)) // ret(j, m('right', j)) ) #FloorDiv
          except ZeroDivisionError:  m('zeroDivErr')

    def test_ComplexBinOp(m):
      def ret(r, *args): return r
      for i in range(10):
        for j in range(10):
          m( ret(i, m('01', i)) *  ret(j, m('02', j)) +  ret(i, m('03', i)) -  ret(j, m('04', j)) )
          m( ret(i, m('01', i)) ** ret(j, m('02', j)) << ret(i, m('03', i)) >> ret(j, m('04', j)) )
          m( ret(i, m('01', i)) ^  ret(j, m('02', j)) |  ret(i, m('03', i)) &  ret(j, m('04', j)) )

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_UnaryOp(self):

    def test_simpleUnaryOp(m):
      def ret(r, *args): return r
      for i in range(10):
        for j in range(10):
          m( ret(i, m('op')) )
          m( not ret(i, m('op'))) #Not
          m( + ret(i, m('op'))) #UAdd
          m( - ret(i, m('op'))) #USub
          m( ~ ret(i, m('op'))) #Invert

    def test_complexUnaryOp(m):
      def ret(r, *args): return r
      for i in range(10):
        for j in range(10):
          m( ret(i, m('op')) )
          m( - (not ret(i, m('op')))) #Not
          m( ~ (+ ret(i, m('op')))) #UAdd
          m( not (- ret(i, m('op')))) #USub
          m( - (~ ret(i, m('op')))) #Invert

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_Dict(self):

    def test_simpleDict(m):
      def ret(r, *args): m(r); return r
      d = {
          ret('a'): ret(1),
          ret('b'): ret(2),
          ret('c'): ret(3),
          ret('d'): ret(4),
          ret('e'): ret(5),
          ret('f'): ret(6),
      }
      m(d)

    def test_complexDictComp(m):
      def ret(r, *args): m(r); return r
      d = {
          ret('a'): {
            ret('aa'): ret(1),
            ret('ab'): ret(2),
            ret('ac'): ret(3),
          },
          ret('b'): {
            ret('ba'): ret(4),
            ret('bb'): ret(5),
            ret('bc'): ret(6),
          },
          ret('c'): {
            ret('ca'): ret(7),
            ret('cb'): ret(8),
            ret('cc'): ret(9),
          },
          ret('d'): {
            ret('da'): ret(10),
            ret('db'): ret(11),
            ret('dc'): ret(12),
          },
          ret('e'): {
            ret('ea'): ret(13),
            ret('eb'): ret(14),
            ret('ec'): ret(15),
          },
          ret('f'): {
            ret('fa'): ret(16),
            ret('fb'): ret(17),
            ret('fc'): ret(18),
          },
      }
      m(d)

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_Set(self):

    def test_simpleSet(m):
      def ret(r, *args): m(r); return r
      d = {
          ret('a'), ret(1),
          ret('b'), ret(2),
          ret('c'), ret(3),
          ret('d'), ret(4),
          ret('e'), ret(5),
          ret('f'), ret(6),
      }
      m(d)

    def test_complexSet(m):
      def ret(r, *args): m(r); return r
      d = {
          ret('a'), (
            ret('aa'), ret(1),
            ret('ab'), ret(2),
            ret('ac'), ret(3),
          ),
          ret('b'), (
            ret('ba'), ret(4),
            ret('bb'), ret(5),
            ret('bc'), ret(6),
          ),
          ret('c'), (
            ret('ca'), ret(7),
            ret('cb'), ret(8),
            ret('cc'), ret(9),
          ),
          ret('d'), (
            ret('da'), ret(10),
            ret('db'), ret(11),
            ret('dc'), ret(12),
          ),
          ret('e'), (
            ret('ea'), ret(13),
            ret('eb'), ret(14),
            ret('ec'), ret(15),
          ),
          ret('f'), (
            ret('fa'), ret(16),
            ret('fb'), ret(17),
            ret('fc'), ret(18),
          ),
      }
      m(d)

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_Tulpe(self):

    def test_simpleTuple(m):
      def ret(r, *args): m(r); return r
      d = (
          ret('a'), ret(1),
          ret('b'), ret(2),
          ret('c'), ret(3),
          ret('d'), ret(4),
          ret('e'), ret(5),
          ret('f'), ret(6),
      )
      m(d)

    def test_complexTuple(m):
      def ret(r, *args): m(r); return r
      d = (
          ret('a'), (
            ret('aa'), ret(1),
            ret('ab'), ret(2),
            ret('ac'), ret(3),
          ),
          ret('b'), (
            ret('ba'), ret(4),
            ret('bb'), ret(5),
            ret('bc'), ret(6),
          ),
          ret('c'), (
            ret('ca'), ret(7),
            ret('cb'), ret(8),
            ret('cc'), ret(9),
          ),
          ret('d'), (
            ret('da'), ret(10),
            ret('db'), ret(11),
            ret('dc'), ret(12),
          ),
          ret('e'), (
            ret('ea'), ret(13),
            ret('eb'), ret(14),
            ret('ec'), ret(15),
          ),
          ret('f'), (
            ret('fa'), ret(16),
            ret('fb'), ret(17),
            ret('fc'), ret(18),
          ),
      )
      m(d)

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_List(self):

    def test_simpleList(m):
      def ret(r, *args): m(r); return r
      d = [
          ret('a'), ret(1),
          ret('b'), ret(2),
          ret('c'), ret(3),
          ret('d'), ret(4),
          ret('e'), ret(5),
          ret('f'), ret(6),
      ]
      m(d)

    def test_complexTuple(m):
      def ret(r, *args): m(r); return r
      d = [
          ret('a'), [
            ret('aa'), ret(1),
            ret('ab'), ret(2),
            ret('ac'), ret(3),
          ],
          ret('b'), [
            ret('ba'), ret(4),
            ret('bb'), ret(5),
            ret('bc'), ret(6),
          ],
          ret('c'), [
            ret('ca'), ret(7),
            ret('cb'), ret(8),
            ret('cc'), ret(9),
          ],
          ret('d'), [
            ret('da'), ret(10),
            ret('db'), ret(11),
            ret('dc'), ret(12),
          ],
          ret('e'), [
            ret('ea'), ret(13),
            ret('eb'), ret(14),
            ret('ec'), ret(15),
          ],
          ret('f'), [
            ret('fa'), ret(16),
            ret('fb'), ret(17),
            ret('fc'), ret(18),
          ],
      ]
      m(d)


    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_Repr(self):

    def test_simpleRepr(m):
      def ret(r): m(r); return r
      class Toto:
        def __str__(self): return '01'
        def __repr__(self): return '02'

      m( `ret(3)` )
      m( `ret((10, 11, 12))` )
      m( `ret([10, 11, 12])` )
      m( `ret({10, 11, 12})` )
      m( `Toto()` )

    def test_complexRepr(m):
      def ret(r): m(r); return r
      class Toto:
        def __str__(self): return '01'
        def __repr__(self): return '02'

      m( ``ret(3)`` )
      m( ``ret((10, 11, 12))`` )
      m( ``ret([10, 11, 12])`` )
      m( ``ret({10, 11, 12})`` )
      m( ``Toto()`` )

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_Call(self):

    def test_simpleCall(m):
      def ret(r): m(r); return r
      def calonm(): m('calOnM'); return m
      d = {'1':2, '3':4, '5':6}
      calonm()(ret('b'), toto=ret('a'), tutu=ret('c'), a=ret('d'), z=ret('e'), aa=ret('f'), *ret(range(10)), **ret(d))

    def test_complexCall(m):
      def retall(*args, **kargs): m(args, kargs); return (args, kargs)
      def calonm(): m('calOnM'); return m
      d = {'1':2, '3':4, '5':6}
      calonm()(retall(retall('b')))
      calonm()( *retall(retall(*range(10), **{'toto':1})))


    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_Cmp(self):

    def test_simpleCmp(m):
      def ret(r): m(r); return r
      for i in range(10):
        for j in range(10):
          m(ret(i) == ret(j))
          m(ret(i) != ret(j))
          m(ret(i) < ret(j))
          m(ret(i) <= ret(j))
          m(ret(i) > ret(j))
          m(ret(i) >= ret(j))
          m(ret(i) is ret(j))
          m(ret(i) is not ret(j))
          m(ret(i) in ret(range(j)))
          m(ret(i) not in ret(range(j)))

    def test_complexCmp(m):
      def ret(r): m(r); return r
      for i in range(5):
        for j in range(5):
          for k in range(5):
            for l in range(5):
              m(ret(i) == ret(j) == ret(k) == ret(l))
              m(ret(i) != ret(j) != ret(k) != ret(l))
              m(ret(i) < ret(j) < ret(k) < ret(l))
              m(ret(i) <= ret(j) <= ret(k) <= ret(l))
              m(ret(i) > ret(j) > ret(k) > ret(l))
              m(ret(i) >= ret(j) >= ret(k) >= ret(l))
              m(ret(i) is ret(j) is ret(k) is ret(l))
              m(ret(i) is not ret(j) is not ret(k) is not ret(l))

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_Call(self):

    def test_complexCall(m):
      def retall(*args, **kargs): m(args, kargs); return (args, kargs)
      def calonm(): m('calOnM'); return m
      d = {'1':2, '3':4, '5':6}
      calonm()(retall(retall('b')))
      calonm()( *retall(retall(*range(10), **{'toto':1})))

    def test_SuiteCall(m):
      def retall(*args, **kargs): m(args, kargs); return (args, kargs)
      def calonm(): m('calOnM'); return m
      d = {'1':2, '3':4, '5':6}
      calonm()(retall(retall('b')))
      calonm()( *retall(retall(*range(10), **{'toto':1})))

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_While(self):

    def test_minimunWhile(m):
      def ret(r): m(r); return r
      a, b = 0, 10
      while ret(a) < ret(b):
        m('begin')
        a += 1
        m('end')

    def test_testWithList(m):
      def ret(r): m(r); return r
      a = list(range(10))
      while ret(a):
        m('begin')
        m(a.pop(0))
        m('end')

    def test_testListLen(m):
      def ret(r): m(r); return r
      l = range(10)
      while len(ret(l)) < ret(len([1, 2, 3])):
          m('begin')
          m(l.pop(0))
          m('end')

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_BoolOp(self):

    def test_simpleBoolOp(m):
      def ret(r): m(r); return r
      for i in (True, False):
        for j in (True, False):
          m(ret(i) and ret(j))
          m(ret(i) or ret(j))

    def test_complexBoolOp(m):
      def ret(r): m(r); return r
      for i in (True, False):
        for j in (True, False):
          for k in (True, False):
            for l in (True, False):
              m(ret(i) and ret(j) and ret(k) and ret(l))
              m(ret(i) or ret(j) or ret(k) or ret(l))


    def test_complexValues(m):
      def ret(r): m(r); return r
      for i in (True, False, [], [1], (), (1, 2), 0, 1):
        for j in (True, False, [], [1], (), (1, 2), 0, 1):
          for k in (True, False, [], [1], (), (1, 2), 0, 1):
            for l in (True, False, [], [1], (), (1, 2), 0, 1):
              m(ret(i) and ret(j) and ret(k) and ret(l))
              m(ret(i) or ret(j) or ret(k) or ret(l))

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_IfExpr(self):

    def test_simpleIfExpr(m):
      def ret(r): m(r); return r
      for i in (0, 1, True, False):
        for j in (0, 1, True, False):
          for k in (0, 1, True, False):
            m(ret(i) if ret(j) else ret(k))

    def test_complexIfExpr(m):
      def ret(r): m(r); return r
      for i in (0, 1, True, False):
        for j in (0, 1, True, False):
          for k in (0, 1, True, False):
            for l in (0, 1, True, False):
              for n in (0, 1, True, False):
                m(ret(i) if ret(j) else ret(k) if ret(l) else ret(n))

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_lambda(self):

    def test_simpleLambda(m):
      def ret(r): m(r); return r
      n = lambda r: m(ret(r))
      n('toto')
      o = lambda r: ret(r)
      n( o('titi') )

    def test_complexLambda(m):
      def ret(r): m(r); return r
      n = lambda x : lambda y: ret(ret(x)*ret(y))
      o = lambda a : lambda b: ret(a < b)

      for i in range(5):
        for j in range(5):
          m(n(i)(j))
          m(o(i)(j))

    def test_vithVariables(m):
      def ret(r): m(r); return r
      for i in range(5):
        for j in range(5):
          o = lambda : i * j
          m(o())

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)

  def test_ListComp(self):

    def test_simple(m):
      def ret(r): m(r); return r

      m( [ret( (e, e) ) for e in ret(range(10))] )
      m( [ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5))] )
      m( [ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) ])
      m( [ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) if ret(ret(a) > 7)])

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_SetComp(self):

    def test_simple(m):
      def ret(r): m(r); return r

      m( {ret( (e, e) ) for e in ret(range(10))} )
      m( {ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5))} )
      m( {ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) })
      m( {ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) if ret(ret(a) > 7)})

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_SetDict(self):

    def test_simple(m):
      def ret(r): m(r); return r
      m( {ret(e):ret(e) for e in ret(range(10))} )
      m( {ret(a):ret(b) for a in ret(range(10)) for b in ret(range(5))} )
      m( {ret(a):ret(b) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) } )
      m( {ret(a):ret(b) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) if ret(ret(a) > 7)} )

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_GeneratorComp(self):

    def test_simple(m):
      def ret(r): m(r); return r

      m( list( (ret( (e, e) ) for e in ret(range(10))) ) )
      m( list( (ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5))) ) )
      m( list( (ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) ) ) )
      m( list( (ret( (a, b) ) for a in ret(range(10)) for b in ret(range(5)) if ret(ret(b) < 3) if ret(ret(a) > 7))) )

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


  def test_Attribute(self):

    def test_simple(m):
      def ret(r): m(r); return r
      class Foo(object): pass
      f = Foo()
      f.titi = 10
      ret(f.titi)
      f.tutu, f.toto = f, f
      ret(f.tutu.toto.titi)
      ret(f.tutu.toto.toto.tutu.toto.tutu.toto.tutu.tutu.titi)

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


if __name__ == "__main__":
  unittest.main()


#__EOF__

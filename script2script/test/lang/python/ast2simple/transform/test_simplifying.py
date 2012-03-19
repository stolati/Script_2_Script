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
      def ret(r, *args): m(r); return r
      class Toto:
        def __str__(self): return '01'
        def __repr__(self): return '02'

      m( `ret(3)` )
      m( `ret((10, 11, 12))` )
      m( `ret([10, 11, 12])` )
      m( `ret({10, 11, 12})` )
      m( `Toto()` )

    self.checkFctOnLocals(locals(), Simplifying(), mock.Mock)


if __name__ == "__main__":
  unittest.main()



#__EOF__

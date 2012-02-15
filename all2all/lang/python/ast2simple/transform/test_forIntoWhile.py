#!/usr/bin/env python
import unittest
from forIntoWhile import ForIntoWhile as Fiw
from methodVisitUtil import *
import mock


def simpleFor(fct, container):
  for e in container:
    fct(e)



def iforWithElse(res1, res2):
  for i in range(10):
    return res1
  else:
    return res2

def forWithElse(res1, res2):
  print 'ok'

#print parser.compileast

class TestForIntoWhile(unittest.TestCase):

  def forWithElse(res1, res2):
    print 'ok'

  def forSimple(l, res1, res2): pass
  def forContinue(): pass
  def forBreak(): pass

  # ast.parse(code, filename)
  #a.visitWith(Parse.ForIntoWhile())


  def test_simpleFor(self):
    m = mock.Mock()
    fct = simpleFor
    fct(m, range(10))
    assert m.call_args_list == [mock.call(n) for n in range(10)]

    m = mock.Mock()
    fct = visitMethod(fct) #, Fiw())
    fct(m, range(10))
    assert m.call_args_list == [mock.call(n) for n in range(10)]


if __name__ == "__main__":
  unittest.main()



#__EOF__

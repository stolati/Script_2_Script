#!/usr/bin/env python
import unittest, ast

from script2script.lang.python.ast2simple.transform.nodeTransformer import *

class TestVariableGenerator(unittest.TestCase):

  def test_uniticy(self):
    vgl = [VariableGenerator() for i in range(10)]

    res = []
    for vg in vgl:
      for i in range(10):
        valName = vg.geneVariable()
        self.assertNotIn(valName, res)
        res.append(valName)
    self.assertEqual(len(res), 100)

  def test_uniticy_withNames(self):
    vgl = [VariableGenerator() for i in range(10)]

    res = []
    for vg in vgl:
      for i in range(10):
        valName = vg.geneVariable('toto')
        self.assertNotIn(valName, res)
        res.append(valName)
    self.assertEqual(len(res), 100)

  def test_uniticy_withClass(self):
    vgl = [type('gene%d'%i, (VariableGenerator,), {})() for i in range(10)]

    res = []
    for vg in vgl:
      for i in range(10):
        valName = vg.geneVariable('toto')
        self.assertNotIn(valName, res)
        res.append(valName)
    self.assertEqual(len(res), 100)


class TestNodeVisitor(unittest.TestCase):

  def test_withIterNodes(self):
    nodes = ast.If(
        ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [
          ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False),
        ],
        [],
    )
    waitedRes = 'If Call Name Load List Load Print Call Name Load List Load'.split(' ')

    iterRes = [n.__class__.__name__ for n in iter_nodes(nodes)]
    self.assertEquals(waitedRes, iterRes)





#class TestTransformer(unittest.TestCase): pass














if __name__ == "__main__":
  unittest.main()



#__EOF__

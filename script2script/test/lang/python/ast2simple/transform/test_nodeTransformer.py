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


class TestNodeTransformer(unittest.TestCase):

  def getNodeTest(self):
    return ast.If(
        ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [
          ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False),
        ],
        [],
    )

  def testChange(self):
    res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [ ast.Print(None, ast.Call(ast.Name('titi', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

    class TotoInTiti(NodeTransformer):
      def visit_Name(self, node):
        return ast.Name('titi', node.ctx) if node.id == 'toto' else node

    bases = node2json(res)
    transformed = node2json(TotoInTiti().visit(self.getNodeTest()))
    self.assertEqual(bases, transformed)


  def testReturnList(self):
    res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [ ast.Print(None, ast.Name('tralala', ast.Load()), False), ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

    class PrintDouble(NodeTransformer):
      def visit_Print(self, node):
        return [ ast.Print(None, ast.Name('tralala', ast.Load()), False), self.generic_visit(node), ]

    bases =  node2json(res)
    transformed = node2json(PrintDouble().visit(self.getNodeTest()))
    self.assertEqual(bases, transformed)

  def testReturnListImbricated(self):
    res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [ ast.Print(None, ast.Name('tralala', ast.Load()), False), ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

    class PrintDouble(NodeTransformer):
      def visit_Print(self, node):
        return [[ [[ast.Print(None, ast.Name('tralala', ast.Load()), False)]], self.generic_visit(node), ]]

    bases =  node2json(res)
    transformed = node2json(PrintDouble().visit(self.getNodeTest()))
    self.assertEqual(bases, transformed)


class TestNodeTransformerAddedStmt(unittest.TestCase):

  def getNodeTest(self):
    return ast.If(
        ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [
          ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False),
        ],
        [],
    )

  def testChange(self):
    res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [ ast.Print(None, ast.Call(ast.Name('titi', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

    class TotoInTiti(NodeTransformerAddedStmt):
      def visit_Name(self, node):
        return ast.Name('titi', node.ctx) if node.id == 'toto' else node

    bases = node2json(res)
    transformed = node2json(TotoInTiti().visit(self.getNodeTest()))
    self.assertEqual(bases, transformed)


  def testReturnList(self):
    res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [ ast.Print(None, ast.Name('tralala', ast.Load()), False), ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

    class PrintDouble(NodeTransformerAddedStmt):
      def visit_Print(self, node):
        return [ ast.Print(None, ast.Name('tralala', ast.Load()), False), self.generic_visit(node), ]

    bases =  node2json(res)
    transformed = node2json(PrintDouble().visit(self.getNodeTest()))
    self.assertEqual(bases, transformed)

  def testReturnListImbricated(self):
    res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
        [ ast.Print(None, ast.Name('tralala', ast.Load()), False), ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

    class PrintDouble(NodeTransformerAddedStmt):
      def visit_Print(self, node):
        return [[ [[ast.Print(None, ast.Name('tralala', ast.Load()), False)]], self.generic_visit(node), ]]

    bases =  node2json(res)
    transformed = node2json(PrintDouble().visit(self.getNodeTest()))
    self.assertEqual(bases, transformed)


    def testAddedElement(self):
      res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
          [ ast.Print(None, ast.Name('tralala', ast.Load()), False), ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

      class PrintDouble(NodeTransformerAddedStmt):
        def visit_Print(self, node):
          self.statementToAdd( ast.Print(None, ast.Name('tralala', ast.Load()), False) )
          return self.generic_visit(node)

      bases =  node2json(res)
      transformed = node2json(PrintDouble().visit(self.getNodeTest()))
      self.assertEqual(bases, transformed)


    def testAddedElementInside(self):
      res = ast.If( ast.Call(ast.Name('tutu', ast.Load()), [ast.List([], ast.Load())], [], None, None),
          [ ast.Print(None, ast.Name('tralala', ast.Load()), False), ast.Print(None, ast.Call(ast.Name('toto', ast.Load()), [ast.List([], ast.Load())], [], None, None), False), ], [],)

      class PrintDouble(NodeTransformerAddedStmt):
        def visit_Name(self, node):
          if node.id == 'toto':
            self.statementToAdd( ast.Print(None, ast.Name('tralala', ast.Load()), False) )
          return node

      bases =  node2json(res)
      transformed = node2json(PrintDouble().visit(self.getNodeTest()))
      self.assertEqual(bases, transformed)


if __name__ == "__main__":
  unittest.main()



#__EOF__

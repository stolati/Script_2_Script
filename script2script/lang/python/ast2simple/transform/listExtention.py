#!/usr/bin/env python

from ast import *
import nodeTransformer

#TODO do with no-empty list/tuple/dict


class ListExtention(nodeTransformer.NodeTransformerAddedStmt):

  def visit_List(self, node):
    if not isinstance(node.ctx, Load): return self.generic_visit(node)
    if len(node.elts) == 0: return Call( Name('list', Load()), [], [], None, None)

    varName = self.geneVariable('list')
    #varName = list()
    before = [Assign([Name(varName, Store())], Call(Name('list', Load()), [], [], None, None))]
    for e in node.elts:
      before += [
        #varName.append(e)
        Expr(Call(
          Attribute(Name(varName, Load()), 'append', Load()),
          [self.visit(e)], [], None, None))
      ]

    self.statementsToAdd( before)
    return Name(varName, Load())


class TupleExtention(nodeTransformer.NodeTransformerAddedStmt):

  def visit_Tuple(self, node):
    if not isinstance(node.ctx, Load): return self.generic_visit(node)
    if len(node.elts) == 0: return Call( Name('tuple', Load()), [], [], None, None)

    varName = self.geneVariable('tuple')
    #varName = tuple()
    before = [Assign([Name(varName, Store())], Call(Name('list', Load()), [], [], None, None))]
    for e in node.elts:
      #varName.append(e)
      before += [
        Expr(Call(
          Attribute(Name(varName, Load()), 'append', Load()),
          [self.visit(e)], [], None, None))
      ]

    self.statementsToAdd( before)
    return Call(Name('tuple', Load()), [Name(varName, Load())], [], None, None)


class DictExtention(nodeTransformer.NodeTransformerAddedStmt):

  def visit_Dict(self, node):
    if len(node.keys) == 0: return Call(Name('dict', Load()), [], [], None, None)

    varName = self.geneVariable('dict')
    #varName = dict()
    before = [Assign([Name(varName, Store())], Call(Name('dict', Load()), [], [], None, None))]
    for i in range(len(node.keys)):
      key, val = node.keys[i], node.values[i]
      before += [
        #varName.__setitem__(key, val)
        Expr(Call(
          Attribute(Name(varName, Load()), '__setitem__', Load()),
          [self.visit(key), self.visit(val)], [], None, None))
      ]

    self.statementsToAdd( before)
    return Name(varName, Load())









#__EOF__

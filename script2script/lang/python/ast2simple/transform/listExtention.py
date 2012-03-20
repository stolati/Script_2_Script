#!/usr/bin/env python

from ast import *
import nodeTransformer

#TODO remove thoses, not needed anymore

class ListExtention(nodeTransformer.NodeTransformerAddedStmt):

  def visit_List(self, node):
    if not isinstance(node.ctx, Load): return self.generic_visit(node)
    if len(node.elts) == 0: return Call( Name('list', Load()), [], [], None, None)

    varName = self.genVar('list')
    #varName = list()
    before = [varName.assign(Call(Name('list', Load()), [], [], None, None))]
    for e in node.elts:
      before += [
        #varName.append(e)
        Expr(Call(
          varName.load('append'),
          [self.visit(e)], [], None, None))
      ]

    self.statementsToAdd( before)
    return varName.load()


class TupleExtention(nodeTransformer.NodeTransformerAddedStmt):

  def visit_Tuple(self, node):
    if not isinstance(node.ctx, Load): return self.generic_visit(node)
    if len(node.elts) == 0: return Call( Name('tuple', Load()), [], [], None, None)

    varName = self.genVar('tuple')
    #varName = tuple()
    before = [varName.assign(Call(Name('list', Load()), [], [], None, None))]
    for e in node.elts:
      #varName.append(e)
      before += [
        Expr(Call(
          varName.load('append'),
          [self.visit(e)], [], None, None))
      ]

    self.statementsToAdd( before)
    return Call(Name('tuple', Load()), [varName.load()], [], None, None)


class DictExtention(nodeTransformer.NodeTransformerAddedStmt):

  def visit_Dict(self, node):
    if len(node.keys) == 0: return Call(Name('dict', Load()), [], [], None, None)

    varName = self.genVar('dict')
    #varName = dict()
    before = [varName.assign(Call(Name('dict', Load()), [], [], None, None))]
    for i in range(len(node.keys)):
      key, val = node.keys[i], node.values[i]
      before += [
        #varName.__setitem__(key, val)
        Expr(Call(
          varName.load('__setitem__'),
          [self.visit(key), self.visit(val)], [], None, None))
      ]

    self.statementsToAdd( before)
    return varName.load()









#__EOF__

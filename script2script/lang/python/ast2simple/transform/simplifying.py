#!/usr/bin/env python
import ast
from ast import *
from nodeTransformer import *

#TODO take care of the while command
#     it should copy the added command before and after


class Simplifying(NodeTransformerAddedStmt):
  #def statementToAdd(self, stm): self.bodyToAddBefore[-1].append(stm)
  #def statementsToAdd(self, stms): self.bodyToAddBefore[-1] += stms

  #def visit_BoolOp(self, node): pass #TODO very specials
  def visit_BinOp(self, node):
    # BitAnd | FloorDiv

    varLeft = self.genVar('left_operand')
    varRight = self.genVar('rigth_operand')
    varExpr = self.genVar('resultBinOp')

    #keep this order
    exprLeft = self.visit(node.left)
    exprRight = self.visit(node.right)

    self.statementsToAdd([
        #varLeft = exprLeft
        varLeft.assign(exprLeft),
        #varRight = exprRight
        varRight.assign(exprRight),
        #varExpr = varLeft + varRight
        varExpr.assign(
          BinOp( varLeft.load(), node.op , varRight.load() ),
        )
    ])

    return varExpr.load()


  def visit_UnaryOp(self, node):
    varOp = self.genVar('resultUnaryOp')
    exprOp = self.visit(node.operand)

    self.statementsToAdd([
      #varOp = - exprOp
      varOp.assign( UnaryOp(node.op, exprOp) ),
    ])

    return varOp.load()



  def visit_Dict(self, node):
    varDict = self.genVar('dict')
    self.statementToAdd(
      #varDict = dict()
      varDict.assign( Call(Name('dict', Load()), [], [], None, None) ),
    )

    for k, v in zip(node.keys, node.values):
      varKey = self.genVar('key')
      varVal = self.genVar('val')

      exprVal = self.visit(v)
      exprKey = self.visit(k)

      self.statementsToAdd( [
          #varVal = exprVal
          varVal.assign(exprVal),
          #varKey = exprKey
          varKey.assign(exprKey),
          #varDict.__setitem__(varKey, varVal)
          Expr(
            Call(
              varDict.load('__setitem__'),
              [varKey.load(), varVal.load()], [], None, None
            )
          ),
      ])

    return varDict.load()


  def visit_Set(self, node):
    varSet = self.genVar('set')
    self.statementToAdd(
      #varSet = set()
      varSet.assign( Call(Name('set', Load()), [], [], None, None) ),
    )

    for e in node.elts:
      varElt = self.genVar('elt')

      exprElt = self.visit(e)

      self.statementsToAdd([
        #varElt = exprElt
        varElt.assign(exprElt),
        #varSet.add( exprElt )
        Expr(
          Call(
            varSet.load('add'),
            [varElt.load()], [], None, None
          )
        ),
      ])

    return varSet.load()


  def visit_Tuple(self, node):

    nameLoad = self.visit_List(node) #duck typing powaaaa

    #because we used a list to tmp puts things in, go back to tuple
    varTuple = self.genVar('tuple')
    self.statementToAdd(
      varTuple.assign( Call(Name('tuple', Load()), [nameLoad], [], None, None) ),
    )

    return varTuple.load()


  def visit_List(self, node):
    varList = self.genVar('list')
    self.statementToAdd(
      #varList = tuple()
      varList.assign( Call(Name('list', Load()), [], [], None, None) ),
    )

    for e in node.elts:
      varElt = self.genVar('elt')

      exprElt = self.visit(e)

      self.statementsToAdd([
        #varElt = exprElt
        varElt.assign(exprElt),
        #varList.add( exprElt )
        Expr(
          Call(
            varList.load('append'),
            [varElt.load()], [], None, None
          )
        ),
      ])

    return varList.load()

  def visit_Repr(self, node):
    varRepr = self.genVar('repr')
    varValue = self.genVar('value')

    exprValue = self.visit(node.value)

    self.statementsToAdd([
      #varValue = exprValue
      varValue.assign(exprValue),
      #varRepr = repr(varValue)
      varRepr.assign( Call(Name('repr', Load()), [varValue.load()], [], None, None ) ),
    ])

    return varRepr.load()


  def visit_Call(self, node):
    funcVar = self.genVar('func')
    funcExpr = self.visit(node.func)
    self.statementToAdd(funcVar.assign(funcExpr))

    argsRes = []
    for n, arg in enumerate(node.args):
      aVar = self.genVar('arg_%s'%n)
      aExpr = self.visit(arg)
      self.statementToAdd( aVar.assign(aExpr) )
      argsRes.append(aVar.load())

    kargsRes = []
    for keyword in node.keywords:
      arg, value = keyword.arg, keyword.value
      var = self.genVar('kargs_%s' % arg)
      expr = self.visit(value)
      self.statementToAdd( var.assign(expr) )

      keyword.value = var.load()
      kargsRes.append( keyword )

    starargsRes = None
    if node.starargs:
      starArgsVar = self.genVar('starargs')
      starArgsExpr = self.visit(node.starargs)
      self.statementToAdd( starArgsVar.assign(starArgsExpr))
      starargsRes = starArgsVar.load()

    kWargsRes = None
    if node.kwargs:
      kWargsVar = self.genVar('kwargs')
      kWargsExpr = self.visit(node.kwargs)
      self.statementToAdd( kWargsVar.assign(kWargsExpr))
      kWargsRes = kWargsVar.load()

    return Call(funcVar.load(), argsRes, kargsRes, starargsRes, kWargsRes)


  #def visit_Compare(self, node):
  #  #leftVar = self.genVar('leftMost')
  #  #leftExpr = self.visit(node.left)

  #  #for n, (op, comparator) in zip(node.ops, node.comparators)



  #  # Compare(expr left, cmpop* ops, expr* comparators)








    return self.generic_visit(node)

    #left
    #cmpop * ops
    #expr * comparators

# - need more block intelligence
# BoolOp(boolop op, expr* values)
# IfExp(expr test, expr body, expr orelse)
# Lambda(arguments args, expr body)
# ListComp(expr elt, comprehension* generators)
# SetComp(expr elt, comprehension* generators)
# DictComp(expr key, expr value, comprehension* generators)
# GeneratorExp(expr elt, comprehension* generators)
#
# - can be done easely
# Compare(expr left, cmpop* ops, expr* comparators)
# Call(expr func, expr* args, keyword* keywords, expr? starargs, expr? kwargs)
#
#
#- the grammar constrains where yield expressions can occur
#- Do not do it now, wait way more
# Yield(expr? value)
#
#
#- the following expression can appear in assignment context
# Attribute(expr value, identifier attr, expr_context ctx)
# Subscript(expr value, slice slice, expr_context ctx)
#
# ---- content -----
#
#	expr_context = Load | Store | Del | AugLoad | AugStore | Param
#
#	slice = Ellipsis | Slice(expr? lower, expr? upper, expr? step) 
#	      | ExtSlice(slice* dims) 
#	      | Index(expr value) 
#
#	boolop = And | Or 
#
#
#	cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn
#
#	comprehension = (expr target, expr iter, expr* ifs)
#
#	arguments = (expr* args, identifier? vararg, 
#		     identifier? kwarg, expr* defaults)
#
#        -- keyword arguments supplied to call
#        keyword = (identifier arg, expr value)
#
#        -- import name with optional 'as' alias.
#        alias = (identifier name, identifier? asname)
#__EOF__

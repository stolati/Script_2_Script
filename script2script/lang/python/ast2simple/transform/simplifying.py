#!/usr/bin/env python
import ast
from ast import *
from nodeTransformer import *

#TODO take care of the while command


#TODO genVar .store(), .load(), .assign(val)

#Remove jumps command dead code :
# The code immediatly after thoses can't execute :
# after return
# after break
# after continue

# redefine visitList function

class Simplifying(NodeTransformerAddedStmt):
  #def statementToAdd(self, stm): self.bodyToAddBefore[-1].append(stm)
  #def statementsToAdd(self, stms): self.bodyToAddBefore[-1] += stms

  #def visit_BoolOp(self, node): pass #TODO very specials
  def visit_BinOp(self, node):
    # BitAnd | FloorDiv

    varLeft = self.geneVariable('left_operand')
    varRight = self.geneVariable('rigth_operand')
    varExpr = self.geneVariable('resultBinOp')

    #keep this order
    exprLeft = self.visit(node.left)
    exprRight = self.visit(node.right)

    self.statementsToAdd([
        #varLeft = exprLeft
        Assign([Name(varLeft, Store())], exprLeft),
        #varRight = exprRight
        Assign([Name(varRight, Store())], exprRight),
        #varExpr = varLeft + varRight
        Assign(
          [Name(varExpr, Store())],
          BinOp( Name(varLeft, Load()), node.op ,Name(varRight, Load()) ),
        )
    ])

    return Name(varExpr, Load())


  def visit_UnaryOp(self, node):
    varOp = self.geneVariable('resultUnaryOp')
    exprOp = self.visit(node.operand)

    self.statementsToAdd([
      #varOp = - exprOp
      Assign([Name(varOp, Store())], UnaryOp(node.op, exprOp)),
    ])

    return Name(varOp, Load())

  #def visit_Lambda(self, node): #TODO transform lambda into a def function
  #def IfExp(self, node): #TODO transform into a real if expression


  def visit_Dict(self, node):
    varDict = self.geneVariable('dict')
    self.statementToAdd(
      #varDict = dict()
      Assign([Name(varDict, Store())], Call(Name('dict', Load()), [], [], None, None) ),
    )

    for k, v in zip(node.keys, node.values):
      varKey = self.geneVariable('key')
      varVal = self.geneVariable('val')

      exprVal = self.visit(v)
      exprKey = self.visit(k)

      self.statementsToAdd( [
          #varVal = exprVal
          Assign([Name(varVal, Store())] , exprVal),
          #varKey = exprKey
          Assign([Name(varKey, Store())] , exprKey),
          #varDict.__setitem__(varKey, varVal)
          Expr(
            Call(
              Attribute(Name(varDict, Load()), '__setitem__', Load()),
              [Name(varKey, Load()), Name(varVal, Load())], [], None, None
            )
          ),
      ])

    return Name(varDict, Load())


  def visit_Set(self, node):
    varSet = self.geneVariable('set')
    self.statementToAdd(
      #varSet = set()
      Assign([Name(varSet, Store())], Call(Name('set', Load()), [], [], None, None) ),
    )

    for e in node.elts:
      varElt = self.geneVariable('elt')

      exprElt = self.visit(e)

      self.statementsToAdd([
        #varElt = exprElt
        Assign([Name(varElt, Store())] , exprElt),
        #varSet.add( exprElt )
        Expr(
          Call(
            Attribute(Name(varSet, Load()), 'add', Load()),
            [Name(varElt, Load())], [], None, None
          )
        ),
      ])

    return Name(varSet, Load())


  def visit_Tuple(self, node):

    nameLoad = self.visit_List(node) #duck typing powaaaa

    #because we used a list to tmp puts things in, go back to tuple
    varTuple = self.geneVariable('tuple')
    self.statementToAdd(
      Assign([Name(varTuple, Store())], Call(Name('tuple', Load()), [nameLoad], [], None, None) ),
    )

    return Name(varTuple, Load())


  def visit_List(self, node):
    varList = self.geneVariable('list')
    self.statementToAdd(
      #varList = tuple()
      Assign([Name(varList, Store())], Call(Name('list', Load()), [], [], None, None) ),
    )

    for e in node.elts:
      varElt = self.geneVariable('elt')

      exprElt = self.visit(e)

      self.statementsToAdd([
        #varElt = exprElt
        Assign([Name(varElt, Store())] , exprElt),
        #varList.add( exprElt )
        Expr(
          Call(
            Attribute(Name(varList, Load()), 'append', Load()),
            [Name(varElt, Load())], [], None, None
          )
        ),
      ])

    return Name(varList, Load())

  def visit_Repr(self, node):
    varRepr = self.geneVariable('repr')
    varValue = self.geneVariable('value')

    exprValue = self.visit(node.value)

    self.statementsToAdd([
      #varValue = exprValue
      Assign([Name(varValue, Store())] ,exprValue),
      #varRepr = repr(varValue)
      Assign([Name(varRepr, Store())], Call(Name('repr', Load()), [Name(varValue, Load())], [], None, None ) ),
    ])

    return Name(varRepr, Load())


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

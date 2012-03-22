#!/usr/bin/env python
import ast
from ast import *
from nodeTransformer import *

#TODO take care of the Yield element (maybe before that, to be simplier)
#TODO take care of the attribute element (maybe just for load stuffs)

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
    if not isinstance(node.ctx, Load):
      return self.generic_visit(node)

    nameLoad = self.visit_List(node) #duck typing powaaaa

    #because we used a list to tmp puts things in, go back to tuple
    varTuple = self.genVar('tuple')
    self.statementToAdd(
      varTuple.assign( Call(Name('tuple', Load()), [nameLoad], [], None, None) ),
    )

    return varTuple.load()


  def visit_List(self, node):
    if not isinstance(node.ctx, Load):
      return self.generic_visit(node)

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


  def visit_While(self, node):
    cdtVar = self.genVar('cdt')
    testBefore = node.test

    self.statementToAdd( cdtVar.assign(nodeCopy(node.test)) )

    return While(cdtVar.load(),
       self.visit_a_StatementList(
         node.body + self.visit_a_StatementList([cdtVar.assign(nodeCopy(node.test))])
       ),
    self.visit(node.orelse))


  def visit_Compare(self, node):
    #to remove recursive problems
    if isinstance(node.left, Name) \
        and len(node.comparators) == 1 \
        and isinstance(node.comparators[0], Name):
      return self.generic_visit(node)

    #TODO the if test on res is done each times, optimise that

    resVar = self.genVar('res')
    self.statementToAdd( resVar.assign( Name('True', Load()) ) )

    rightVar = self.genVar('lefOp')
    self.statementToAdd( rightVar.assign( self.visit(node.left) ) )

    for n, (ops, comp) in enumerate(zip(node.ops, node.comparators)):
      leftVar, rightVar = rightVar, self.genVar('rightOp%s' % n)

      #if res:
      self.statementsToAdd([ If( resVar.load(),
        #rightVar = comp
        self.visit_a_StatementList([rightVar.assign( comp )]) +
        #res = leftVar < rightVar
        [resVar.assign(Compare(leftVar.load(), [ops], [rightVar.load()]))]
      ,[])])

    return resVar.load()

  def visit_BoolOp(self, node):
    #to remove recursive problems
    if len(node.values) == 2\
        and isinstance(node.values[0], Name) \
        and isinstance(node.values[1], Name):
      return self.generic_visit(node)

    if isinstance(node.op, Or): return self.visit_BoolOpOr(node)
    if isinstance(node.op, And): return self.visit_BoolOpAnd(node)
    assert False

  def visit_BoolOpOr(self, node): #visit special for and comparators

    resVar = self.genVar('res')
    self.statementToAdd(resVar.assign(Name('False', Load())))

    notResVar = self.genVar('notRes')

    for val in node.values:
      #if res:
      self.statementsToAdd([
        notResVar.assign(UnaryOp(Not(), resVar.load()) ),
        If( notResVar.load(),
        #res = val
        self.visit_a_StatementList([resVar.assign(val)])
      ,[])])

    return resVar.load()


  def visit_BoolOpAnd(self, node): #visit special for and comparators

    resVar = self.genVar('res')
    self.statementToAdd(resVar.assign(Name('True', Load())))
    #TODO can be optimised by imbricating if statements

    for val in node.values:
      #if res:
      self.statementsToAdd([ If( resVar.load(),
        #res = val
        self.visit_a_StatementList([resVar.assign(val)])
      ,[])])

    return resVar.load()


  def visit_IfExpr(self, node):
    tmpVar = self.genVar('tmp')

    res = self.visit_a_StatementList([
     If(node.test,
       tmpVar.assign(node.body),
       tmpVar.assign(node.orelse),
    )])

    self.statementsToAdd(res)

    return tmpVar.load()

  #transform lambda into real def function
  def visit_Lambda(self, node):
    fctName = self.genVar('fct')

    args = nodeCopy(node.args)
    body = node.body

    res = self.visit_a_StatementList([FunctionDef(
        fctName.name,
        args,
        [Return(body)],
        [])])
    self.statementsToAdd(res)

    return fctName.load()


  def _transformComprIfs(self, ifs, inside):
    """
    Transform transformation ifs
    putting inside all the imbricated ifs
    return a list of statements
    """
    if len(ifs) == 0: return inside
    head, tail = ifs[0], ifs[1:]

    return [ If(head, self._transformComprIfs(tail, inside), []) ]



  def _transformComprFors(self, comprList, inside):
    """
    Generate the "for"s of a comprehension, putting inside at the center
    Return a list of statements
    """
    if len(comprList) == 0: return inside
    head, tail = comprList[0], comprList[1:]

    return [
        For(head.target, head.iter,
          self._transformComprIfs(head.ifs,
            self._transformComprFors(tail, inside))
          , [])
    ]

    return comprList


  def visit_ListComp(self, node):
    genList = self.genVar('genList')

    self.statementToAdd(genList.assign(Call(Name('list', Load()), [], [], None, None)))
    append = [ Expr(Call(genList.load('append'), [node.elt], [], None, None)) ]
    elements = self._transformComprFors(node.generators, append)
    res = self.visit_a_StatementList( elements )
    self.statementsToAdd(res)

    return genList.load()

  def visit_SetComp(self, node):
    genSet = self.genVar('genSet')

    self.statementToAdd(genSet.assign(Call(Name('set', Load()), [], [], None, None)))
    append = [ Expr(Call(genSet.load('add'), [node.elt], [], None, None)) ]
    elements = self._transformComprFors(node.generators, append)
    res = self.visit_a_StatementList( elements )
    self.statementsToAdd(res)

    return genSet.load()

  def visit_DictComp(self, node):
    genDict = self.genVar('genDict')
    keyVar, valVar = self.genVar('key'), self.genVar('val')

    self.statementToAdd(genDict.assign(Call(Name('dict', Load()), [], [], None, None)))
    append = [
        valVar.assign(node.value),
        keyVar.assign(node.key),
        Expr(Call(genDict.load('__setitem__'), [keyVar.load(), valVar.load()], [], None, None))
    ]
    elements = self._transformComprFors(node.generators, append)
    res = self.visit_a_StatementList( elements )
    self.statementsToAdd(res)

    return genDict.load()


  def visit_GeneratorExp(self, node):
    myFct = self.genVar('myFct')
    myGenerator = self.genVar('myGenerator')

    append = [ Expr(Yield(node.elt)) ]
    elements = self._transformComprFors(node.generators, append)

    fctBody = [
        FunctionDef( myFct.name,
          arguments([], None, None, []),
          elements,
          []),
        myGenerator.assign(Call(myFct.load(), [], [], None, None)),
    ]

    res = self.visit_a_StatementList( fctBody )
    self.statementsToAdd(res)

    return myGenerator.load()

  def visit_Attribute(self, node):
    if not isinstance(node.ctx, Load): return self.generic_visit(node)

    tmpVar = self.genVar('tmp')
    self.statementsToAdd([
      tmpVar.assign(Attribute(self.visit(node.value), node.attr, Load())),
    ])

    return tmpVar.load()


#__EOF__

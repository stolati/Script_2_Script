#!/usr/bin/env python

from ast import *
import nodeTransformer

#simplify the try statement so it can be ported to SIMPLE easely
#
#in the AST stuff, there is 2 elements :
# It seems that the except is in a finally when it comes

# TryExcept(body[], handlers[], orelse[])
#   ExceptHandler(type, name, body[])
# TryFinally(body[], finalbody[])

#TODO we have to think about the Raise(type, inst, tback) element


class TrySimplifier(nodeTransformer.NodeTransformer):


  #return an if cdt for that handler
  def _transformHandler(self, handler, varName):
    cdt = Name('True', Load())
    body = handler.body

    if handler.type :
      #isinstance(varName, handler.type)
      cdt = Call(
         Name('isinstance', Load()) ,
         [
           Name(varName, Load()),
           Name(handler.type.id, Load()),
         ],
         [], None, None
      )

    if handler.name :
      #handler.name = varName
      bodyFirst = [Assign(
        [Name(handler.name.id, Store())],
        Name(varName, Load()),
      )]
      body = bodyFirst + body

    return If(cdt, body, [])


  def _transformHandlers(self, handlers):
    handlers = list(handlers)
    handlers.reverse()

    errVarName = self.geneVariable()
    #defining the super handler
    myHdl = ExceptHandler(
        Name('Exception', Load()),
        Name(errVarName, Store()),
        [], #not defined yet
    )

    currHdl = Raise()

    for h in handlers:
      h = self._transformHandler(h, errVarName)
      h.orelse = [currHdl]
      currHdl = h

    myHdl.body = [currHdl]
    return [myHdl]


  def _generate(self, body, handlers, orelse, finalbody):
    #pathological cases, empty try body
    if self.isEmpty(body): return orelse + finalbody

    #transform each handlers into an if case, regrouping handlers into one
    handlers = self._transformHandlers(handlers)
    assert len(handlers) == 1

    if self.isEmpty(orelse): #no orelse clause
      #return the tryfinally without orelse
      return TryFinally(
          [TryExcept(
            body,
            handlers,
            [],
          )],
          finalbody
      )

    if self.isEmpty(finalbody):
      #no finally clause, but have a orelse one
      return [TryFinally(
          [TryExcept(
            body,
            handlers,
            [],
          )],
          []
      )] + orelse


    isErrorOrelse = self.geneVariable()

    #isErrorOrelse = False
    before = [
        Assign([Name(isErrorOrelse, Store())], Name('False', Load()) ),
    ]

    #isErrorOrelse = True ; orelse
    afterBody = [
        Assign([Name(isErrorOrelse, Store())], Name('True', Load()) ),
    ] + orelse

    currIf = handlers[0].body
    newIf = [
        If(
          Name(isErrorOrelse, Load()),
          [Raise()],
          currIf,
        ),
    ]
    handlers[0].body = newIf

    return before + [TryFinally(
        [TryExcept(
          body+ afterBody,
          handlers,
          [],
        )],
        finalbody
    )]


  def visit_TryExcept(self, node):
    return self._generate(
        self.visit(node.body),
        self.visit(node.handlers),
        self.visit(node.orelse),
        [] #from the missing tryFinally
    )


  def visit_TryFinally(self, node):
    #test if we have except inside
    haveExcept = (len(node.body) == 1 and isinstance(node.body[0], TryExcept))

    if not haveExcept:
      return self._generate(
          self.visit(node.body),
          [],
          [],
          self.visit(node.finalbody),
      )

    exceptNode = node.body[0]
    return self._generate(
        self.visit(exceptNode.body),
        self.visit(exceptNode.handlers),
        self.visit(exceptNode.orelse),
        self.visit(node.finalbody),
    )



#__EOF__

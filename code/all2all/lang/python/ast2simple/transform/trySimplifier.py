#!/usr/bin/env python

from ast import *
import nodeTransformer

from all2all.lang.python.ast2simple.astPrint import Print_python

#simplify the try statement so it can be ported to SIMPLE easely
#
# The goal is to have only 3 elements :
#   try {
#     a1
#   } catch (exception name01) {
#     a2 <= isinstanceof tests for each exception type
#   } finally { a3 }
#


#Example :
#  try:
#      code
#      raise ???
#  except IOERror as (errno, streeror):
#    print toto
#    raise ???
#  except IOERror as err:
#    print toto
#    raise ???
#  except ValueError:
#    print "could not convert to integer"
#    raise ???
#  except:
#    print "toto"
#    raise
#  else:
#    #code if no exception has been raised
#  finally:
#    #code everytime
#

#try :
#  codeA32Error = False
#  try:
#      code
#      raise ???
#    try:
#       code a32
#    except Exception as err6789:
#       codeA32Error = True
#       raise err6789
#  except Exception as err1234:
#    if codeA32Error :
#      raise err1234
#    elseif isintanceof(err, IOError):
#      (errno, streeror) = err1234
#      print toto
#      raise err1234
#    elsif isintanceof(err1324, IOError):
#      err = err1234
#      print toto
#      raise err1234
#    elsif isinstance(err1234, ValueError):
#      print "could not convert to integer"
#      raise err1234
#    else:
#      print "toto"
#      raise err1234
#  else:
#    code a32
#    #code if no exception has been raised
#  finally:
#    #code everytime
#


#cases 1 complex, all is here :

#try :
#  codeA32Error = False
#  try:
#      code
#      raise ???
#    try:
#       code a32
#    except Exception as err6789:
#       codeA32Error = True
#       raise err6789
#  except Exception as err1234:
#    if codeA32Error :
#      raise err1234
#    elseif isintanceof(err, IOError):
#      (errno, streeror) = err1234
#      print toto
#      raise err1234
#    elsif isintanceof(err1324, IOError):
#      err = err1234
#      print toto
#      raise err1234
#    elsif isinstance(err1234, ValueError):
#      print "could not convert to integer"
#      raise err1234
#    else:
#      print "toto"
#      raise err1234
#  finally:
#    #code everytime
#


#cases 2 without finally :

#try :
#  try:
#      code
#      raise ???
#  except Exception as err1234:
#    if isintanceof(err, IOError):
#      (errno, streeror) = err1234
#      print toto
#      raise err1234
#    elsif isintanceof(err1324, IOError):
#      err = err1234
#      print toto
#      raise err1234
#    elsif isinstance(err1234, ValueError):
#      print "could not convert to integer"
#      raise err1234
#    else:
#      print "toto"
#      raise err1234
#  code a32


#cases 3 : without else

#try :
#  try:
#      code
#      raise ???
#  except Exception as err1234:
#    if isintanceof(err, IOError):
#      (errno, streeror) = err1234
#      print toto
#      raise err1234
#    elsif isintanceof(err1324, IOError):
#      err = err1234
#      print toto
#      raise err1234
#    elsif isinstance(err1234, ValueError):
#      print "could not convert to integer"
#      raise err1234
#  finally:
#    #code everytime
#

#cases 3 : without else and without finally

#try :
#  try:
#      code
#      raise ???
#  except Exception as err1234:
#    if codeA32Error :
#      raise err1234
#    elseif isintanceof(err, IOError):
#      (errno, streeror) = err1234
#      print toto
#      raise err1234
#    elsif isintanceof(err1324, IOError):
#      err = err1234
#      print toto
#      raise err1234
#    elsif isinstance(err1234, ValueError):
#      print "could not convert to integer"
#      raise err1234
#


# So we must have a stuff that say :
#  the else is inside the try
#  or the else is at the end of the try
#
# inside : with finally and else not null
#  => variable + try + first if


#special case when there is only one except (or none)

#the transformation should be :
# TryFinally(body = TryExcept [], finalbody [])
# even when there is no execpt clauses





#in the AST stuff, there is 2 elements :
# It seems that the except is in a finally when it comes

# TryExcept(body[], handlers[], orelse[])
#   ExceptHandler(type, name, body[])
# TryFinally(body[], finalbody[])

#we have to think about the Raise(type, inst, tback) element


def log(fct):
  def f(*args, **kargs):
    print args
    res = fct(*args, **kargs)
    print 'res = ', Print_python(res)
    return res

  return f





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


  #@log
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









##search for a break method inside a for element
##use the inside function
#class HaveBreak(NodeVisitor):
#  class HaveBreakException(Exception): pass
#
#  def visit_Break(self, node): raise HaveBreak.HaveBreakException()
#  def visit_For(self, node): return #don't look for inside For
#  def visit_While(self, node): return #don't look for inside While
#
#  #return if there is a break inside a For ast statement
#  #Should be a For element
#  @staticmethod
#  def inside(node):
#    assert isinstance(node, For)
#    try:
#      for subNode in node.body:
#        HaveBreak().visit(subNode)
#    except HaveBreak.HaveBreakException:
#      return True
#    return False
#
#
##transforme in an ast nodes
##each for loops into a while equivalent loops
#class ForIntoWhile(nodeTransformer.NodeTransformer):
#
#  def breakNElse(self, for_node):
#    """Tell if a node use the breakNelse statements"""
#    assert isinstance(for_node, For)
#    return bool(for_node.orelse) and HaveBreak.inside(for_node)
#
#
#  def visit_For(self, node):
#
#    #prepare the For statement
#    f_target = self.visit(node.target)
#    f_iter = self.visit(node.iter)
#    f_body = [self.visit(e) for e in node.body]
#    f_orelse = [self.visit(e) for e in node.orelse]
#    f = For(f_target, f_iter, f_body, f_orelse)
#
#    if self.breakNElse(f):
#      return self._genComplexFor(node)
#    return self._genSimpleFor(node)
#
#
#  #from a For, generate a simple while
#  #it must not have a break linked to the else
#  #it never use break, and always execute the else
#  #
#  #continueIter = True
#  #aIter = iter(a3)
#  #while continueIter:
#  #  try:
#  #    a1 = aIter.next() #python 2.x
#  #  except: StopIteration:
#  #    continueIter = False
#  #  a3
#  #else:
#  #  a4
#  #
#  def _genSimpleFor(self, node):
#    aIter = self.geneVariable()
#    continueIter = self.geneVariable()
#
#    res = [
#      #aIter = iter(a3)
#      Assign(
#        [Name(aIter, Store())],
#        Call(Name('iter', Load()), [node.iter], [], None, None),
#      ),
#      #while continueIter:
#      While( Name('True', Load()),
#        [
#          #try
#          TryExcept(
#            #a1 = aIter.next()
#            [Assign(
#              [node.target],
#              Call(
#                Attribute(Name(aIter, Load()), 'next', Load()),
#                [], [], None, None
#              ),
#            )],
#            #except: StopIteration:
#            [ ExceptHandler(Name('StopIteration', Load()), None, [
#              #continueIter = False
#              Break(),
#            ]) ],
#          []),
#          #a3
#        ] + node.body,
#        [],
#      ),
#      #a4
#    ] + node.orelse
#
#    return res
#
#
#
#  #from a Fro, generate a full while
#  #it can have a break linked to the else
#  #
#  #continueIter = True
#  #aIter = iter(a3)
#  #while continueIter:
#  #  try:
#  #    a1 = aIter.next() #python 2.x
#  #    a1 = next(aIter) #python 3.x
#  #  except: StopIteration:
#  #    continueIter = False
#  #  if not continueIter:
#  #    a3
#  #else:
#  #  a4
#  #
#  def _genComplexFor(self, node):
#    aIter = self.geneVariable()
#    continueIter = self.geneVariable()
#
#    res = [
#      #continueIter = True
#      Assign(
#        [Name(continueIter, Store())],
#        Name('True', Load()),
#      ),
#      #aIter = iter(a3)
#      Assign(
#        [Name(aIter, Store())],
#        Call(Name('iter', Load()), [node.iter], [], None, None),
#      ),
#      #while continueIter:
#      While( Name(continueIter, Load()),
#        [
#          #try
#          TryExcept(
#            #a1 = aIter.next()
#            [Assign(
#              [node.target],
#              Call(
#                Attribute(Name(aIter, Load()), 'next', Load()),
#                [], [], None, None
#              ),
#            )],
#            #except: StopIteration:
#            [ ExceptHandler(Name('StopIteration', Load()), None, [
#              #continueIter = False
#              Assign(
#                [Name(continueIter, Store())],
#                Name('False', Load()),
#              )
#            ]) ],
#          []),
#          #if not continueIter: a3
#          If( Name(continueIter, Load()),
#            node.body,
#          [])
#        ],
#        #else: a4
#        node.orelse,
#      ),
#    ]
#
#    return res

#__EOF__

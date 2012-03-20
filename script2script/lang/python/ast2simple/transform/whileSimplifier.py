#!/usr/bin/env python

from ast import *
import nodeTransformer

#the while is simple (and in Simple, there are whiles)
#while a1:
#  a2
#else:
#  a3

#The only stuff that is strange in python is the else case
#it is executed if the while didn't return as a result of a "break"

#TODO should be reunificated between for and while
#search for a break method inside a while element
#use the inside function
class HaveBreak(NodeVisitor):
  class HaveBreakException(Exception): pass

  def visit_Break(self, node): raise HaveBreak.HaveBreakException()
  def visit_For(self, node): return #don't look for inside for
  def visit_While(self, node): return #don't look for inside while

  #return if there is a break inside a For ast statement
  #Should be a For element
  @staticmethod
  def inside(node):
    assert isinstance(node, While)
    try:
      for subNode in node.body:
        HaveBreak().visit(subNode)
    except HaveBreak.HaveBreakException:
      return True
    return False


class WhileSimplifier(nodeTransformer.NodeTransformer):

  def breakNElse(self, while_node):
    """Tell if a node use the breakNelse statements"""
    assert isinstance(while_node, While)
    return bool(while_node.orelse) and HaveBreak.inside(while_node)

  def visit_While(self, node):
    #prepare the While statement
    w_test = self.visit(node.test)
    w_body = self.visitList(node.body)
    w_orelse = self.visitList(node.orelse)

    w = While(w_test, w_body, w_orelse)

    if self.breakNElse(w):
        return self._genComplexWhile(w)

    return self._genSimpleWhile(w)


  # Replace the while with :
  # while a1:
  #   a2
  # a3
  # because in this version, there is no break, or else is empty
  def _genSimpleWhile(self, node):
    return [
            While(node.test, node.body, [])
    ] + node.orelse

  #Replace the complexe with :
  # hadBreak = False
  # while a1:
  #   a2 => if break, set hadBreak to true just before
  # if hadBreak:
  #   a3
  def _genComplexWhile(self, node):
      goElse = self.genVar()
      def beforeBreakFactory():
        return [goElse.assign(Name('False', Load()))]
      chgBreakVisitor = AddIf2Break(beforeBreakFactory)

      return [
        #hadBreak = False
        Assign(
            [goElse.store()],
            Name('True', Load()),
        ),
        #while a1
        While(
            node.test,
            chgBreakVisitor.visit(node.body),
            [],
        ),
        #if hadBreak : a3
        If(
            goElse.load(),
            node.orelse,
            []
        ),
      ]


#for the complexe while replacing
#set a value if a break is executed
class AddIf2Break(nodeTransformer.NodeTransformer):
  def __init__(self, beforeNodesFactory):
      self._bnf = beforeNodesFactory #nodes to add before the break statement

  #don't wisit loops under this one, (the break variable is different)
  #def visit_For(self, node): return node
  #def visit_While(self, node): return node

  def visit(self, node):
    res = nodeTransformer.NodeTransformer.visit(self, node)
    return res

  def visit_Break(self, node):
    res = self._bnf() + [node]
    return res


#__EOF__

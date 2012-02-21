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
  def visit_For(self, node): return #don't look for inside For
  def visit_While(self, node): return #don't look for inside While

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
    w_body = [self.visit(e) for e in node.body]
    w_orelse = [self.visit(e) for e in node.orelse]
    w = While(w_test, w_body, w_orelse)
    
    if self.breakNElse(w):
      print "complex"
      return w
    
    return self._genSimpleWhile(w)
  
  
  # Replace the while with :
  # while a1:
  #   a2
  # a3
  # because in this version, there is no break, or else is empty
  def _genSimpleWhile(self, node):
    res  = [
      While(node.test, node.body, [])
    ] + node.orelse
    res = [fix_missing_locations(e) for e in res]
    return res
  
  

#__EOF__

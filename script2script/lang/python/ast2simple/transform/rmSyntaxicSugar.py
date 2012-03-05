#!/usr/bin/env python

#TODO : List to list
#TODO : Tuple to tuple
#TODO : Dict to Dict

#TODO : multiple assign
#TODO : augassign
#TODO : compare

from ast import *
import nodeTransformer

# transform some elements into their counterparts :
#  augassign (for simple variables, instance variable, slice elements) (file example 18)
#  slice elements into calls
#  del calls on (simple variables, not instance variable, slice elements)
#

class RmSyntaxicSugar(nodeTransformer.NodeTransformer):

  #TODO a nodeTransformer that can add execution before code
  #def visit_List(self, node):
  #  if not isinstance(node.ctx, Load):
  #    return self.generic_visit(node)

  #  #tmpVar = list()
  #  #tmpVar.__add__(elemnts)
  #  #tmpVar
  #  elts = [ self.visit(e) for e in node.elts ]


  #def visit_Tuple(self, node):
  #  if not isinstance(node.ctx, Load):
  #    return self.generic_visit(node)

  #  #tmpVar = tuple()
  #  #tmpVar.__add__(elemnts)
  #  #tmpVar
  #  elts = [ self.visit(e) for e in node.elts ]


  #def visit_Dict(self, node):
  #  for elements, toto in couple(keys, values):
  #   
  #  tmpVar = dict()
  #  tmpVar.__setitem__(key, value)
  #  tmpVar
  #

  def visit_Delete(self, node):
    if len(node.targets) == 1: return self.generic_visit(node)
    return [ Delete([self.visit(e)]) for e in node.targets ]

  #def visit_Assign(self, node):
  # unpack(target_list, expression)
  # 
  # 
  #
  #
  #
  #
  #
  #
  #




#__EOF__

#!/usr/bin/env python

from ast import *
import nodeTransformer

# transform some elements into their counterparts :
#  augassign (for simple variables, instance variable, slice elements) (file example 18)
#  slice elements into calls
#  del calls on (simple variables, not instance variable, slice elements)
#


class ContainerEmulate(nodeTransformer.NodeTransformer):

  def sliceIntoParam(self, slice_val):
    if isinstance(slice_val, Index):
      return self.visit(slice_val.value)
    #TODO Ellipsis
    #TODO Slice
    #TOOD ExtSlice
    assert False, "not implemented now"


  def visit_Subscript(self, node):
    #assert isinstance(node.ctx, Load) #be sure the other cases are already taken
    if not isinstance(node.ctx, Load): return node

    value = self.visit(node.value)
    slice_val = self.sliceIntoParam(node.slice)
    assert isinstance(node.ctx, Load)

    #a1[a2] => a1.__getitem__(a2)
    return Call(
        Attribute(value, '__getitem__', Load()),
        [slice_val], [], None, None
    )


  #TODO AugAssign
  #TODO del

  def visit_Assign(self, node):
    #TODO test assign multiple use, list all assign use
    #TODO do a change for assign stuffs to 1 element
    assert len(node.targets) == 1
    target = node.targets[0]
    if not isinstance(target, Subscript):
      return self.generic_visit(node)

    value = self.visit(target.value)
    slice_val = self.sliceIntoParam(target.slice)
    assert isinstance(target.ctx, Store)

    ass_right = self.visit(node.value)

    #a1[a2] = a3 => a1.__setitem__(a2, a3)

    return Expr( #because Assign is a statement, not a expression
        Call(
          Attribute(value, '__setitem__', Load()),
          [slice_val, ass_right], [], None, None
        )
    )

  def visit_Delete(self, node):
    #TODO test delete multiple use, list all delete use
    #TODO do a change for delete stuffs to 1 element
    assert len(node.targets) == 1
    target = node.targets[0]
    if not isinstance(target, Subscript):
      return self.generic_visit(node)

    value = self.visit(target.value)
    slice_val = self.sliceIntoParam(target.slice)
    assert isinstance(target.ctx, Del)

    #del a1[a2] => a1.__detitem__(a2)

    return Expr( #because Delete is a statement, not a expression
        Call(
          Attribute(value, '__delitem__', Load()),
          [slice_val], [], None, None
        )
    )


  #def visit_AugAssign(self, node):
  #  #TODO be more intelligent
  #  if not isinstance(node.target, Subscript):
  #    return self.generic_visit(node)

  #  value = self.visit(node.target.value)
  #  slice_val = self.sliceIntoParam(node.target.slice)
  #  print node.target.ctx
  #  assert isinstance(node.target.ctx, Store)
  #  op = self.visit(node.op)
  #  ass_right = self.visit(node.value)

#container type:
#  __getitem__(self, key)
#  __setitem__(self, key, value)
#  __delitem__(self, key)
#  __iter__(self)
#  __contains__(self, item)

#key could be slices, integer, or anything
#


#
#should test slice
#




#__EOF__

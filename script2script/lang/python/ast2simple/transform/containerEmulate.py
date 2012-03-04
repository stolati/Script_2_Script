#!/usr/bin/env python

#TODO : delete multiple uses => delete single use
#TODO : assign multiple uses => assign single use

#TODO : augassign
#TODO : slice : x[1:, :, ...] => (slice(1, None, None), slice(None, None, None), Ellipsis)


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
    elif isinstance(slice_val, Slice):
      lower = self.visit(slice_val.lower) or Name('None', Load())
      upper = self.visit(slice_val.upper) or Name('None', Load())
      step = self.visit(slice_val.step) or Name('None', Load())

      return Call(
          Name('slice', Load()),
          [lower, upper, step], [], None, None
      )
    elif isinstance(slice_val, Ellipsis):
      return Name('Ellipsis', Load())
    elif isinstance(slice_val, ExtSlice):
      return Tuple(
        [self.sliceIntoParam(s) for s in slice_val.dims],
        Load()
      )
    else: assert False, "slice type unknown"


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

  def visit_Assign(self, node):
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


  def visit_AugAssign(self, node):
    if not isinstance(node.target, Subscript):
      return self.generic_visit(node)

    operator = self.visit(node.op)
    value = self.visit(node.value)

    target_value = self.visit(node.target.value)
    target_slice = self.sliceIntoParam(node.target.slice)
    target_ctx = Store()

    #list[a] += value =>
    # listValue = list
    # sliceValue = slice
    # getValue = listValue.__getitem__(a)
    # getValue += value
    # listValue.__setitem__(a, getValue)

    listVar = self.geneVariable()
    sliceVar = self.geneVariable()
    contentValVar = self.geneVariable()

    return [
        Assign( [Name(listVar, Store())], target_value),
        Assign( [Name(sliceVar, Store())], target_slice),
        Assign( [Name(contentValVar, Store())],
          Call(
            Attribute(Name(listVar, Load()), '__getitem__', Load()),
            [Name(sliceVar, Load())], [], None, None
          )
        ),
        AugAssign(Name(contentValVar, Store()), operator, value),
        Expr(Call(
          Attribute(Name(listVar, Load()), '__setitem__', Load()),
          [Name(sliceVar, Load()), Name(contentValVar, Load())], [], None, None
        )),
    ]


#container type:
#TODO  __contains__(self, item)

#__EOF__

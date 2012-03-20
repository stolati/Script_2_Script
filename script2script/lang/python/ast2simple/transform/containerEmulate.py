#!/usr/bin/env python

#TODO : compare multiple uses => compare single use

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

    listVar = self.genVar()
    sliceVar = self.genVar()
    contentValVar = self.genVar()

    return [
        listVar.assign(target_value),
        sliceVar.assign(target_slice),
        contentValVar.assign(
          Call(
            listVar.load('__getitem__'),
            [sliceVar.load()], [], None, None
          )
        ),
        AugAssign(contentValVar.store(), operator, value),
        Expr(Call(
          listVar.load('__setitem__'),
          [sliceVar.load(), contentValVar.load()], [], None, None
        )),
    ]


  #cmpop = In NotIn
  def visit_Compare(self, node):
    assert len(node.ops) == 1
    assert len(node.comparators) == 1
    isOpIn = isinstance(node.ops[0], In)
    isOpNotIn = isinstance(node.ops[0], NotIn)
    if not isOpIn and not isOpNotIn: return self.generic_visit(node)

    left = self.visit(node.left)
    ops = self.visit(node.ops[0])
    comp = self.visit(node.comparators[0])

    #a in b => b.__contains__(a)
    res = Call(
        Attribute( comp , '__contains__', Load()),
        [left], [], None, None
    )

    if isOpNotIn: #not b.__contains__(a)
      res = UnaryOp(
          Not(),
          res,
      )

    return res

#__EOF__

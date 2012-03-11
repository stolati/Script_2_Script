#!/usr/bin/env python

#TODO : List to list
#TODO : Tuple to tuple
#TODO : Dict to Dict

#TODO : augassign
#TODO : compare

#TODO assignOnlyOne, do it for a = b = c = {}
#TODO assignOnlyOne, check when [a, b, (a, b)] = [b, a, (b, a)] = toto

from ast import *
import nodeTransformer

# transform some elements into their counterparts :
#  augassign (for simple variables, instance variable, slice elements) (file example 18)
#  slice elements into calls
#  del calls on (simple variables, not instance variable, slice elements)
#

class DeleteOnlyOne(nodeTransformer.NodeTransformer):
  """
  Transform each ast.Delete node, so it contain only one element to delete
  """

  def visit_Delete(self, node):
    if len(node.targets) == 1: return self.generic_visit(node)
    return [ Delete([self.visit(e)]) for e in node.targets ]


class AssignOnlyOne(nodeTransformer.NodeTransformer):
  """
  Transform each ast.Assign node, so it contain only one element to assign
  TODO : we can optimise the result code,
  like the "a, b = b, a" don't need all the fussy stuff
  """

  def genAssign(self, varList, dataVariableName):
    """
    generate a code for affectation
    because of the order of Assign, we return a list of all the sub-tuple inside
    => (assign code, assign list, List(varList, dataVariableName))
    """

    tmpVar = self.geneVariable()
    numValue = self.geneVariable()
    #tmpVar = iter(dataVariableName)
    initPart = [Assign([Name(tmpVar, Store())], Call(Name('iter', Load()), [Name(dataVariableName, Load())], [], None, None))]

    moreVars = []
    affectations = []
    assignations = []
    for i, n in enumerate(varList.elts):
      myTmpName = self.geneVariable(i)
      affectations += [
          #tmpVar_<i> = tmpVar.next()
          Assign( [Name(myTmpName, Store())], Call(Attribute(Name(tmpVar, Load()), 'next', Load()), [], [], None, None ))
        ]

      if isinstance(n, Tuple) or isinstance(n, List):
        moreVars.append( (n, myTmpName) )
      else:
        assignations += [
            #var = tmpVar_<i>
            Assign( [n], Name(myTmpName, Load()) )
          ]


    tryAssign = [
        #try: affectations
        TryExcept(
          affectations,
          #except StopIteration:
          [ExceptHandler( Name('StopIteration', Load()), None, [
              #raise ValueError("need more value to unpack")
              Raise(Call(Name('ValueError', Load()), [Str("need more value to unpack")], [], None, None), None, None),
            ]
            )],
        [])
    ]

    testMoreValue = [
        #try:
        TryExcept(
          #tmpVar.next()
          [ Expr(Call(Attribute(Name(tmpVar, Load()), 'next', Load()), [], [], None, None )) ],
          #except StopIteration: pass
          [ExceptHandler( Name('StopIteration', Load()), None, [Pass()]) ],
          #else : raise ValueError("too many values to unpack")
          [
            Raise(Call(Name('ValueError', Load()), [Str("too many values to unpack")], [], None, None), None, None),

          ])
    ]

    return (initPart + tryAssign + testMoreValue, assignations, moreVars)


  def assertValid(self, node):
    if isinstance(node, Tuple) or isinstance(node, List):
      assert isinstance(node.ctx, Store)
      for n in node.elts: self.assertValid(n)
    else:
      assert isinstance(node, Name) or isinstance(node, Attribute)


  def visit_Assign(self, node):
    assert len(node.targets) == 1
    target = node.targets[0]
    if isinstance(target, Name) or isinstance(target, Attribute):
      return node

    vName = self.geneVariable()
    before = [
        Assign([Name(vName, Store())], node.value)
    ]
    after = []

    toProcess = [(target, vName)]

    while(toProcess):
      curTarget, curVName = toProcess.pop(0)
      c, l, others = self.genAssign(curTarget, curVName)
      before += c
      after += l
      toProcess += others

    return before + after



#__EOF__

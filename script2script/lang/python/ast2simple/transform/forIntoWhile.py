#!/usr/bin/env python

from ast import *
import nodeTransformer

#the for is a semi-complexe stuff it could be summarised as :
#for a1 in a2:
#  a3
#else:
#  a4

#The iterator from a2 is taken with the iter() function
#The "else" cause is only executed when for exit without break
#It's the same stuff than the while statement

##goal from wikipedia
#aIter = iter(a3)
#while True:
#  try:
#    a1 = aIter.next() #python 2.x
#    a1 = next(aIter) #python 3.x
#  except: StopIteration:
#    break
#  a3
#else:
#  a4

#but it don't work because of the stop, which bypass the else cause each times
#this version seems more good, at the cost of a variable

#continueIter = True
#aIter = iter(a3)
#while continueIter:
#  try:
#    a1 = aIter.next() #python 2.x
#    a1 = next(aIter) #python 3.x
#  except: StopIteration:
#    continueIter = False
#  if not continueIter:
#    a3
#else:
#  a4



#search for a break method inside a for element
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
    assert isinstance(node, For)
    try:
      for subNode in node.body:
        HaveBreak().visit(subNode)
    except HaveBreak.HaveBreakException:
      return True
    return False


#transforme in an ast nodes
#each for loops into a while equivalent loops
class ForIntoWhile(nodeTransformer.NodeTransformer):

  def breakNElse(self, for_node):
    """Tell if a node use the breakNelse statements"""
    assert isinstance(for_node, For)
    return bool(for_node.orelse) and HaveBreak.inside(for_node)


  def visit_For(self, node):

    #prepare the For statement
    f_target = self.visit(node.target)
    f_iter = self.visit(node.iter)
    f_body = self.visit(node.body)
    f_orelse = self.visit(node.orelse)
    f = For(f_target, f_iter, f_body, f_orelse)

    if self.breakNElse(f):
      return self._genComplexFor(node)
    return self._genSimpleFor(node)


  #from a For, generate a simple while
  #it must not have a break linked to the else
  #it never use break, and always execute the else
  #
  #continueIter = True
  #aIter = iter(a3)
  #while continueIter:
  #  try:
  #    a1 = aIter.next() #python 2.x
  #  except: StopIteration:
  #    continueIter = False
  #  a3
  #else:
  #  a4
  #
  def _genSimpleFor(self, node):
    aIter = self.genVar('iter')

    res = [
      #aIter = iter(a3)
      aIter.assign(
        Call(Name('iter', Load()), [node.iter], [], None, None),
      ),
      #while continueIter:
      While( Name('True', Load()),
        [
          #try
          TryExcept(
            #a1 = aIter.next()
            [Assign(
              [node.target],
              Call(
                aIter.load('next'),
                [], [], None, None
              ),
            )],
            #except: StopIteration:
            [ ExceptHandler(Name('StopIteration', Load()), None, [
              #continueIter = False
              Break(),
            ]) ],
          []),
          #a3
        ] + node.body,
        [],
      ),
      #a4
    ] + node.orelse

    return res



  #from a Fro, generate a full while
  #it can have a break linked to the else
  #
  #continueIter = True
  #aIter = iter(a3)
  #while continueIter:
  #  try:
  #    a1 = aIter.next() #python 2.x
  #    a1 = next(aIter) #python 3.x
  #  except: StopIteration:
  #    continueIter = False
  #  if not continueIter:
  #    a3
  #else:
  #  a4
  #
  def _genComplexFor(self, node):
    aIter = self.genVar('iter')
    continueIter = self.genVar('continue')

    res = [
      #continueIter = True
      continueIter.assign( Name('True', Load()) ),
      #aIter = iter(a3)
      aIter.assign(
        Call(Name('iter', Load()), [node.iter], [], None, None),
      ),
      #while continueIter:
      While( continueIter.load(),
        [
          #try
          TryExcept(
            #a1 = aIter.next()
            [Assign(
              [node.target],
              Call(
                aIter.load('next'),
                [], [], None, None
              ),
            )],
            #except: StopIteration:
            [ ExceptHandler(Name('StopIteration', Load()), None, [
              #continueIter = False
              continueIter.assign( Name('False', Load()),)
            ]) ],
          []),
          #if not continueIter: a3
          If( continueIter.load(),
            node.body,
          [])
        ],
        #else: a4
        node.orelse,
      ),
    ]

    return res

#__EOF__

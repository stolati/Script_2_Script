#!/usr/bin/env python

from nodeTransformer import *

#transforme in an ast nodes
#each for loops into a while equivalent loops
class ForIntoWhile(NodeTransformer):

  ##base
  #for a1 in a2:
  #  a3
  #else:
  #  a4

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


  def visit_For(self, node):
    genVar = self.geneVariable()

    return [
      #geneVar = iter(node.iter)
      ast.Assign(
        [Name(genVar)],
        ast.Call(Name('iter'), [node.iter], [], None, None)
      ),

      #while True
      ast.While(Name('True'),
        [
          ast.TryExcept( #try:
            [ast.Assign( #node.target = genVar.next()
              [node.target],
              ast.Call(
                ast.Attribute(Name(genVar), Name('next'), ast.Load()),
                [], [], None, None
              )
            )],
            #except StopIteration:
            [ ast.ExceptHandler(Name('StopIteration'), None, [ast.Break()]) ],
            []
          )
        ]+node.body, node.orelse),
    ]


if __name__ == "__main__": print "hello"


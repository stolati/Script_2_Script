#!/usr/bin/env python
from ast import NodeTransformer as Ast_NT



#declare a node transformer for inheritance
class NodeTransformer(Ast_NT):

  def geneVariable(self):
    if not hasattr(self, 'varNum'): self.varNum = 0
    self.varNum += 1
    return 'genVar_%s_%s' % (self.__class__.__name__, self.varNum)








#__EOF__

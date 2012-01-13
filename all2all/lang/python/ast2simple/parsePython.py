#!/usr/bin/env python

import ast
import astPrint

def parse(code, filename):
  return ASTWrapper(ast.parse(code, filename))


class ASTWrapper:
  def __init__(self, ast, printFunc = astPrint.print_python):
    self._content = ast
    self._printFunc = printFunc

  def __str__(self): return self._printFunc(self._content)

  def visiteWith(self, visitor):
    self._content = visitor.visit(self._content)


class MyFirstVisitor(ast.NodeTransformer):

  def visit_Module(self, node):
    print 'visiting node', node
    print ast.dump(node, False)

#ast.copy_location(new_node, old_node)
#ast.fix_missing_locations(node)
#ast.iter_fields(node) => (fieldname, value)
#ast.iter_child_nodes(node) -> [node] directly under it
#ast.walk(node) -> nodes (all of them)

#NodeTransformer.dump(node, annotate_fields=True, include_attributes=False)


#__EOF__

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


class NotExistsException(Exception):
  def __init__(self, name): Exception.__init__(self, 'The element "%s" should not exists'%name)


#TODO create metaclass for SimpleElement
#TODO so it can be like Python ast : _fields, constructor with fields, etc ...


#simple parts
class SimpleElement:
  _fields = []

  def __str__(self): raise NotImplementedError()
  #return the string passed, indented once, searching for \n char
  @staticmethod
  def _strIndent(s): return '\n'.join(['|  '+ss for ss in s.split('\n')])

  #return a list of fields in a dict manner
  def getFields(self): raise NotImplementedError()


class Module:
  _fields = ['body'] #the body is always an ExprList
  def __init__(self, body): self.body = body
  def __str__(self): return 'Module %s' % self.body

class ExprList:
  _fields = ['exprs']
  def __init__(self, exprs): self.exprs = exprs
  def __str__(self):
    if not self.exprs: return '{ <Empty> }'
    return '{\n%s\n}' % SimpleElement._strIndent('\n'.join([str(e) for e in self.exprs]))

class Variable:
  _fields = ['name']
  def __init__(self, name): self.name = name
  def __str__(self): return str(self.name)

class Assign:
  _fields = ['target', 'value']
  def __init__(self, target, value): self.target, self.value = target, value
  def __str__(self): return '%s = %s' % (self.target, self.value)

class Class:
  _fields = ['body'] #body should only be variables declarations
  def __init__(self, body): self.body = body
  def __str__(self): return 'Class %s' % self.body

class Function:
  _fields = ['params', 'body']
  def __init__(self, params, body): self.params, self.body = params, body
  def __str__(self): return 'Function%s %s' % (self.params, self.body)

class Params:
  _fields = ['names']
  def __init__(self, names): self.names = names
  def __str__(self): return '(%s)' % ', '.join(str(e) for e in self.names)

class Name:
  _fields = ['id']
  def __init__(self, id): self.id = id
  def __str__(self): return str(self.id)

class Attribute:
  _fields = ['value', 'attr']
  def __init__(self, value, attr): self.value, self.attr = value, attr
  def __str__(self): return '%s.%s' % (self.value, self.attr)

class Return:
  _fields = ['value']
  def __init__(self, value): self.value = value
  def __str__(self): return 'Return %s' % self.value



#for each element of Python, transform it into an element of SIMPLE
#some element should be absent, replaced by other python syntax element
class PythonAst2Simple(ast.NodeTransformer):

  #don't exists in simple elements
  def visit_For(self, node): raise NotExistsException('For')


  def visit_Module(self, node):
    exprList = [self.visit(e) for e in node.body]
    return Module(ExprList(exprList))

  def visit_ClassDef(self, node):
    exprList = [self.visit(e) for e in node.body]
    return Assign(Variable(node.name), Class(ExprList(exprList)))

  def visit_FunctionDef(self, node):
    exprList = [self.visit(e) for e in node.body]
    params = [Name( e.id ) for e in node.args.args]
    return Assign(Variable(node.name), Function(Params(params), ExprList(exprList)))

  def visit_Assign(self, node):
    assert len(node.targets) == 1, 'TODO change function when this raise'
    return Assign(self.visit(node.targets[0]), self.visit(node.value))

  def visit_Attribute(self, node):
    return Attribute(self.visit(node.value), Name(node.attr))

  def visit_Name(self, node): return Name(node.id)

  def visit_Return(self, node): return Return(self.visit(node.value))

  #def visit_Module(self, node):


#ast.copy_location(new_node, old_node)
#ast.fix_missing_locations(node)
#ast.iter_fields(node) => (fieldname, value)
#ast.iter_child_nodes(node) -> [node] directly under it
#ast.walk(node) -> nodes (all of them)

#NodeTransformer.dump(node, annotate_fields=True, include_attributes=False)


#__EOF__

#!/usr/bin/env python

import ast
import astPrint

def parse(code, filename):
  return ASTWrapper(ast.parse(code, filename))

class ASTWrapper:
  def __init__(self, ast, printFunc = astPrint.Print_python):
    self._content = ast
    self._printFunc = printFunc

  def __str__(self): return str(self._printFunc(self._content))

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

class Call:
  _fields = ['func', 'args']
  def __init__(self, func, args): self.func, self.args = func, args
  def __str__(self): return '%s(%s)' % (self.func, ', '.join(str(a) for a in self.args))

class Str:
  _fields = ['s']
  def __init__(self, s): self.s = s
  def __str__(self): return '"%s"' % self.s.replace('"', '\\"').replace('\n', '\\n')

class IfElse:
  _fields = ['test', 'if', 'orelse']
  def __init__(self, test, body, orelse): self.test, self.body, self.orelse = test, body, orelse
  def __str__(self): return 'If(%s) %s else %s' % (self.test, self.body, self.orelse)

class NoneType:
  _fields = []
  def __init__(self): pass
  def __str__(self): return "null"


#for each element of Python, transform it into an element of SIMPLE
#some element should be absent, replaced by other python syntax element
class PythonAst2Simple(ast.NodeTransformer):

  #replace temporaly visit method
  #TODO remove
  def visit(self, node):
    method = 'visit_' + node.__class__.__name__
    try:
      visitor = getattr(self, method)
    except:
      assert False, "Function %s don\'t exists" % method
    return visitor(node)


  #called when we have a body
  def visit_body(self, body):
    if not body: return ExprList([])
    if len(body) == 1 and body[0].__class__.__name__ == "Pass":
      return ExprList([])
    return ExprList([self.visit(e) for e in body])

  #don't exists in simple elements
  def visit_For(self, node): raise NotExistsException('For')
  def visit_Pass(self, node): raise NotExistsException('Pass')

  def visit_Str(self, node): return Str(node.s)

  def visit_Call(self, node):
    assert not node.keywords, 'TODO do keywords arguments'
    assert not node.starargs, 'TODO do starargs arguments'
    assert not node.kwargs, 'TODO do kwargs arguments'

    argList = [self.visit(e) for e in node.args]
    return Call(self.visit(node.func), argList)

  def visit_Import(self, node):
    return Name('import TODO')

  def visit_ImportFrom(self, node):
    return Name('import TODO')

  def visit_Expr(self, node):
    return self.visit(node.value)

  def visit_Module(self, node):
    return Module(self.visit_body(node.body))

  def visit_ClassDef(self, node):
    return Assign(Variable(node.name), Class(self.visit_body(node.body)))

  def visit_FunctionDef(self, node):
    params = [Name( e.id ) for e in node.args.args]
    return Assign(Variable(node.name), Function(Params(params), self.visit_body(node.body)))

  def visit_Assign(self, node):
    assert len(node.targets) == 1, 'TODO change function when this raise'
    return Assign(self.visit(node.targets[0]), self.visit(node.value))

  def visit_Attribute(self, node):
    return Attribute(self.visit(node.value), Name(node.attr))

  def visit_Name(self, node): return Name(node.id)

  def visit_Return(self, node): return Return(self.visit(node.value))
  def visit_If(self, node):
    return IfElse(self.visit(node.test), self.visit_body(node.body), self.visit_body(node.orelse))

  def visit_List(self, node):
    return Call(Name('List'), [self.visit(e) for e in node.elts])

  def visit_Compare(self, node):
    elements = [self.visit(node.left)]
    for o, c in zip(node.ops, node.comparators):
      elements.append(self.visit(c))
      elements.append(self.visit(o))
    return Call(Name("Compare"), elements)

  def visit_NoneType(self, node): return NoneType()

  def visit_Eq(self, e): return  Str('=')
  def visit_NotEq(self, e): return  Str('!=')
  def visit_Lt(self, e): return  Str('<')
  def visit_LtE(self, e): return  Str('<=')
  def visit_Gt(self, e): return  Str('>')
  def visit_GtE(self, e): return  Str('>=')
  def visit_Is(self, e): return  Str('is')
  def visit_IsNot(self, e): return  Str('is not')
  def visit_In(self, e): return  Str('in')
  def visit_NotIn(self, e): return  Str('not in')

  def visit_UnaryOp(self, node):
    return Call(Name("UnaryOp"), [self.visit(node.op), self.visit(node.operand)])

  def visit_Not(self, node): return Str("Not")
  def visit_UAdd(self, node): return Str("+")
  def visit_USub(self, node): return Str("-")
  def visiti_Invert(sel, node): return Str("~")


#ast.copy_location(new_node, old_node)
#ast.fix_missing_locations(node)
#ast.iter_fields(node) => (fieldname, value)
#ast.iter_child_nodes(node) -> [node] directly under it
#ast.walk(node) -> nodes (all of them)

#NodeTransformer.dump(node, annotate_fields=True, include_attributes=False)

class ForIntoWhile(ast.NodeTransformer):

  ##base
  #for a1 in a2:
  #  a3
  #else:
  #  a4

  ##goal test 1
  #aIter = a3.__iter__()
  #aContinue = True
  #try:
  #  a1 = aIter.next()
  #except StopIteration:
  #  aContinue = False
  #
  #while(aContinue):
  #  a4
  #  try:
  #    a1 = aIter.next()
  #  except StopIteration:
  #    Stop = False
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
  ##but where is the a4 one ?

  def visit_For(self, node): pass #TODO fill this








#__EOF__

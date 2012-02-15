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

  def visitWith(self, visitor):
    self._content = visitor.visit(self._content)


class NotExistsException(Exception):
  def __init__(self, name): Exception.__init__(self, 'The element "%s" should not exists'%name)


#TODO create metaclass for SimpleElement
#TODO so it can be like Python ast : _fields, constructor with fields, etc ...


#simple parts
class SimpleElement:
  _fields = []

  def __init__(self, *args, **kargs):
    fields = list(self.__class__._fields)
    try: #simulate args
      for a in args: setattr(self, fields.pop(0), a)
    except IndexError:
      raise TypeError('__init__ takes exacly %s arguments (%s given)' % (len(self._fields), len(args) ))
    try: #simulate kargs
      for k, v in kargs.iteritems():
        fields.remove(k)
        setattr(self, k, v)
    except ValueError:
      raise TypeError("__init__() got an unexpected keyword argument '%s'" % k)
    if fields: #simulate not enough args
      got = len(self._fields) - len(fields)
      raise TypeError('__init__ takes exacly %s arguments (%s given)' % (len(self._fields), got ))

  @staticmethod
  def _strIndent(s): return '\n'.join(['|  '+ss for ss in s.split('\n')])



class PrintElement:
  def __init__(self, content):
    self.content = content

  def ast2str(self, e):
    return getattr(self, 'str_' + e.__class__.__name__, self.classNotFound)(e)

  def classNotFound(self, e):
    print "value not found", 'str_' + e.__class__.__name__,
    return str(e)

  def __str__(self): return self.ast2str(self.content)
  def __call__(self, e): return self.ast2str(e)

  def str_Module(self, e): return 'Module %s' % self(e.body)
  def str_ExprList(self, e):
    if not e.exprs: return '{ <Empty> }'
    return '{\n%s\n}' % SimpleElement._strIndent('\n'.join([self(i) for i in e.exprs]))
  def str_Variable(self, e): return str(e.name)
  def str_Assign(self, e): return '%s = %s' % (self(e.target), self(e.value))
  def str_Class(self, e): return 'Class %s' % self(e.body)
  def str_Function(self, e): return 'Function%s %s' % (self(e.params), self(e.body))
  def str_Params(self, e): return '(%s)' % ', '.join(self(i) for i in e.names)
  def str_Name(self, e): return str(e.id)
  def str_Attribute(self, e): return '%s.%s' % (self(e.value), self(e.attr))
  def str_Return(self, e): return 'Return %s' % self(e.value)
  def str_Call(self, e): return '%s(%s)' % (self(e.func), ', '.join(self(a) for a in e.args))
  def str_Str(self, e): return '"%s"' % e.s.replace('"', '\\"').replace('\n', '\\n')
  def str_IfElse(self, e): return 'If(%s) %s else %s' % (self(e.test), self(e.body), self(e.orelse))
  def str_NoneType(self, e): return "null"
  def str_While(self, e): return 'While(%s) %s' % (self(e.test), self(e.body))
  def str_Num(self, e): return 'Num("%s")' % e.n


class Module(SimpleElement): _fields = ['body'] #the body is always an ExprList
class ExprList(SimpleElement): _fields = ['exprs']
class Variable(SimpleElement): _fields = ['name']
class Assign(SimpleElement): _fields = ['target', 'value']
class Class(SimpleElement): _fields = ['body']
class Function(SimpleElement): _fields = ['params', 'body']
class Params(SimpleElement): _fields = ['names']
class Name(SimpleElement): _fields = ['id']
class Attribute(SimpleElement): _fields = ['value', 'attr']
class Return(SimpleElement): _fields = ['value']
class Call(SimpleElement): _fields = ['func', 'args']
class Str(SimpleElement): _fields = ['s']
class IfElse(SimpleElement): _fields = ['test', 'body', 'orelse']
class NoneType(SimpleElement): _fields = []
class While(SimpleElement): _fields = ['test', 'body']
class Num(SimpleElement): _fields = ['n']


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
  def visit_Num(self, node): return Num(node.n)



  def visit_While(self, node):
    assert not node.orelse
    return While(self.visit(node.test), self.visit_body(node.body))

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

  #binary operators
  def visit_BinOp(self, node):
    return Call(Name("BinaryOp"), [self.visit(node.left), self.visit(node.op), self.visit(node.right)])
  def visit_Add(self, node): return  Str('+')
  def visit_Sub(self, node): return  Str('-')
  def visit_Mult(self, node): return  Str('*')
  def visit_Div(self, node): return  Str('/')
  def visit_Mod(self, node): return  Str('%')
  def visit_Pow(self, node): return  Str('**')
  def visit_LShift(self, node): return  Str('>>')
  def visit_RShift(self, node): return  Str('<<')
  def visit_BitOr(self, node): return  Str('|')
  def visit_BitXor(self, node): return  Str('^')
  def visit_BitAnd(self, node): return  Str('&')
  def visit_FloorDiv(self, node): return  Str('//')

  def visit_Subscript(self, node):
    sliceValue = []
    if isinstance(node.slice, ast.Index):
      sliceValue = [Str("Index"), self.visit(node.slice.value)]
    else : assert False, 'Subscript content not known : %s' % node.slice

    return Call(Name("Subscript"), [self.visit(node.value)] + sliceValue)
  def visit_Index(self, node): assert False, "should not be visited"


#ast.copy_location(new_node, old_node)
#ast.fix_missing_locations(node)
#ast.iter_fields(node) => (fieldname, value)
#ast.iter_child_nodes(node) -> [node] directly under it
#ast.walk(node) -> nodes (all of them)

#NodeTransformer.dump(node, annotate_fields=True, include_attributes=False)

class TrySimplify(ast.NodeTransformer):
  pass



class WhileRemoveElse(ast.NodeTransformer):

  def geneVariable(self):
    if not hasattr(self, 'varNum'): self.varNum = 0
    self.varNum += 1
    return 'genVar_%s_%s' % (self.__class__.__name__, self.varNum)

  #while a1:
  #  a2
  #else:
  #  a3

  ##maybe 1
  #genVar = a1
  #if genVar:
  #  while genVar:
  #    a2
  #    genVar = a1
  #else:
  #  a3

  ##maybe 2
  #genVar = True
  #while a1
  #  genVar = False
  #  a2
  #if genVar:
  #  a3

  def visit_While(self, node):
    if not node.orelse : return node
    assert False, 'TODO while remove else'

  def visit_For(self, node):
    assert False, "This visitor must be after ForIntoWhile"

#__EOF__

#!/usr/bin/env python
import ast
from simple.simple import *
from transform.nodeTransformer import NodeTransformer
from all2all.simple.simple import AST as S_AST

class NotExistsException(Exception):
    def __init__(self, name): Exception.__init__(self, 'The element "%s" should not exists'%name)


#for each element of Python, transform it into an element of SIMPLE
#some element should be absent, replaced by other python syntax element
class PythonAst2Simple(object): #it's its own transformer

  #replace temporaly visit method
  #TODO remove
  def visit(self, node):
      method = 'visit_' + node.__class__.__name__
      assert hasattr(self, method), "Function %s don't exists" % method
      return getattr(self, method)(node)

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

  def visit_Eq(self, e): return    Str('=')
  def visit_NotEq(self, e): return    Str('!=')
  def visit_Lt(self, e): return    Str('<')
  def visit_LtE(self, e): return    Str('<=')
  def visit_Gt(self, e): return    Str('>')
  def visit_GtE(self, e): return    Str('>=')
  def visit_Is(self, e): return    Str('is')
  def visit_IsNot(self, e): return    Str('is not')
  def visit_In(self, e): return    Str('in')
  def visit_NotIn(self, e): return    Str('not in')

  def visit_UnaryOp(self, node):
      return Call(Name("UnaryOp"), [self.visit(node.op), self.visit(node.operand)])

  def visit_Not(self, node): return Str("Not")
  def visit_UAdd(self, node): return Str("+")
  def visit_USub(self, node): return Str("-")
  def visiti_Invert(sel, node): return Str("~")

  #binary operators
  def visit_BinOp(self, node):
      return Call(Name("BinaryOp"), [self.visit(node.left), self.visit(node.op), self.visit(node.right)])
  def visit_Add(self, node): return    Str('+')
  def visit_Sub(self, node): return    Str('-')
  def visit_Mult(self, node): return    Str('*')
  def visit_Div(self, node): return    Str('/')
  def visit_Mod(self, node): return    Str('%')
  def visit_Pow(self, node): return    Str('**')
  def visit_LShift(self, node): return    Str('>>')
  def visit_RShift(self, node): return    Str('<<')
  def visit_BitOr(self, node): return    Str('|')
  def visit_BitXor(self, node): return    Str('^')
  def visit_BitAnd(self, node): return    Str('&')
  def visit_FloorDiv(self, node): return    Str('//')

  def visit_Subscript(self, node):
      sliceValue = []
      if isinstance(node.slice, ast.Index):
          sliceValue = [Str("Index"), self.visit(node.slice.value)]
      else : assert False, 'Subscript content not known : %s' % node.slice

      return Call(Name("Subscript"), [self.visit(node.value)] + sliceValue)
  def visit_Index(self, node): assert False, "should not be visited"


#__EOF__

#!/usr/bin/env python
# Define the element of the simple AST
# define too the walker of the simple AST
#

#simple parts
class AST:
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

class Module(AST): _fields = ['body'] #the body is always an ExprList
class ExprList(AST): _fields = ['exprs']
class Variable(AST): _fields = ['name']
class Assign(AST): _fields = ['target', 'value']
class Class(AST): _fields = ['body']
class Function(AST): _fields = ['params', 'body']
class Params(AST): _fields = ['names']
class Name(AST): _fields = ['id']
class Attribute(AST): _fields = ['value', 'attr']
class Return(AST): _fields = ['value']
class Call(AST): _fields = ['func', 'args']
class Str(AST): _fields = ['s']
class IfElse(AST): _fields = ['test', 'body', 'orelse']
class NoneType(AST): _fields = []
class Break(AST): _fields = []
class Raise(AST): _fields = []
class Continue(AST): _fields = []
class While(AST): _fields = ['test', 'body']
class Num(AST): _fields = ['n']
class TryCatchFinally(AST): _fields = ['body', 'errName', 'catch', 'final']




def dumpSimple(node): return str(SimpleDump(node))

class SimpleDump:
    def __init__(self, content):
        self.content = content

    @staticmethod
    def _strIndent(s): return '\n'.join(['|  '+ss for ss in s.split('\n')])

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
        return '{\n%s\n}' % SimpleDump._strIndent('\n'.join([self(i) for i in e.exprs]))
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
    def str_TryCatchFinally(self, e):
      return 'try %s catch_error %s %s finally %s' % (
          self(e.body), self(e.errName),
          self(e.catch), self(e.final)
      )

    def str_Break(self, e): return '%Break%'
    def str_Raise(self, e): return '%Raise% ???'
    def str_Continue(self, e): return '%Continue%'



def dumpJson(node): return JsonDump([node]).get()


class JsonDump:

  def __init__(self, node):
    self.content = node

  def get(self): return self.visit(self.content)

  def visit(self, node):
    if not isinstance(node, AST):
      return self._specific_visit(node)
    return self.generic_visit(node)

  def _specific_visit(self, node):
    if node is None: return 'None'
    if isinstance(node, str): return node
    if isinstance(node, int): return node
    if hasattr(node, '__iter__'):
      return [self.visit(n) for n in node]
    raise Exception('node type not known %s for element %s' % (node.__class__, node))

  def generic_visit(self, node):
    assert isinstance(node, AST)
    res = {}
    for f in node._fields:
      res[f] = self.visit(getattr(node, f))
    res['__class__'] = node.__class__.__name__
    return res



#declare a node transformer for inheritance
class NodeTransformer(object):

  #when visiting node, group collection of statement
  #used for the "body" "orelse" and stuffs like that groups
  def visitList(self, nodeList):
    res = []
    for node in nodeList:
      tmpRes = self.visit(node)
      if isinstance(tmpRes, ast.AST):
          res.append(tmpRes)
      elif hasattr(tmpRes, '__iter__'): #because changing node can return list
          res += tmpRes
      else:
          raise Exception("bad node type, waiting for list or node")
    return res


  #redefined this because of the list no-taken into account
  def visit(self, node):
    #usual case first
    if isinstance(node, AST):
      nodeName = 'visit_' + node.__class__.__name__
      if hasattr(self, nodeName):
          return getattr(self, nodeName)(node)
      else:
          return self.generic_visit(node)

    #special cases
    if node is None : return node
    if isinstance(node, str): return node
    if isinstance(node, int): return node
    if hasattr(node, '__iter__'): return self.visitList(node)

    assert False

  def generic_visit(self, node):
    if isinstance(node, AST):
      for f in node._fields:
          attr = getattr(node, f)
          attr = self.visit(attr)
          setattr(node, f, attr)
      return node
    elif isinstance(node, str):
      return node




#__EOF__

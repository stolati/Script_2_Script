
from script2script.simple.simple import *

def simple2javascript(simpleAst):
  return str(Simple2Javascript(simpleAst))

#class Module(AST): _fields = ['body'] #the body is always an ExprList
#class ExprList(AST): _fields = ['exprs']
#class Class(AST): _fields = ['body']
#class Function(AST): _fields = ['params', 'body']
#class Params(AST): _fields = ['names']
#class Name(AST): _fields = ['id']
#class Attribute(AST): _fields = ['value', 'attr']
#class Return(AST): _fields = ['value']
#class Call(AST): _fields = ['func', 'args']
#class Str(AST): _fields = ['s']
#class IfElse(AST): _fields = ['test', 'body', 'orelse']
#class NoneType(AST): _fields = []
#class Break(AST): _fields = []
#class Raise(AST): _fields = []
#class Continue(AST): _fields = []
#class While(AST): _fields = ['test', 'body']
#class Num(AST): _fields = ['n']
#class TryCatchFinally(AST): _fields = ['body', 'errName', 'catch', 'final']


class Simple2Javascript(object):
  basic_library = """
//basic_lib_begin
True = true;
False = false;
None = null;
Print = function(e){ print(str(e)); };
str = function(e){
  if(e === None) return 'None';
  if(typeof e === 'string') return "'" + e + "'";
  if(typeof e === 'number') return ''+e;
  if(hasattr(e, '__str__')) return getattr(e, '__str__')();
  if(hasattr(e, '__repr__')) return getattr(e, '__repr__')();
  print(typeof e);

  return '';
}
min = function(m1, m2){ m1 > m2 ? m2 : m1 ; };
max = function(m1, m2){ m1 > m2 ? m1 : m2 ; };
BinaryOp = function(left, op, right){
  switch(op){
    case "+": return left+right ; break;
    case "-": return left-right ; break;
    case "*": return left*right ; break;
    case "/": return left/right ; break;
  }
  throw new Object("assertion false");
};
Compare = function(left, right, op){
  switch(op){
    case ">": return left > right ; break;
    case "<": return left < right ; break;
    case ">=": return left >= right ; break;
    case "<=": return left <= right ; break;
    case "=": return left == right ; break;
    case "!=": return left != right ; break;
  }
  throw new Object("assertion false");
};
UnaryOp = function(op, cmd){
  switch(op){
    case "Not": return (! cmd) ; break;
  }
  throw new Object("assertion false");
};
AttributeError = function(){};
getattr = function(ob, name){
  //TODO test for the __getattr__ stuff
  if(typeof ob[name] === 'undefined')
    throw new AttributeError();
  if(typeof ob[name] === 'function')
    return function(){ return ob[name].apply(ob, arguments) ;}
  return ob[name];
};
hasattr = function(ob, name){
  try{
    getattr(ob, name)
    return True;
  } catch(error) {
    if(error instanceof AttributeError){
      return False;
    }
    throw error;
  }
}

list = function(){
  return [];
}

if(typeof Array.prototype.append !== 'function'){
  Array.prototype.append = Array.prototype.push;
}
if(typeof Array.prototype.__str__ !== 'function'){
  Array.prototype.__str__ = function(x){
    myClone = [];
    for(var i = 0; i < this.length; i++)
      myClone[i] = str(this[i]);
    return "[" + myClone.join(", ") + "]";
  };
}
if(typeof Array.prototype.extend !== 'function'){
  Array.prototype.extend = function(L){
    for(var i = 0; i < L.length ; i++)
      this.append(L[i]);
    return None;
  };
}
if(typeof Array.prototype.__getitem__ !== 'function'){
  Array.prototype.__getitem__ = function(i){
    return this[i];
  };
}
if(typeof Array.prototype.__setitem__ !== 'function'){
  Array.prototype.__setitem__ = function(i, x){
    this[i] = x;
  };
}

//delete list[1];
//basic_lib_end
  """

  def __init__(self, content):
    self.content = content
    self.indent_str = '  '

  def bodyIndent(self, body): #return a body in an indented form
    if not body : return []
    return [self.indent_str + ss for ss in '\n'.join([self(e) for e in body]).split('\n')]

  def indentStr(self, s): #return the same string, indented
    return '\n'.join([self.indent_str + ss for ss in s.split('\n')])

  def ast2str(self, e):
    #get the class name and use it for calling function
    return getattr(self, 'str_' + e.__class__.__name__, self.classNotFound)(e)

  def classNotFound(self, e):
    if hasattr(e, '_fields'): return '%s%s' % (e, repr(e._fields))
    if hasattr(e, '__iter__'): return '%s(is a list)' % (e)
    if e is None: return ""
    return str(e)

  def __call__(self, e): return self.ast2str(e) #for one time change
  def __str__(self): return self.basic_library + self(self.content)


  ##########################
  # named functions
  ##########################

  def str_Module(self, e):
    comment = 20 * '//' + '\n'
    moduleHeader = '\n%s// Module\n%s\n' % (comment, comment)
    bodyStr = self(e.body) # ''.join([self(e)+'\n' for e in e.body])
    return moduleHeader + '\n{\n%s\n}\n' % self.indentStr(bodyStr)

  def str_ExprList(self, e):
    return ''.join(self(n) + ';\n' for n in e.exprs)

  def str_Call(self, e):
    arguments = ', '.join([self(a) for a in e.args])
    return '%s(%s)' % (self(e.func), arguments)

  def str_Name(self, e):
    return e.id

  def str_Str(self, e):
    res = e.s
    replace = [('"', '\\"'), ("\n", "\\n"), ("\t", "\\t")]
    for a, b in replace : res = res.replace(a, b)
    return '"%s"' % res

  def str_Assign(self, e):
    #test if the target is an Attribute
    if isinstance(e.target, Attribute):
       return '%s.%s = %s' % (self(e.target.value), self(e.target.attr), self(e.value))

    return '%s = %s' % ( self(e.target), self(e.value) )

  def str_Num(self, e): return str(e.n)

  def str_IfElse(self, e):
    test = self(e.test)
    body = self.indentStr(self(e.body))
    hasElse = len(e.orelse.exprs) != 0
    if hasElse:
      orelse = self.indentStr(self(e.orelse))
      return "if(%s){\n%s\n} else {\n%s\n}\n" % (test, body, orelse)
    else:
      return "if(%s){\n%s\n}\n" % (test, body)

  def str_While(self, e):
    test = self(e.test)
    body = self.indentStr(self(e.body))
    return "while(%s){\n%s\n}\n" % (test, body)

  def str_Variable(self, e):
    return e.name

  def str_Function(self, e):
    res = 'function(%s){\n%s\n}' % (self(e.params), self.indentStr(self(e.body)) )
    return res

  def str_Params(self, e):
    return ', '.join(self(n) for n in e.names)

  def str_Return(self, e):
    return 'return %s' % self(e.value)

  def str_Class(self, e): #TODO modify before calling this one, a transformer special for that
    def removeSelf(f): #get a Function, and remove the self (adding first self = this)
      assert isinstance(f, Function)
      assert f.params.names[0].id == 'self', 'is %s instead of self' % f.params.names[0]

      param_names = f.params.names[1:]
      body_expr = [Assign(Variable('self'), Name('this'))] + f.body.exprs
      return Function(Params(param_names), ExprList(body_expr))

    init = None
    #searching for the __init__ function
    functions = {}
    for a in e.body.exprs: #should be assign = Function
      assert isinstance(a, Assign)
      assert isinstance(a.target, Variable)
      assert isinstance(a.value, Function)

      if a.target.name == '__init__':
        init = a.value
      else:
        functions[a.target.name] = a.value

    if init is None:
      init = Function(Params([Name('self')]), ExprList([]))

    #remove self from the __init__ stuff
    init.params.names.pop(0)

    params = self(init.params)

    body = []

    #init of the object
    body.append('self = new Object();')

    body.append( self(init.body) ) #add the __init__ content

    for k, v in functions.iteritems():
      f = removeSelf(v)
      body.append( 'self.%s = %s;' % (k, self(f)) )


    body.append('return self;')

    return 'function(%s){\n%s\n}' % (params, self.indentStr('\n'.join(body)))


  def str_Attribute(self, e):
    return 'getattr(%s, "%s")' % (self(e.value), self(e.attr))


#    def str_ClassDef(self, e):
#        res = [self(d) for d in e.decorator_list]
#        bases = ', '.join([self(b) for b in e.bases])
#        res.append('class %s%s:' %(e.name, bases and '(%s)' % bases))
#        res += self.bodyIndent(e.body)
#        return '\n'.join(res)
#
#    def str_arguments(self, e):
#        res = []
#        args, defaults = list(e.args), list(e.defaults)
#
#        args.reverse(), defaults.reverse()
#        defaults += [None] * len(args)
#        for a, d in zip(args, defaults):
#            if d: res.append('%s = %s' % (self(a), self(d)))
#            else: res.append(self(a))
#        res.reverse()
#
#        if e.vararg : res.append('*'+r(e.vararg))
#        if e.kwarg : res.append('**'+r(e.kwarg))
#        return '('+', '.join(res)+')'

#    def str_Return(self, e): return 'return %s' % self(e.value)
#    def str_Attribute(self, e): return '%s.%s' % (self(e.value), e.attr)
#    def str_Import(self, e):
#        return '\n'.join('import %s' % self(e) for e in e.names)
#    def str_alias(self, e):
#        return (e.asname and '{n} as {a}' or '{n}').format(n=e.name, a=e.asname)
#    def str_Expr(self, e): return self(e.value)
#    def str_Pass(self, e): return 'pass'
#    def str_Break(self, e): return 'Break'
#    def str_Continue(self, e): return 'Continue'
#    def str_ImportFrom(self, e):
#        return 'from %s import %s' % (e.module, ', '.join(self(e) for e in e.names) )
#
#    def str_Raise(self, e):
#        #return print_simple(e) #don't work, why that ? I don't know
#        #TODO test the raise stuff, and print a more complex one
#        return 'Raise ???'
#
#    def str_TryFinally(self, e):
#        res = ['try:']
#        res += self.bodyIndent(e.body)
#        res += ['finally:']
#        res += self.bodyIndent(e.finalbody)
#        return '\n'.join(res)
#
#    def str_TryExcept(self, e):
#        res = ['try:']
#        res += self.bodyIndent(e.body)
#        res += [self(h) for h in e.handlers]
#        orelse = self.bodyIndent(e.orelse)
#        res += orelse and ['else:'] + orelse or []
#        return '\n'.join(res)
#
#    def str_ExceptHandler(self, e):
#        name = e.name and self(e.name) or ''
#        typeStr = e.type and self(e.type) or ''
#        res = ['except:']
#        if typeStr: res = ['except %s:' % typeStr]
#        if name and typeStr: res = ['except %s as %s:' %(typeStr, name)]
#        res += self.bodyIndent(e.body)
#        return '\n'.join(res)
#
#    def str_AugAssign(self, e):
#        return '%s %s= %s' %(self(e.target), self(e.op), self(e.value))
#    def str_Delete(self, e):
#        return 'del %s' %(', '.join(self(e) for e in e.targets))
#    def str_Global(self, e):
#        return 'global ' + ', '.join(self(e) for e in e.names)
#
#    #slices and index
#    def str_Subscript(self, e): return self(e.value) + '['+ self(e.slice) + ']'
#    def str_Index(self, e): return self(e.value)
#    def str_Slice(self, e):
#        step = {None:''}.get(e.step, self(e.step))
#        return self(e.lower)+':'+self(e.upper) + step
#
#    #base types
#    def str_List(self, e): return '[%s,]' % ', '.join(self(e) for e in e.elts)
#    def str_Tuple(self, e): return '(%s,)' % ', '.join(self(e) for e in e.elts)
#    def str_Dict(self, e): return '{%s}' %    ', '.join(self(e1) + ':' + self(e2) for e1, e2 in zip(e.keys, e.values))
#
#    #boolean operators
#    def str_BoolOp(self, e):
#        return    (' %s ' % self(e.op)).join(self(e) for e in e.values)
#    def str_Or(self, e): return 'or'
#    def str_And(self, e): return 'and'
#
#
#    #binary operators
#    def str_BinOp(self, e):
#        return    '%s %s %s' % (self(e.left), self(e.op), self(e.right))
#    def str_Add(self, e): return '+'
#    def str_Sub(self, e): return '-'
#    def str_Mult(self, e): return '*'
#    def str_Div(self, e): return '/'
#    def str_Mod(self, e): return '%'
#    def str_Pow(self, e): return '**'
#    def str_LShift(self, e): return '>>'
#    def str_RShift(self, e): return '<<'
#    def str_BitOr(self, e): return '|'
#    def str_BitXor(self, e): return '^'
#    def str_BitAnd(self, e): return '&'
#    def str_FloorDiv(self, e): return '//'
#
#    #comparaison operators
#    def str_Compare(self, e):
#        res = self(e.left) + ' '
#        res += ' '.join(self(o) + ' ' + self(c) for o, c in zip(e.ops, e.comparators))
#        return    res
#    def str_Eq(self, e): return '='
#    def str_NotEq(self, e): return '!='
#    def str_Lt(self, e): return '<'
#    def str_LtE(self, e): return '<='
#    def str_Gt(self, e): return '>'
#    def str_GtE(self, e): return '>='
#    def str_Is(self, e): return 'is'
#    def str_IsNot(self, e): return 'is not'
#    def str_In(self, e): return 'in'
#    def str_NotIn(self, e): return 'not in'
#
#    #unary operators
#    def str_UnaryOp(self, e): return '%s %s' % (self(e.op), self(e.operand))
#    def str_Not(self, e): return 'not'
#    def str_UAdd(self, e): return '+'
#    def str_USub(self, e): return '-'
#    def str_Invert(self, e): return '~'
#
#__EOF__

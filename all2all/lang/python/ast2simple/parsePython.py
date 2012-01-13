#!/usr/bin/env python

import ast

def parse(code, filename):
  return py_ast_print_python(ast.parse(code, filename))


class ASTWrapper:
  def __init__(self, ast):
    self._content = ast
    self._level = 0 #level for the indentation


  def __str__(self):
    return self.__toStr(self._content, 0)

  def __toStr(self, content, indent):
    if isinstance(content, ast.Module):
      print "is Module"
      print content._fields
      print dir(content)
    else:
      print "not known"
      print content
      print content._fields
    print content

    return "toto"


#try to do the printing in the original format
def py_ast_print_python(content, level=0):
  indent, indentNext = level * '  ', (level+1)* '  '
  passing = indentNext + 'pass\n'
  r = lambda e : py_ast_print_python(e, level)
  rplus = lambda e : py_ast_print_python(e, level+1)
  rzero = lambda e : py_ast_print_python(e, 0)

  if isinstance(content, ast.Module):
    moduleHeader = '{indent}{comment}\n{indent}# Module\n{indent}{comment}\n\n'.format(indent=indent, comment=20*'#')
    bodyStr =''.join([r(e)+'\n' for e in content.body])
    return moduleHeader + bodyStr

  if isinstance(content, ast.ClassDef):
    deco = ''.join([r(e) for e in content.decorator_list])
    bases = ', '.join([rzero(e) for e in content.bases])
    if bases : bases = '(%s)' % bases
    declaration = 'class ' + content.name + bases + ':\n'
    bodyStr = ''.join([rplus(e)+'\n' for e in content.body]) or passing
    return deco + declaration + bodyStr

  if isinstance(content, ast.FunctionDef):
    deco = ''.join([r(e) for e in content.decorator_list])
    args = rzero(content.args)+':\n'
    body = ''.join([rplus(e)+'\n' for e in content.body]) or passing
    return deco + indent + 'def ' + content.name + args + body

  if isinstance(content, ast.arguments):
    res = []
    args, defaults = content.args, content.defaults

    args.reverse(), defaults.reverse()
    defaults += [None] * len(args)
    for a, d in zip(args, defaults):
      if d: res.append('%s = %s' % (rzero(a), rzero(d)))
      else: res.append(rzero(a))
    res.reverse()

    if content.vararg : res.append('*'+r(content.vararg))
    if content.kwarg : res.append('**'+r(content.kwarg))
    return '('+', '.join(res)+')'



  if isinstance(content, ast.Name): return content.id
  if isinstance(content, ast.Return): return indent + 'return ' + rzero(content.value)
  if isinstance(content, ast.Attribute): return indent + '%s.%s' % (rzero(content.value), content.attr)
  if isinstance(content, ast.Assign): return indent + '%s = %s' % ( ', '.join(rzero(e) for e in content.targets), rzero(content.value))
  if isinstance(content, ast.Import):
    return '\n'.join('%simport %s' % (indent, rzero(e)) for e in content.names)
  if isinstance(content, ast.alias):
    return (content.asname and '{n} as {a}' or '{n}').format(n=content.name, a=content.asname)
  if isinstance(content, ast.Expr): return indent + rzero(content.value)
  if isinstance(content, ast.Call):
    res = [rzero(a) for a in content.args]
    res += [rzero(a) for a in content.keywords]
    res += ['*' + rzero(a) for a in content.starargs or []] #TODO
    res += ['**' + rzero(a) for a in content.kwargs or []] #TODO
    return '%s(%s)' % (rzero(content.func), ', '.join(res))
  if isinstance(content, ast.Pass): return passing
  if isinstance(content, ast.ImportFrom):
    return indent + 'from %s import %s' % (content.module, ', '.join(rzero(e) for e in content.names) )


  if isinstance(content, ast.If):
    test = rzero(content.test)
    body = ''.join(rplus(e)+'\n' for e in content.body)
    orelse = ''.join(rplus(e)+'\n' for e in content.orelse)
    ifstr = '%sif %s:\n%s' % (indent, test, body)
    elsestr = orelse and '%selse:\n%s' % (indent, orelse) or ''
    return ifstr + elsestr
  if isinstance(content, ast.While):
    test = rzero(content.test)
    body = ''.join(rplus(e)+'\n' for e in content.body)
    orelse = ''.join(rplus(e)+'\n' for e in content.orelse)
    ifstr = '%swhile %s:\n%s' % (indent, test, body)
    elsestr = orelse and '%selse:\n%s' % (indent, orelse) or ''
    return ifstr + elsestr
  if isinstance(content, ast.For):
    target = rzero(content.target)
    iterStr = rzero(content.iter)
    body = ''.join(rplus(e)+'\n' for e in content.body)
    orelse = ''.join(rplus(e)+'\n' for e in content.orelse)
    elseStr = orelse and '%selse:\n%s' % (indent, orelse) or ''
    return indent + 'for %s in %s:\n%s' % (target, iterStr, body) + elseStr
  if isinstance(content, ast.TryExcept):
    body = ''.join(rplus(e)+'\n' for e in content.body)
    handlers = ''.join(r(e)+'\n' for e in content.handlers)
    body = ''.join(rplus(e)+'\n' for e in content.body)
    orelse = ''.join(rplus(e)+'\n' for e in content.orelse)
    return indent + 'try:\n' + body + handlers + orelse
  if isinstance(content, ast.ExceptHandler):
    body = ''.join(rplus(e)+'\n' for e in content.body)
    name = content.name and rzero(content.name) or ''
    typeStr = content.type and rzero(content.type) or ''
    if name and typeStr: return indent + 'except %s as %s:\n%s' %(typeStr, name, body)
    if typeStr: return indent + 'except %s:\n%s' %(typeStr, body)
    return indent + 'except:\n%s' %(body)

  if isinstance(content, ast.AugAssign):
    return indent + '%s %s= %s' %(rzero(content.target), rzero(content.op), rzero(content.value))
  if isinstance(content, ast.Delete):
    return indent + 'del %s' %(', '.join(rzero(e) for e in content.targets))
  if isinstance(content, ast.Global):
    return indent + 'global ' + ', '.join(rzero(e) for e in content.names)

  if isinstance(content, ast.Print):
    dest = content.dest and rzero(content.dest) +', ' or ''
    values = ', '.join(rzero(e) for e in content.values)
    nl = (not content.nl) and ',' or ''
    return indent + 'print %s' % dest+ values +nl




  #slices and index
  if isinstance(content, ast.Subscript): return indent+ rzero(content.value) + '['+ rzero(content.slice) + ']'
  if isinstance(content, ast.Index): return indent+rzero(content.value)
  if isinstance(content, ast.Slice):
    step = {None:''}.get(content.step, rzero(content.step))
    return indent+rzero(content.lower)+':'+rzero(content.upper) + step

  #base types
  if isinstance(content, ast.Num): return indent + str(content.n)
  if isinstance(content, ast.Str):
    res = content.s
    replace = [('"', '\\"'), ("\n", "\\n"), ("\t", "\\t")]
    for a, b in replace : res = res.replace(a, b)
    return '"%s"' % res
  if isinstance(content, ast.List): return indent+'[%s]' % ', '.join(rzero(e) for e in content.elts)
  if isinstance(content, ast.Tuple): return indent+'(%s)' % ', '.join(rzero(e) for e in content.elts)
  if isinstance(content, ast.Dict): return indent+'{%s}' %  ', '.join(rzero(e1) + ':' + rzero(e2) for e1, e2 in zip(content.keys, content.values))

  #boolean operators
  if isinstance(content, ast.BoolOp):
    return indent+ (' %s ' % rzero(content.op)).join(rzero(e) for e in content.values)
  if isinstance(content, ast.Or): return indent+'or'
  if isinstance(content, ast.And): return indent+'and'


  #binary operators
  if isinstance(content, ast.BinOp):
    return indent + '%s %s %s' % (rzero(content.left), rzero(content.op), rzero(content.right))
  if isinstance(content, ast.Add): return indent + '+'
  if isinstance(content, ast.Sub): return indent + '-'
  if isinstance(content, ast.Mult): return indent + '*'
  if isinstance(content, ast.Div): return indent + '/'
  if isinstance(content, ast.Mod): return indent + '%'
  if isinstance(content, ast.Pow): return indent + '**'
  if isinstance(content, ast.LShift): return indent + '>>'
  if isinstance(content, ast.RShift): return indent + '<<'
  if isinstance(content, ast.BitOr): return indent + '|'
  if isinstance(content, ast.BitXor): return indent + '^'
  if isinstance(content, ast.BitAnd): return indent + '&'
  if isinstance(content, ast.FloorDiv): return indent + '//'

  #comparaison operators
  if isinstance(content, ast.Compare):
    res = rzero(content.left) + ' '
    res += ' '.join(rzero(o) + ' ' + rzero(c) for o, c in zip(content.ops, content.comparators))
    return indent + res
  if isinstance(content, ast.Eq): return indent + '='
  if isinstance(content, ast.NotEq): return indent + '!='
  if isinstance(content, ast.Lt): return indent + '<'
  if isinstance(content, ast.LtE): return indent + '<='
  if isinstance(content, ast.Gt): return indent + '>'
  if isinstance(content, ast.GtE): return indent + '>='
  if isinstance(content, ast.Is): return indent + 'is'
  if isinstance(content, ast.IsNot): return indent + 'is not'
  if isinstance(content, ast.In): return indent + 'in'
  if isinstance(content, ast.NotIn): return indent + 'not in'

  #unary operators
  if isinstance(content, ast.UnaryOp): return indent +'%s %s' % (rzero(content.op), rzero(content.operand))
  if isinstance(content, ast.Not): return indent + 'not'
  if isinstance(content, ast.UAdd): return indent + '+'
  if isinstance(content, ast.USub): return indent + '-'
  if isinstance(content, ast.Invert): return indent + '~'

  #dev else case
  if hasattr(content, '_fields'): return '%s%s' % (content, repr(content._fields))
  if hasattr(content, '__iter__'): return '%s(is a list)' % (content)
  return str(content)


def py_ast_print_simple(content):
  res = []
  if hasattr(content, '_fields'):
    for f in content._fields:
      res.append(ASTSimpleToString(getattr(content, f)))
  elif hasattr(content, '__iter__'):
    for e in content:
      res.append(ASTSimpleToString(e))
  else:
    return str(content)

  name = content.__class__.__name__
  return '%s(%s)' % (name, ', '.join(res))



def py_ast_print_indented(content, level=1):
  indent = level * '|  '
  name = content.__class__.__name__

  if hasattr(content, '_fields'): #if element from Module
    if len(content._fields) == 0: return name + '()'
    res = name + '(\n'
    for attrName in content._fields:
      attrValue = ASTIndentToString(getattr(content, attrName), level+1)
      res += '{indent}{attrName}={attrValue},\n'.format(**locals())
    return res + indent + ')'

  if hasattr(content, '__iter__'): #if it's a list
    if len(content) == 0: return '[]'
    res = '[\n'
    for e in content:
      value = ASTIndentToString(e, level+1)
      res += '{indent}{value},\n'.format(**locals())
    return res + indent + ']'

  return '"' + str(content) + '"'


#__EOF__

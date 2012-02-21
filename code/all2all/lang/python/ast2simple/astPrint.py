#!/usr/bin/env python

#this module give some ways to print an ast module
import ast

class Print_python:
    def __init__(self, content):
        self.content = content
        self.indent_str = '|  '

    def indentStr(self, s): #return the same string, indented
        return '\n'.join([self.indent_str + ss for ss in s.split('\n')])

    def bodyIndent(self, body): #return a body in an indented form
        if not body : return []
        return [self.indent_str + ss for ss in '\n'.join([self(e) for e in body]).split('\n')]

    def ast2str(self, e):
        #TODO remove line, temporaly use this trick before we have true Simple
        if e.__class__.__str__ != object.__str__: return str(e)
        #get the class name and use it for calling function
        return getattr(self, 'str_' + e.__class__.__name__, self.classNotFound)(e)

    def classNotFound(self, e):
        if hasattr(e, '_fields'): return '%s%s' % (e, repr(e._fields))
        if hasattr(e, '__iter__'): return '%s(is a list)' % (e)
        return str(e)

    def __call__(self, e): return self.ast2str(e) #for one time change
    def __str__(self): return self(self.content)

    ##########################
    # named functions
    ##########################

    def str_Module(self, e):
        comment = 20 * '#' + '\n'
        moduleHeader = '%s# Module\n%s\n' % (comment, comment)
        bodyStr = ''.join([self(e)+'\n' for e in e.body])
        return moduleHeader + bodyStr

    def str_ClassDef(self, e):
        res = [self(d) for d in e.decorator_list]
        bases = ', '.join([self(b) for b in e.bases])
        res.append('class %s%s:' %(e.name, bases and '(%s)' % bases))
        res += self.bodyIndent(e.body)
        return '\n'.join(res)

    def str_FunctionDef(self, e):
        res = [self(e) for e in e.decorator_list]
        res.append('def %s%s:' % (e.name, self(e.args)))
        res += self.bodyIndent(e.body)
        return '\n'.join(res)

    def str_arguments(self, e):
        res = []
        args, defaults = list(e.args), list(e.defaults)

        args.reverse(), defaults.reverse()
        defaults += [None] * len(args)
        for a, d in zip(args, defaults):
            if d: res.append('%s = %s' % (self(a), self(d)))
            else: res.append(self(a))
        res.reverse()

        if e.vararg : res.append('*'+r(e.vararg))
        if e.kwarg : res.append('**'+r(e.kwarg))
        return '('+', '.join(res)+')'

    def str_Name(self, e):
        #forced test for my knowledge
        assert e.ctx.__class__ not in [ast.AugLoad, ast.AugStore]
        return e.id
    def str_Return(self, e): return 'return %s' % self(e.value)
    def str_Attribute(self, e): return '%s.%s' % (self(e.value), e.attr)
    def str_Assign(self, e):
        if isinstance(e.targets, ast.Tuple) or isinstance(e.targets, ast.List):
            return '%s = %s' % (self(e.targets), self(e.value))
        return '%s = %s' % ( ' = '.join(self(e) for e in e.targets), self(e.value))
    def str_Import(self, e):
        return '\n'.join('import %s' % self(e) for e in e.names)
    def str_alias(self, e):
        return (e.asname and '{n} as {a}' or '{n}').format(n=e.name, a=e.asname)
    def str_Expr(self, e): return self(e.value)
    def str_Call(self, e):
        res = [self(a) for a in e.args]
        res += [self(a) for a in e.keywords]
        res += ['*' + self(a) for a in e.starargs or []] #TODO
        res += ['**' + self(a) for a in e.kwargs or []] #TODO
        return '%s(%s)' % (self(e.func), ', '.join(res))
    def str_Pass(self, e): return 'pass'
    def str_Break(self, e): return 'Break'
    def str_Continue(self, e): return 'Continue'
    def str_ImportFrom(self, e):
        return 'from %s import %s' % (e.module, ', '.join(self(e) for e in e.names) )


    def str_If(self, e):
        res = ['if %s:' % self(e.test)]
        res += self.bodyIndent(e.body)
        orelse = self.bodyIndent(e.orelse)
        res += orelse and ['else:'] + orelse or []
        return '\n'.join(res)
    def str_While(self, e):
        res = ['while %s:' % self(e.test)]
        res += self.bodyIndent(e.body)
        orelse = self.bodyIndent(e.orelse)
        res += orelse and ['else:'] + orelse or []
        return '\n'.join(res)
    def str_For(self, e):
        res = ['for %s in %s:' % (self(e.target), self(e.iter))]
        res += self.bodyIndent(e.body)
        orelse = self.bodyIndent(e.orelse)
        res += orelse and ['else:'] + orelse or []
        return '\n'.join(res)
    def str_TryExcept(self, e):
        res = ['try:']
        res += self.bodyIndent(e.body)
        res += [self(h) for h in e.handlers]
        orelse = self.bodyIndent(e.orelse)
        res += orelse and ['else:'] + orelse or []
        return '\n'.join(res)
    def str_ExceptHandler(self, e):
        name = e.name and self(e.name) or ''
        typeStr = e.type and self(e.type) or ''
        res = ['except:']
        if typeStr: res = ['except %s:' % typeStr]
        if name and typeStr: res = ['except %s as %s:' %(typeStr, name)]
        res += self.bodyIndent(e.body)
        return '\n'.join(res)

    def str_AugAssign(self, e):
        return '%s %s= %s' %(self(e.target), self(e.op), self(e.value))
    def str_Delete(self, e):
        return 'del %s' %(', '.join(self(e) for e in e.targets))
    def str_Global(self, e):
        return 'global ' + ', '.join(self(e) for e in e.names)

    def str_Print(self, e):
        dest = e.dest and self(e.dest) +', ' or ''
        values = ', '.join(self(e) for e in e.values)
        nl = (not e.nl) and ',' or ''
        return 'print %s' % dest+ values +nl




    #slices and index
    def str_Subscript(self, e): return self(e.value) + '['+ self(e.slice) + ']'
    def str_Index(self, e): return self(e.value)
    def str_Slice(self, e):
        step = {None:''}.get(e.step, self(e.step))
        return self(e.lower)+':'+self(e.upper) + step

    #base types
    def str_Num(self, e): return str(e.n)
    def str_Str(self, e):
        res = e.s
        replace = [('"', '\\"'), ("\n", "\\n"), ("\t", "\\t")]
        for a, b in replace : res = res.replace(a, b)
        return '"%s"' % res
    def str_List(self, e): return '[%s,]' % ', '.join(self(e) for e in e.elts)
    def str_Tuple(self, e): return '(%s,)' % ', '.join(self(e) for e in e.elts)
    def str_Dict(self, e): return '{%s}' %    ', '.join(self(e1) + ':' + self(e2) for e1, e2 in zip(e.keys, e.values))

    #boolean operators
    def str_BoolOp(self, e):
        return    (' %s ' % self(e.op)).join(self(e) for e in e.values)
    def str_Or(self, e): return 'or'
    def str_And(self, e): return 'and'


    #binary operators
    def str_BinOp(self, e):
        return    '%s %s %s' % (self(e.left), self(e.op), self(e.right))
    def str_Add(self, e): return '+'
    def str_Sub(self, e): return '-'
    def str_Mult(self, e): return '*'
    def str_Div(self, e): return '/'
    def str_Mod(self, e): return '%'
    def str_Pow(self, e): return '**'
    def str_LShift(self, e): return '>>'
    def str_RShift(self, e): return '<<'
    def str_BitOr(self, e): return '|'
    def str_BitXor(self, e): return '^'
    def str_BitAnd(self, e): return '&'
    def str_FloorDiv(self, e): return '//'

    #comparaison operators
    def str_Compare(self, e):
        res = self(e.left) + ' '
        res += ' '.join(self(o) + ' ' + self(c) for o, c in zip(e.ops, e.comparators))
        return    res
    def str_Eq(self, e): return '='
    def str_NotEq(self, e): return '!='
    def str_Lt(self, e): return '<'
    def str_LtE(self, e): return '<='
    def str_Gt(self, e): return '>'
    def str_GtE(self, e): return '>='
    def str_Is(self, e): return 'is'
    def str_IsNot(self, e): return 'is not'
    def str_In(self, e): return 'in'
    def str_NotIn(self, e): return 'not in'

    #unary operators
    def str_UnaryOp(self, e): return '%s %s' % (self(e.op), self(e.operand))
    def str_Not(self, e): return 'not'
    def str_UAdd(self, e): return '+'
    def str_USub(self, e): return '-'
    def str_Invert(self, e): return '~'


#print indented
def print_simple(content):
    res = []
    if hasattr(content, '_fields'):
        for f in content._fields:
            res.append(print_simple(getattr(content, f)))
    elif hasattr(content, '__iter__'):
        for e in content:
            res.append(print_simple(e))
    else:
        return str(content)

    name = content.__class__.__name__
    return '%s(%s)' % (name, ', '.join(res))


#print an indented ast
def print_indented(content, level=1):
    indent = level * '|  '
    name = content.__class__.__name__

    if hasattr(content, '_fields'): #if element from Module
        if len(content._fields) == 0: return name + '()'
        res = name + '(\n'
        for attrName in content._fields:
            attrValue = print_indented(getattr(content, attrName), level+1)
            res += '{indent}{attrName}={attrValue},\n'.format(**locals())
        return res + indent + ')'

    if hasattr(content, '__iter__'): #if it's a list
        if len(content) == 0: return '[]'
        res = '[\n'
        for e in content:
            value = print_indented(e, level+1)
            res += '{indent}{value},\n'.format(**locals())
        return res + indent + ']'

    return '"' + str(content) + '"'



#!/usr/bin/env python
import ast, inspect, re, mock, unittest, types

#TODO get out of this (up one step)
def callOnBoth(fctOri, mockFactory, visitor, *args):
  """
  call the fct with and without visitor
  the function must accept at least 1 argument
  which will be a mock object
  @param fctOri: the originel function reference
  @param mockFactory: the mock (first parameters of functions) factory function
  @param visitor: the NodeTransformer visitor object
  @param *args: the args to give to the function
  @return: a tuple of the mock calls list (withoutVisitor, withVisitor)
  """
  mOri = mockFactory()
  try:
    fctOri(mOri, *args) #test the original function
  except Exception as e:
    mOri(e)
  resOri = mOri.call_args_list

  mGoal = mockFactory()
  fctGoal = visitMethod(fctOri, visitor)
  try:
    fctGoal(mGoal, *args) #test the function modified
  except Exception as e:
    mGoal(e)
  resGoal = mGoal.call_args_list

  return (resOri, resGoal)


def visitMethod(method, *visitors):
  mvu = MethodVisitUtil(method)
  for v in visitors: mvu.visitWith(v)
  return mvu.getFct()


class MethodVisitUtil(object):
  def __init__(self, method):
    self._method = method
    self._method_name = method.func_name
    self._ast = self._method2ast()

  def _method2ast(self):
    src = inspect.getsource(self._method)
    srcClean = self.unindent(src)
    return ast.parse(srcClean)

  def getAst(self): return self._ast

  #unindent to the maximal a string
  #it use the first line as the level 0
  @staticmethod
  def unindent(s):
    if not s: return s
    lines = s.split('\n')
    reRes = re.search('(^\W+)', lines[0])
    if not reRes : return s
    reGroups = reRes.groups()
    beginStr, beginLen = reGroups[0], len(reGroups[0])

    res = []
    for line in lines:
      if line.startswith(beginStr):
        res.append(line[beginLen:])
      else:
        res.append(line)

    return '\n'.join(res)


  def visitWith(self, visitor):
    self._ast = visitor.visit(self._ast)
    self._ast = ast.fix_missing_locations(self._ast)

  def getFct(self):
    compiled = compile(self._ast, '<string>', 'exec')
    myScope = {}
    exec compiled in myScope
    return myScope[self._method_name]

  #call the current function
  def __call__(self, *args, **kargs):
    return self.getFct()(*args, **kargs)

  def __str__(self):
    return '<%s %s>' % (self.__class__.__name__, ast.dump(self._ast.body[0]))




class AstTransformerTestClass(unittest.TestCase):

  def dualTestFct(self, fctOri, visitor, mockFactory, *args):
    resOri, resVisited = callOnBoth(fctOri, mockFactory, visitor, *args)

    #TODO remove
    if resOri != resVisited:
      print 'testing %s' % fctOri.func_name
      print 'result : %s \n %s' % (resOri, resVisited)

    self.assertEqual(resOri, resVisited, "error on function %s" % fctOri.func_name)

  def checkFctOnLocals(self, locals_values, visitor, mockFactory, *args):
    for k, v in locals_values.iteritems():
      if k.startswith('test_') and isinstance(v, types.FunctionType):
        self.dualTestFct(v, visitor, mockFactory, *args)




#__EOF__

#!/usr/bin/env python

import ast
import astPrint
import os, os.path

from transform.containerEmulate import ContainerEmulate
from transform.forIntoWhile import ForIntoWhile
from transform.whileSimplifier import WhileSimplifier
from transform.cleanJumps import CleanJumps
from transform.trySimplifier import TrySimplifier
from transform.rmSyntaxicSugar import DeleteOnlyOne, AssignOnlyOne
from transform.simplifying import Simplifying

from ast2simple import PythonAst2Simple
from script2script.simple.simple import dumpSimple


def ast2str(astContent, my_format=None):
  formats = {
      'pyAst_python':astPrint.Print_python,
      'pyAst_simple':astPrint.print_simple,
      'pyAst_indented':astPrint.print_indented,
      'siAst_simple':dumpSimple,
  }
  fct = formats[my_format]

  return str(fct(astContent))


def loadPython(fstr, toSimple=True):
  """load a python file or string command, return it's Simple format"""

  if os.path.isfile(fstr):
    lp = LoadPython.loadFile(fstr)
  else: #it's a command
    lp = LoadPython.loadCommand(fstr)

  lp.doPrepare()
  if toSimple: lp.doTransform()
  return lp.getContent()


class LoadPython:
  preparation = [
      ForIntoWhile,
      WhileSimplifier,
      CleanJumps,
      TrySimplifier,
      ContainerEmulate,
      DeleteOnlyOne,
      AssignOnlyOne,
      TrySimplifier,
      Simplifying,
  ]

  transformation = [ PythonAst2Simple, ]

  def __init__(self, astContent): self._content = astContent

  @staticmethod
  def loadFile(fPath):
    """ Create a loadPython element, beginning with a file """
    with open(fPath) as f:
      return LoadPython(ast.parse(f.read(), fPath))

  @staticmethod
  def loadCommand(code):
    """ Create a loadPython element, beginning with a command """
    return LoadPython(ast.parse(code))

  def visitWith(self, visitor): self._content = visitor.visit(self._content)
  def transformAll(self): self.doPrepare(); self.doTransform()
  def doPrepare(self): [self.visitWith(m()) for m in self.preparation]
  def doTransform(self): [self.visitWith(m()) for m in self.transformation]
  def getContent(self): return self._content


#__EOF__

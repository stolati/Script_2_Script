#!/usr/bin/env python
import sys
import lang.python.ast2simple.parsePython as parse

if __name__ == "__main__":

  print sys.argv
  f = sys.argv[1]

  content = open(f).read()

  visitor = parse.PythonAst2Simple()
  print visitor
  ast = parse.parse(content, f)
  print '#####################  before  #####################'
  print ast
  ast.visiteWith(visitor)
  print '#####################  after  #####################'
  print ast


#test001 :
#  UIObject = class {
#      var element
#
#      class_new(self){
#        element = NULL
#      }
#
#      getElement = obj_fct(self){
#        return self.element
#      }
#
#      setElement = obj_fct(self, element){
#        self.element = element
#      }
#    }



#__EOF__

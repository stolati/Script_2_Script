#all2all aim to translate any language into any other language
# particulary the dynamics ones

The idea is to use (like gcc) a central language named "Simple"
Simple is simpler than most dynamic langugage.

It has :
 - function and class
 - variable declaration each time (as an object of more precise)
 - classes are not changeable at runtime
 - It have no hyheritance, all should be done by hand
 - No private or protected function/variable
 - method and function are the same, method should return null
 - Exception (try/a single catch/finally)
 - if/while/class/fct are expression (everything return something)
 - Content is simplified (if had always an else, while/for/foreach => do while)
 - Class functions are not attached to the current object
 - lambda functions
 - new Object() is a special expression (not like python)


It's interesting to load all the code once, then perfom the optimisation on them.
Each node should have maximal 3 elements on the simple stuffs


- Transforme 1 test into python ast
- Do an ast tranformation on this python ast
- transforme python ast into simple
- get the simple and return javascript
- do 2 more tests
- do 3 more tests
- do 4 more tests
- do 5 more tests
... Unil all done



Milestone 1:
 Transforme 1 test element into 


Milestone 2:




No differents assignations, only :
 - direct assignation ( variable = value )

So i[3] = 4 become : i.set(id=3, slice=4)

Python => AST => SIMPLE => AST => Javascript


Python stuff that need adaptation :
 - Yield
 - Long data type
 - Function
 - Import
 - Getter/setters
 - __call__
 - operators
 - dir
 - getattr/setattr

Make a configuration
[input]
  ast2simple
  astParsing
  source2ast
[optimisation]
  simpleParsing
  optimisation
[output]
  simple2ast
  astParsing
  ast2source

Make a library by module, so it can be adapted for each languages

Code :
 - Init, Commun
 - Library
 - Source by module
   - Modules = [expressions]
     - expression have the source line information
#
#TODO :
# - test on the foreach modifier
# - do a metaclass for SimpleElement
# - do a whileremoveElse
# - do a test case for whileRemoveElse
# - main pass for each tests
# - simplifier le try
# - do a test case for try



#__EOF__

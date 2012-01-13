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
Each node should have maximal 3 elements


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




















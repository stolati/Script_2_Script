#!/usr/bin/env python

class SimpleElement(list): pass

class Module(SimpleElement): pass
class SFunction(SimpleElement): pass
class SClass(SimpleElement): pass
class SDeclaration(SimpleElement): pass
class SAffectation(SimpleElement): pass
class SType(SimpleElement): pass
class STryCatch(SimpleElement): pass
class SCondition(SimpleElement): pass
class SLoop(SimpleElement): pass
class SConstant(SimpleElement): pass
class SReturn(SimpleElement): pass
class SRaise(SimpleElement): pass
class SCall(SimpleElement): pass
class SIsEqual(SimpleElement): pass

#__EOF__

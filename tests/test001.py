class UIObject:

    def getElement(self):
        return self.element

    def setElement(self, element):
        self.element = element


UIObject = class{

  var element

  class_new(self){
    element = None
  }

  getElement = obj_fct(self){
    return self.element
  }

  setElement = obj_fct(self, element){
    self.element = element
  }
}



UIObject = class{

  var element

  class_new(self){
    element = None
  }

  getElement = obj_fct(self){
    var var_a = getattr(self, 'element')
    return var_a
  }

  setElement = obj_fct(self, element){
    setattr(self, 'element', element)
  }
}

UIObject = function{


}


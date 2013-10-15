class message:

  def __init__(self,id,message):
    self.id=id
    self.message=message
    #~ print self.id + "/" + message
    
  def getMessage(self):
    return self.message
    
  def getId(self):
    return self.id
    

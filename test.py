
class ParameterNode(object):
  def __init__(self, children):
    self.children = children

class ParameterNodeAtInstant(object):
  def __init__(self, node, instant):
      for child_name, child in node.children.items():
        child_at_instant = child.get_at_instant(instant)
        setattr(self, child_name, child_at_instant)

class Child(object):
  def __init__(self, name):
    self.name = name

  def get_at_instant(self, instant):
    return u'{}:{}'.format(self.name, instant)


node = ParameterNode({'rsa': Child('rsa'), 'cmu': Child('cmu')})

node_at_instant = ParameterNodeAtInstant(node, '2018')

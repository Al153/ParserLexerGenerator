class Non_terminal_parse_tree_node:                                                                 #class for non terminals (ie have children)
	def __init__(self,node_type,children):
		self.terminal = 0
		self.type = node_type
		self.children = children
	def __str__(self):
		return self.type + "(" + ",".join([x.type for x in self.children]) + ")"
	def generate(self): # prints out a reconstruction of the original text
		return " ".join(map((lambda x: x.generate()),self.children))

class Terminal_parse_tree_node:                                                                     #class for terminals
	def __init__(self,node_type,token_string):
		self.terminal = 1
		self.type = node_type
		self.string = token_string
	def __str__(self):
		return self.type + "(" + self.string + ")"
	def generate(self): # prints out a reconstruction of the original text
		return self.string
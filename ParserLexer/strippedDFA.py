class StrippedDFA:
	# a stripped down DFA loaded from a dictionary
	def __init__(self,DFA_Dict,token_name):
		# token name is the name of the token to be tested
		try:
			self.state_dict = DFA_Dict["states"]
			self.accept = DFA_Dict["accept"]
			self.start = DFA_Dict["start"]
		except KeyError:
			raise DFA_load_error(token_name)

	def match(self,string):
		# string -> boolean
		current_state = self.start
		for c in string:
			if c in self.state_dict[current_state]:
				current_state = self.state_dict[current_state][c]
			else:
				return False
		return current_state in self.accept
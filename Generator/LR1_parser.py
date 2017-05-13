import json
import parseTreeNodes

class Parser:
	def __init__(self,parse_settings):
		temp_goto_table = parse_settings["goto_table"]
		self.LHS_goto_table = {int(state):temp_goto_table[state] for state in temp_goto_table}

		temp_lookahead_table = parse_settings["lookahead_action_table"]
		self.lookahead_action_table = {int(state):temp_lookahead_table[state] for state in temp_lookahead_table}

		self.enum_rules = [EnumRule(rule[0],rule[1],rule[2]) for rule in parse_settings["rules"]]

	def parse(self,tokens): # parses a stream of tokens
		self.tokens = tokens
		self.tokens.append(parseTreeNodes.Terminal_parse_tree_node("END","END"))
		self.parse_tree_stack = [0]                                                                 #starts with just starting state
		self.lookahead = self.tokens[0]                                                             #Loads in lookahead token 
		self.token_index = 1  
		self.debug_string = ''
		while not self.parse_step():
			pass
		return self.parse_tree_stack[1]

	def parse_step(self):                                                                           #main parsing step, repeated till done or error
		top_state = self.parse_tree_stack[-1]                                                       #get the top state of the stack
		try:
			#print self.lookahead.type,self.lookahead.string,
			next_action_tuple = self.lookahead_action_table[top_state][self.lookahead.type]          #uses table to calculate next values
			#print next_action_tuple
		except KeyError:
			next_action_tuple = ("error",'not expecting terminal type = '+self.lookahead.type+', terminal = "'+self.lookahead.string+'"')                                   #if there is an error, then call error
		if next_action_tuple[0] == "shift":                                                         #carries out a shift operation
			self.debug_string += self.lookahead.string
			self.shift(next_action_tuple[1])                                                        
			return 0                                                                                #returns 1 if done, so this is not done
		elif next_action_tuple[0] == "reduce":
			return self.reduce(next_action_tuple[1])                                                       #next action tuple[1] = pattern number      #carries out a reduce operation
		elif next_action_tuple[0] == "done":                                                        #if parsing complete, report back that it is done
			done = self.done()
			if done:
				return 1
		elif next_action_tuple[0] == "error":                                                       #otherwise report an error

			#self.print_parse_tree(self.parse_tree_stack[-2])
			#self.print_parse_tree(self.parse_tree_stack[-4])
			print top_state
			self.error(next_action_tuple[1])

	def shift(self,next_state):                                                                     #shift operation
		self.parse_tree_stack.append(self.lookahead)                                                #pushes lookahead symbol
		self.parse_tree_stack.append(next_state)                                                    #pushes new state
		self.lookahead = self.tokens[self.token_index]                                              #loads a new lookahead symbol
		self.token_index += 1
	
	def reduce(self,rule_number):
		pattern = self.enum_rules[rule_number].rhs
		lhs = self.enum_rules[rule_number].lhs
		if lhs == "GOAL":
			return self.done()
		length_to_pop = 2*len(pattern)                                                              #the length of the pattern to reduce is doubled (to accomodate for state values)
		popped = self.parse_tree_stack[-length_to_pop::2]                                           #pops off symbols to be matched
		self.parse_tree_stack = self.parse_tree_stack[:-length_to_pop]                              #rest of pop operation
		state_p = self.parse_tree_stack[-1]                                                         #gets previous state
		next_state = self.LHS_goto_table[state_p][lhs]                                                   #calculates new state
		tree_to_push = parseTreeNodes.Non_terminal_parse_tree_node(lhs,popped)                                     #creates  new parse tree node
		self.parse_tree_stack += [tree_to_push,next_state]                                          #pushes new tree and state
		return 0

	def done(self):
		#print self.parse_tree_stack[1].type                                                                                 #halts operation
		if len(self.parse_tree_stack) == 3 and self.parse_tree_stack[0] == 0:                      #if stack consists of a parse tree and the success state 
			return 1
		else:
			self.error("False_EOF")                                                                 #calls an errors
	
	def error(self,reason):                                                                         #error reporting
		print reason
		print "current_tokens: ",self.debug_string[-50:] if len(self.debug_string)>50 else self.debug_string
		quit()

	@staticmethod
	def print_parse_tree(parse_tree_node,offset = ''):
		if parse_tree_node.terminal:
			print offset+parse_tree_node.type+"("+parse_tree_node.string+")"
			return
		else:
			print offset+parse_tree_node.type+"("
			for child in parse_tree_node.children:
				Parser.print_parse_tree(child,offset+"  ")
			print offset+")"





class EnumRule:
	def __init__(self,lhs,rhs,number):
		self.lhs = lhs
		self.rhs = rhs
		self.number = number

if __name__ == "__main__":
	import sys
	source_name = sys.argv[1]
	parse_table_name = sys.argv[2]
	local_parser = Parser(parse_table_name)
	local_parser.print_parse_tree(local_parser.parse(open(source_name,"r").read()))


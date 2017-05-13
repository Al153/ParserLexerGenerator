import json
import sys

def generate_parser(ABNF_grammar):
	parser = Parser(ABNF_grammar)
	print "Writing to file ...",	
	parser_summary =  {
						"lookahead_action_table":parser.lookahead_action_table,
						"goto_table":parser.LHS_goto_table,
						"terminals":parser.terminals,
						"rules":[(rule.lhs,rule.rhs,rule.number) for rule in parser.enum_rules]
					}
	return parser_summary

class Parser:
	def __init__(self,ABNF_grammar):
		print "Extracting ABNF rules ...",
		self.ABNF_tree = ABNF_parse_tree(ABNF_grammar)                                          #parses grammar specification
		self.rules = self.get_rules_table()                                             #gets a list of rules from the ABNF tree
		print "Done!\nGetting grammar symbols ...",

		self.non_terminals = self.get_non_terminals()
		self.terminals = self.get_terminals()                                               #searches rules to get a list of terminal strings which are directly referenced in the grammar
		self.grammar_symbols = [symbol for symbol in self.rules] + self.terminals                        #gets all grammar symbols
		print "Done!\nProducing first sets ...",
		self.initialise_first_sets()
		print "Done!\nProducing item sets ...",
		self.item_set = self.get_item_sets()                                                        #finds all items reachable from "GOAL"
		print "Done!\nExtracting parsing tables ...",
		self.get_parsing_tables()
		print "Done!"

#_________________________________________________ Parse related functions ______________________________________________

	def get_parsing_tables(self):
		self.LHS_goto_table = {}
		self.lookahead_action_table = {}
		for state in self.enumerated_states:
			self.LHS_goto_table[state] = {}
			self.lookahead_action_table[state] = {}

			for symbol in self.enumerated_states[state].goto_table:
				if symbol == "END" and self.is_in_item_set(Item("GOAL",['PROGRAM'], [],'END'), self.enumerated_states[state].own_set):  #if the final rule, accept
					self.lookahead_action_table[state][symbol] = ("done",0)                   
				if symbol in self.terminals:
					self.lookahead_action_table[state][symbol] = ("shift",self.enumerated_states[state].goto_table[symbol])     #shift symbol onto stack, goto new state
				else:
					self.LHS_goto_table[state][symbol] = self.enumerated_states[state].goto_table[symbol]       #once a reduction has occured, get the new state

			for item in self.enumerated_states[state].own_set:
				if item.afterBlob == []: #reduce
					for rule in self.enum_rules:              #searching for acceptable rules
						found = 0
						if rule.lhs == item.lhs and rule.rhs == item.beforeBlob: #if rule is correct
							found = 1
							rule_number = rule.number
							break
					if found:
						self.lookahead_action_table[state][item.lookahead] = ("reduce",rule_number)
					else:
						print "ERROR: no correct rule found for item", 
						self.print_item(item)



#________________________________ Functions for extracting rules from the ABNF parse tree _______________________________________________________

	def get_rules_table(self):                                                                      #extracts rules into an easy to access table, addressed by the lhs of each rule
		rules = {}
		for rule in self.ABNF_tree.rules:                                                           #iterates through rules
			rules[rule] = Rule(rule,self.ABNF_tree.rules[rule])                                     #reordering rules table
		rules["GOAL"] = Rule("GOAL",[["PROGRAM"]])                                      #adds global rule
		self.get_enumerated_rules_table(rules)                                                          #generates an enumerated list of the patterns for table generation                                  
		return rules

	def get_enumerated_rules_table(self,rules):                                                         #separates out rules into a version for each rhs an enumberates them
		# rules_to_ignore = ["ELEMENTARY_TOKENS","IGNORE"]
		rules_to_ignore = []
		self.enum_rules = []                                                                        #new list
		rule_number = 0
		for rule_name in rules:                                                                     #cycles through rules
			if rule_name not in rules_to_ignore:                                                   #not a real rule
				rhs = rules[rule_name].rhs                                                               #gets rhs
				for rhs_part in rhs:                                                                    #iterates through patterns creating enumerated rules
					self.enum_rules.append(EnumRule(rule_name,rhs_part,rule_number))
					rule_number += 1

	def get_terminals(self):
		#finds terminal expressions in the rules
		terminals = []
		for symbol in self.rules:
			for pattern in self.rules[symbol].rhs:
				for token in pattern:
					if not(token in self.non_terminals or token in terminals):
						terminals.append(token)
		return terminals

	def get_non_terminals(self):
		#finds non terminal tokens
		return [symbol for symbol in self.rules]

#_______________________________ set finding algorithms ______________________
	def closure(self,input_items):
		#input is a set of items: item has lhs, rhs, and lookahead, where rhs contains 'blob'
		items = list(input_items)

		for item in items:
			if len(item.afterBlob) > 0: # if there are symbold after the blob
				next_symbol = item.afterBlob[0]
				if next_symbol not in self.terminals:
					lookaheads = self.lookaheads(next_symbol, items)
					for production in self.rules[next_symbol].rhs:
						for terminal in lookaheads:
							item_to_add = Item(next_symbol, [], production, terminal)
							if not self.is_in_item_set(item_to_add, items):
								items.append(item_to_add)
		
		#item_set = set(items)
		return frozenset(items)

	def goto(self,item_set,token):  
		j_item_set = set([])
		for item in item_set:
			if len(item.afterBlob) > 0 and item.afterBlob[0] == token:
					j_item_set |= set([Item(item.lhs, item.beforeBlob+[token], item.afterBlob[1:],item.lookahead)])
		return self.closure(j_item_set) if len(j_item_set) else frozenset(j_item_set)

	def get_item_sets(self):
		grammar_symbols = self.grammar_symbols
		starting_state = self.closure([Item("GOAL", [], ["PROGRAM"],"END")]) 
		C_set = [starting_state]
		self.enumerated_states = {0:Finite_automaton_state(starting_state,0)}   #allows for creation of finite automaton
		state_number = 1                                #counts number of states



		for item_set in C_set:
			state_index = C_set.index(item_set)
			for X in grammar_symbols:
				goto_of_x = self.goto(item_set,X)
				in_c_set, index = self.is_in_c_set(goto_of_x,C_set)
				if len(goto_of_x)>0 and not in_c_set:
					C_set.append(goto_of_x)
					self.enumerated_states[state_number] = Finite_automaton_state(goto_of_x, state_number)
					self.enumerated_states[state_index].goto_table[X] = state_number
					state_number += 1
				elif len(goto_of_x)>0: #otherwise, link back
					self.enumerated_states[state_index].goto_table[X] = index
			print "\rNumber of states = ",len(C_set),
		return frozenset(C_set)


#___________________________ AUXILARY set finding functions __________________________
	def initialise_first_sets(self):
		'''Populates first sets, modified from http://www.andrews.edu/~bidwell/456/'''
		#initialise first table
		self.get_nulls()
		self.first_sets = {symbol:[symbol] if symbol in self.terminals else [] for symbol in self.grammar_symbols}
		#for each NT, gathers a list of symbols which could be in first, including both terminals and non terminals
		for rule in self.enum_rules:
			non_terminal = rule.lhs
			pattern = rule.rhs
			for symbol in pattern:
				if not symbol in self.first_sets[non_terminal]:
					self.first_sets[non_terminal].append(symbol)        #adds the symbol
				if not self.null_dict[symbol]:                          #if the symbol derives the empty string then the next symbol is added to first
					break

		#now while there are still changes each non terminal in each set is used to get the existing symbols in its first set
		changes = 1
		while changes:
			changes = 0
			for symbol_I in self.first_sets:
				for symbol_J in self.first_sets[symbol_I]:
					if not symbol_J in self.terminals:
						changes = self.merge_lists(self.first_sets[symbol_I], self.first_sets[symbol_J])

		#remove non terminals from each set and convert lists to sets
		for symbol_I in self.first_sets:
			self.first_sets[symbol_I] = set(
				filter(
					(lambda symbol: (symbol in self.terminals)),
					self.first_sets[symbol_I]
				)
			)

	def get_nulls(self):
		'''checks if the empty string can be derived from symbol.'''

		nullable_set = set([])
		changes = 1
		while changes:
			changes = 0
			for rule in self.enum_rules:
				if rule.lhs not in nullable_set:
					# if rule is not already nullable
					add = True
					for symbol in rule.rhs:
						if symbol not in nullable_set:
							add = False
							break
					if add:
						changes = 1
						nullable_set.add(rule.lhs)
			self.null_dict = {
				symbol: (symbol in nullable_set) for symbol in self.grammar_symbols
			}
		print self.null_dict

	def lookaheads(self,symbol,item_set):			#calculate the lookahead of a set
		return_set = set([])
		item_sets = []
		for item in item_set: 						#lookahead is the union of the follow sets of all items in the item set where the symbol is a immediately to the right of the blob
			if len(item.afterBlob)>0 and item.afterBlob[0] == symbol:
				return_set |= self.follow(item)
		return return_set


	def follow(self,item):
		# follow(l -> 'a.B'b) is set of terminals that can after item
		nullable = 1
		lookaheads = set([])
		for symbol in item.afterBlob[1:]: 		#iterates through symbols, follow of an item is the first set of the symbol to the right of the one to the rights of the blob, in the current context
			lookaheads |= set(self.first_sets[symbol])
			if not self.null_dict[symbol]:
				nullable = 0
				break
		if nullable:
			lookaheads.add(item.lookahead)
		return lookaheads

#________________________________________ functions for comparing and checking membership for items, itemsets etc ___________________

	def compare_item_sets(self,item_set1,item_set2):
		#sees if two item sets are the same
		#counting_item_set = set(item_set2)              #each time an item is matched, it is removed

		if len(item_set1) != len(item_set2): #different lengths = different sets
			return False

		for item1 in item_set1:
			found = 0
			for item2 in item_set2:                     #tries to find each item in the second set, and removes it from the copy of the second set
				if (item1.lhs == item2.lhs):
					if item1.beforeBlob == item2.beforeBlob:
						if (item1.afterBlob == item2.afterBlob):
							if (item1.lookahead == item2.lookahead):
								found = 1
								#counting_item_set.remove(item2)
								break
			if not found:
				return False
		return True

	def is_in_item_set(self,item,item_set):
		#checks if an item is in an item set
		for item1 in item_set:
			if (item1.lhs == item.lhs):
				if (item1.beforeBlob == item.beforeBlob):
					if (item1.afterBlob == item.afterBlob):
						if(item1.lookahead == item.lookahead):
							return True
		return False


	def is_in_c_set(self,goto_set,C_set):
		#checks if an item set is a member of a list
		for item_set in C_set:
			if self.compare_item_sets(item_set,goto_set):
				return True, C_set.index(item_set)
		return False, None


	def merge_lists(self,list1,list2):
		#merges list2 into list 1 as if they are sets, returns changes to indicate if any changes occured
		changes = 0
		for symbol in list2:
			if not symbol in list1:
				changes = 1
				list1.append(symbol)
		return changes


#___________________________________ Functions for displaying things ______________________________________________

	def print_fsm(self):
		for index in self.enumerated_states:
			print "\n\n\n________________________ STATE ",int(index),"______________________________"
			for item in self.enumerated_states[index].own_set:
				self.print_item(item)
			print self.enumerated_states[index].goto_table



	def print_lookahead_table(self):
		for state in self.lookahead_action_table:
			print "\n\n\n________________________ STATE ",state,"_____________________________"
			for item in self.enumerated_states[state].own_set:
				self.print_item(item)
			print "\n__________________________ lookahead table ____________________________"
			for symbol in self.lookahead_action_table[state]:
				print symbol, "==>", self.lookahead_action_table[state][symbol]
			#cont = raw_input('')

	def print_first_sets(self):
		for symbol in self.rules:
			print "FIRST("+symbol+") = ",self.first_sets[symbol]

	def print_item(self,item):
		print item.lhs, "==>", item.beforeBlob + ["BLOB"] + item.afterBlob,",",item.lookahead

#______________________________________________ Auxilary classes __________________________________________________________________
class Rule:                                                                                         #simple rule class
	def __init__(self,lhs,rhs):
		self.lhs = lhs
		self.rhs = rhs

class EnumRule:
	def __init__(self,lhs,rhs,number):
		self.lhs = lhs
		self.rhs = rhs
		self.number = number
		
class Item:
	def __init__(self, lhs, beforeBlob, afterBlob, lookahead):
		self.lhs = lhs
		self.rhs = beforeBlob + ["BLOB"] + afterBlob
		self.length = len(beforeBlob) + len(afterBlob)
		self.lookahead = lookahead
		self.blobIndex = len(beforeBlob)
		self.beforeBlob = beforeBlob
		self.afterBlob = afterBlob

class Finite_automaton_state:
	def __init__(self,own_set,number):
		self.own_set = own_set  
		self.number = number       
		self.goto_table = {}

class ABNF_parse_tree:
	def __init__(self,ABNF_string):
		self.ABNF = ABNF_string
		self.get_rules()
	def get_rules(self):
		#split text into lines,ignoring excess whitespace
		lines = self.ABNF.split("\n")
		rules_list = [self.tokenise_line(line) for line in lines if self.tokenise_line(line)]
		self.rules = {rule.left_hand_side:rule.right_hand_side for rule in map(ABNF_rule,rules_list)}
	def tokenise_line(self,line):
		#simple line tokeniser
		whitespace = [' ','\t']
		escaped_dict = {"n":"\n","t":"\t",'"':'"'}
		line_tokens = []
		current_token = ''
		string = 0
		escaped = 0


		for character in line:
			if not string:                          #vanilla tokens
				if character in whitespace:         #removes whitespace
					if current_token == '':
						pass
					else:
						line_tokens.append(current_token)
						current_token = ''
				elif character == '"' and current_token == '':      #start of string
					string = 1
					current_token += character
				else:                                               #typical character
					current_token += character


			else:
				if not escaped:
					if character == "\\":       #escaped
						escaped = 1
					elif character == '"':      #end of string
						current_token += '"'
						line_tokens.append(current_token)
						current_token = ''
						string = 0
					else:
						current_token += character

				else:
					current_token += escaped_dict[character]
					escaped = 0
		if current_token != '':
			line_tokens.append(current_token)
		if line_tokens == []:
			return False
		else:
			return line_tokens
	def express_parse_tree(self):
		for rule in self.rules:
			print rule, "->",self.rules[rule]






class ABNF_rule:
	def __init__(self,rule_list):
		#rule_list is a list of tokens containing the rule
		self.rule = rule_list
		self.left_hand_side = self.get_lhs()
		self.right_hand_side = self.get_rhs()
	def get_lhs(self):
		#gets the left handside of rule equation and checks it's valid
		if "->" !=  self.rule[1]:
			raise SyntaxError('"->" Operator not present or in incorrect position in rule "'+' '.join(self.rule)+ '".')
		else:
			lhs = self.rule[0]
			return lhs

	def get_rhs(self):
		#generates a list of possible right hand sides of rule equation
		replacement_possibilities = []
		current_possibility = []
		remove_empty_string = lambda s: s != '""' # Lambda term to remove empty strings
		for token in self.rule[2:]: 
			if token == "|":
				if current_possibility != []:
					current_possibility = filter(remove_empty_string, current_possibility)
					replacement_possibilities.append(current_possibility)
					current_possibility = []
				else:
					raise SyntaxError('ABNF parser did not expect "|" operator in rule "'+ ' '.join(self.rule) + '".')
			else:
				current_possibility.append(token)
		if current_possibility != []:
			
			current_possibility = filter(remove_empty_string, current_possibility)
			replacement_possibilities.append(current_possibility)
		return replacement_possibilities
		
if __name__ == '__main__':
	table = generate_parser(sys.argv[1].split(".")[0],open(sys.argv[1]).read())
	open(sys.argv[1].split(".")[0]+".parse","w").write(json.dumps(table))
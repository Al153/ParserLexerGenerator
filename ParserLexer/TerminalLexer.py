import strippedDFA
import Errors
import parseTreeNodes

class Lexer:
	def __init__(self,dfaDict,rule_list,elementaryTokens,toIgnore):
		self.dfas = {r:strippedDFA.StrippedDFA(dfaDict[r],r) for r in dfaDict}
		self.rule_list = rule_list
		self.elementaryTokens = elementaryTokens
		self.toIgnore = toIgnore


	def lex(self,string):
		token_list = self.split(string)
		token_objects = []
		for t in token_list:
			matched = False
			for d in self.rule_list:
				if self.dfas[d].match(t):
					token_objects.append(parseTreeNodes.Terminal_parse_tree_node(d,t))
					matched = True
					break
			if not matched:
				raise Errors.LexerFailedError(t)
		token_objects.append(parseTreeNodes.Terminal_parse_tree_node("END","END"))
		return token_objects

	def split(self,source_text):
		# splits a string up using elementary tokens and ignore
        #splits text according to elementary tokens - chars which indicate a new token
		token_triggers =self.elementaryTokens	                                                    #fetch elementary tokens
		current_token = ''                                                                          #initialise current token and token list
		token_list = []
		for character in source_text:                                                               #iterate through source text
			if character in token_triggers:                                                         #splits if elementary token found
				if current_token not in self.toIgnore and current_token != '':
					token_list.append(current_token)                          #generates parse tree node object
				if character not in self.toIgnore:
					token_list.append(character)                              #adds in parse tree node for elementary token causing splitting
				current_token = ''
			else:
				current_token += character                                                          #otherwise place the character in the token

		if current_token != '' and current_token not in self.toIgnore:                         	#clean up final token
			token_list.append(current_token)
		return token_list

		
		
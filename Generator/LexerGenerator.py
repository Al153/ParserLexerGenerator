import NFA_builder
import DFA_builder
import LR1_parser
import json
import os
import parseTreeNodes

cwd = os.path.dirname(__file__)
RuleParser = LR1_parser.Parser(json.loads(open(cwd+"\\lexerRegex.parse","r").read()))

class TokenRule:
	def __init__(self,lhs,rhs):
		self.lhs = lhs
		self.rhs = rhs # an AST

def createLexer(token_rules,terminals):
	# creates dicts of DFAs for each kind of token
	nfas = {}
	rule_list = []
	print "\tBuilding NFAs ..."
	for rule in token_rules: # get NFAs for all of the REGEX rules
		# a rule is (string * parseTree)
		rule_list.append(rule.lhs)

		nfas[rule.lhs] = NFA_builder.CreateNFA(rule.rhs,nfas)
		print "\r\tNumber of states = ",  NFA_builder.stateCounter.i,

	for t in terminals: # get NFAs for all of the elements
		if t[-1] == '"' and t[0] == '"':
			rule_list.append(t)
			nfas[t] = NFA_builder.CreateNFA(parseTreeNodes.Terminal_parse_tree_node("string",t[1:-1]),nfas)
			print "\r\tNumber of states = ",  NFA_builder.stateCounter.i,
	print "\n\tDone\nBuilding DFAs"
	rule_list.reverse()
	alphabet = ' \n\t!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
	return {"dfas":{r:DFA_builder.DFA(nfas[r],alphabet).dictRepresentation() for r in rule_list},"rules": rule_list }


def getRule(line):
	tokens = tokeniseRule(line)
	ast = RuleParser.parse(tokens)
	return TokenRule(ast.children[0].string,ast.children[3])
	
def tokeniseRule(rule):
	# simple handwritten lexer
	tokens = [] # TerminalToken List
	currentToken = ''
	string = 0
	escaped = 0
	escapedDict = {'"':'"','\\':"\\","n":"\n"}
	elementaryTokens =  [" ","\t","\n","|","(",")","*","-",">","."]
	toIgnore  = [''," ","\n","\t"]
	for char in rule:
		if string:
			if escaped:
				escaped = 0
				if char in escapedDict:
					currentToken += escapedDict(char)
			else:
				if char == "\\":
					escaped = 1
				elif char == '"':
					tokens.append(createToken(currentToken,string))
					string = 0
					currentToken = ''
				else:
					currentToken += char

		else:
			if char in elementaryTokens:
				if currentToken not in toIgnore:
					tokens.append(createToken(currentToken,string))
				if char not in toIgnore:
					tokens.append(createToken(char,string))
				currentToken = ''
			else:
				if char == '"':
					if currentToken != '':
						raise RegexStringTerminalError()
					else:
						string = 1
				else:
					currentToken += char
	if currentToken not in toIgnore:
					tokens.append(createToken(currentToken,string))
	return tokens


def createToken(string,isString):
	#determines the type of terminal that a string is 
	if isString:
		return parseTreeNodes.Terminal_parse_tree_node("string",string)
	else:
		if string in ["-",">","|","(",")","*","."]:
			return parseTreeNodes.Terminal_parse_tree_node('"'+string+'"',string)
		else:
			return parseTreeNodes.Terminal_parse_tree_node("id",string)

	
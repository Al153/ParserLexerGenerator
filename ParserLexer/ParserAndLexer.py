#this script loads a PaL from file and lexes&Parses the text applied to it
import json
import LR1_parser
import TerminalLexer
import strippedDFA
from Errors import *

def PAL(sourceTextFile,PALdictFile): # <- these are file handles
	#PAL dict:
	PAL_Structure = { 
			"Parser": {
				"goto_table":{},
				"lookahead_action_table":{},
				"rules":[]
			},
			"Lexer": {
				"dfas":{},
				"rules":[]
			},
			"Terminals": [],
			"ElementaryTokens":[],
			"Ignore":[]
		}

	PALdict = json.loads(PALdictFile.read())
	checkDict(PALdict)

	# now decode some of the bits
	parseSettings = PALdict["Parser"] 
	DFA_dict = PALdict["Lexer"]["dfas"]
	DFA_rules = PALdict["Lexer"]["rules"]
	terminals = PALdict["Terminals"]
	ElementaryTokens = PALdict["ElementaryTokens"]
	toIgnore = PALdict["Ignore"]
	lexer = TerminalLexer.Lexer(DFA_dict,DFA_rules,ElementaryTokens,toIgnore)
	parser = LR1_parser.Parser(parseSettings)
	tokens = lexer.lex(sourceTextFile.read())
	return parser.parse(tokens)




def checkDict(PALdict):
	# function which checks that the PAL dict has the right structure
	if ("Parser" in PALdict) and ("Lexer" in PALdict) and ("Terminals" in PALdict) and ("ElementaryTokens" in PALdict) and ("Ignore" in PALdict):
		p = PALdict["Parser"]
		l = PALdict["Lexer"]
		if ("goto_table" in p) and ("lookahead_action_table" in p) and ("rules" in p):
			if ("dfas" in l) and ("rules" in l):
				return

	raise PALParseFileFormatError()

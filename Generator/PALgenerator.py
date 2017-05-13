import json
import parser_generator_neatened
import LexerGenerator
import Errors

def createPAL(palFile):
	# pal file should be a file handle
	print "Getting segments ...",
	segments = getSegments(palFile)
	print "Done!\nChecking PAL file format ...",
	checkFormat(segments)
	print "Done!\nGetting token rules, and grammar ...",
	token_rules = getTokenRules(segments["Terminals"])
	ABNF = segments["Grammar"]
	elementaryTokens = segments["ElementaryTokens"]
	print "elementary tokens = ", getElements(elementaryTokens)
	print "Done!\nProducing a parser: "
	parserSummary = parser_generator_neatened.generate_parser(ABNF)
	print '\nDone!\a\a\a\a\a\a\a\a\a\a\a\a\a'
	terminals = parserSummary["terminals"]
	print "Creating a lexer:"
	lexerSummary = LexerGenerator.createLexer(token_rules,terminals)
	print "Done!\nPacking structure ...",
	ignore = segments["Ignore"]
	structure = { "Parser":parserSummary,"Lexer":lexerSummary,"Terminals":terminals,"ElementaryTokens":getElements(elementaryTokens),"Ignore":getElements(ignore)}
	print "Done!"
	return structure

def getSegments(textFile):
	segments = {}
	currentSegmentName = ''
	currentSegment = ''
	for line in textFile:
		line = getLine(line)
		if line == "": continue # ignore emptylines
		if isSegmentName(line):
			if not(currentSegmentName == ""):
				segments[currentSegmentName] = currentSegment
			currentSegment = ''
			currentSegmentName = getSegmentName(line)
		else:
			currentSegment += line + "\n"
	if not(currentSegmentName == ""):
		segments[currentSegmentName] = currentSegment
	return segments

def isSegmentName(line):
	if " " not in line and line[-1] == ":":
		if "\t" not in line:
			return True
	return False

def getSegmentName(line):
	return line[:-1]

def getLine(line): 
	newLine = ''
	commented = False
	hyphen = 0
	for char in line: # remove comments
		if hyphen == 0:
			if char == "-":
				hyphen = 1
			else:
				newLine += char
		elif hyphen == 1:
			if char == "-":
				commented = True
				break
			else:
				newLine += "-" + char
				hyphen = 0

	while (newLine != '') and (newLine[0] == " " or newLine[0] == "\n" or newLine[0] == "\t"):
		newLine = newLine[1:]
	#now remove excess whitespace at EOL
	while (newLine != '') and (newLine[-1] == " " or newLine[-1] == "\n" or newLine[-1] == "\t"):
		newLine = newLine[:-1]



	return newLine

def getTokenRules(text):
	lines = text.split("\n")
	lineRules = []
	for line in lines:
		newLine = getLine(line)
		if newLine != '':
			lineRules.append(LexerGenerator.getRule(line))
	return lineRules


def main(fileName):
	file = open(fileName,"r")
	structure = createPAL(file)
	resultFileName = fileName.split(".")[0] + ".spec"
	resultFile = open(resultFileName,"w")
	resultFile.write(json.dumps(structure))

def checkFormat(segments):
	# needs to check that segments contain all of the right fields
	if not (("ElementaryTokens" in segments) and ("Ignore" in segments) and ("Terminals" in segments) and ("Grammar" in segments)):
		raise Errors.PALFormatError()

def getElements(text):
	tokens = [] # TerminalToken List
	currentToken = ''
	string = 0
	escaped = 0
	elementaryTokens =  [" ","\t","\n","|"]
	toIgnore  = [''," ","\n","\t","|"]
	escaped_dict = {"n":"\n","t":"\t",'"':'"',"r":"\r"}
	for char in text:
		if string:
			if escaped:
				escaped = 0
				if char in escaped_dict:
					currentToken += escaped_dict[char]
				else:
					currentToken += char
			else:
				if char == '"':
					string = 0
					currentToken += '"'
				elif char == "\\":
					escaped = 1
				else:
					currentToken += char
		else:
			if char in elementaryTokens:
				if currentToken not in toIgnore:
					tokens.append(currentToken)
				if char not in toIgnore:
					tokens.append(char)
				currentToken = ''
			else:
				if char == '"':
					string = 1
				currentToken += char
	if currentToken not in toIgnore:
					tokens.append(currentToken)
	
	retTokens = []
	for token in tokens:
		if token[0] == '"' and token[-1] == '"':
			retTokens.append(token[1:-1])
		else:
			print "Error: a token should begin with and end with quotation marks (\"\")"
	return retTokens

def getElements2(line): 
		whitespace = [' ','\t']
		escaped_dict = {"n":"\n","t":"\t",'"':'"',"r":"\r"}
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
				else:                                               #typical character
					current_token += character


			else:
				if not escaped:
					if character == "\\":       #escaped
						escaped = 1
					elif character == '"':      #end of string
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


		elements = []
		for token in line_tokens: 
			if token != "|":
				elements.append(token)
		return elements

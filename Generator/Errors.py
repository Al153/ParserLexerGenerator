class DFALoadError(Exception):
	def __init__(self,DFAName):
		self.DFAName = DFAName
	def __str__(self):
		return "The DFA specification for terminal: '"+self.DFAName+"' does not contain one of: 'state','accept','start'. It must contain all three to be runable."

class PALFormatError(Exception):
	def __str__():
		return "A .PAL file should contain the following fields:\nElementaryTokens\nIgnore\nTerminals\nGrammar"
class RegexStringTerminalError(Exception):
	def __init__(self):
		pass
	def __str__(self):
		return "A terminal's definition should have the correct syntax."

class ElementFormatError(Exception):
	def __init__(self,string):
		self.msg = string

	def __str__(self):
		return "An element's definition should have the correct syntaxt ("+self.msg+")."
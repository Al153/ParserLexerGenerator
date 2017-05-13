class LexerFailedError(Exception):
	def __init__(self,string):
		self.string = string
	def __str__(self):
		return "Token: '"+self.string+ "' could not be matched to a terminal type"



class PALParseFileFormatError(Exception):
	def __init__(self):
		pass
	def __str__(self):
		return "A PAL .parse file should have the specified fields."

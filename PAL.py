import Generator
import ParserLexer
import ParserLexer.LR1_parser
import sys

def Create(fileName):
	Generator.PALgenerator.main(fileName)

def Parse(SourceFileName,specFileName):
	return ParserLexer.ParserAndLexer.PAL(open(SourceFileName,"r"),open(specFileName,"r"))

if __name__ == '__main__':
	if len(sys.argv) <3:
		print "Error: please specify a flag, and at least one input file \"-(c|p) (f1.PAL| s1.source d1.spec)."
	else:
		if sys.argv[1] == "-c": # create
			Create(sys.argv[2])
		elif sys.argv[1] == "-p": # parse
			if len(sys.argv)<4:
				print "Error: if the flag is -p (parse), then both a source file and a spec file must be specified."
			else:
				ParserLexer.LR1_parser.Parser.print_parse_tree(Parse(sys.argv[2],sys.argv[3]))
		else:
			print "Error: please specify a flag, and at least one input file \"-(c|p) (f1.PAL| s1.source d1.spec)."
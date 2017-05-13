import parseTreeNodes
import LR1_parser
from collections import defaultdict

class stateCounter: # a simple object which generates a unique number for each state
	def __init__(self):
		self.i = 0
	def __call__(self):
		self.i += 1
		return self.i -1

stateCounter = stateCounter()

class Relation: # a simple class which represents a state transition
	def __init__(self,character,result_state):
		self.__character = character
		self.__result_state = result_state
	def get_character(self):
		return self.__character
	def get_result_state(self):
		return self.__result_state


class NFA_state: # a class representing an NFA state
	def __init__(self,state_id,relations_list):
		self.marked = 0
		self.__relations = []
		self.__relations_dict = defaultdict(lambda: [])

		self.__id = state_id
		self.__relations += relations_list
		for r in self.__relations:
			self.__relations_dict[r.get_character()].append(r.get_result_state())

	def addRelation(self,r):
		self.__relations.append(r)
		self.__relations_dict[r.get_character()].append(r.get_result_state())

	def getNextStates(self,c):
		return self.__relations_dict[c]

	def getAllNextStates(self):
		return self.__relations_dict

	def getRelations(self):
		return self.__relations

	def getID(self):
		return self.__id

	def clone(self,stateDict):
		#if not self.marked:
		n = NFA_state(self.__id,[]) # clones an NFA by walking through each state
		stateDict[self.__id] = n
		#self.marked = 1	
		for r in self.getRelations():
			next_id = r.get_result_state().getID() # id of state pointed to by r
			c = r.get_character() # character of relation r
			q = r.get_result_state() # state pointed to by relation r
			if next_id in stateDict:
				n.addRelation(Relation(c,stateDict[next_id]))	
			else:
				n.addRelation(Relation(c,q.clone(stateDict)))
		return n




class NFA:
	def __init__(self,states,start,accept_list):
		self.__states = states
		self.__start = start
		self.__accept = accept_list

	def getStates(self):
		return self.__states

	def getStart(self):
		return self.__start

	def getAcceptStates(self):
		return self.__accept

	#_________________ NFA Construction methods ______________________-

	def concatenate(self,B):
		#PRECONDITION: self = M(r), B = M(s)
		#POSTCONDITION: self = M(rs)
		B_start = B.getStart()
		for q in self.getAcceptStates():
			q.addRelation(Relation("",B_start))
		self.__states += B.getStates() 
		self.__accept = B.getAcceptStates()


	def alternate(self,B):
		#PRECONDITION: self = M(r), B = M(s)
		#POSTCONDITION: self = M(r|s)

		newState = NFA_state(
			stateCounter(),
			[
				Relation("",self.getStart()),
				Relation("",B.getStart())
			]
		)
		self.__states.append(newState)
		self.__states += B.getStates()
		self.__start = newState
		self.__accept += B.getAcceptStates()


	def star(self): # applies the kleene star to an nfa
		#PRECONDITION: self = M(r)
		#POSTCONDITION: self = M(r*)
		newState = NFA_state(
			stateCounter(),
			[
				Relation("",self.getStart())
			]
		)
		self.__states.append(newState)
		for q in self.getAcceptStates():
			q.addRelation(Relation("",newState))
		self.__accept = [newState]
		self.__start = newState

	def clone(self):
		
		# traverses the NFA n, cloning it
		stateDict = {} # ( id -> state )
		new = NFA([],self.getStart().clone(stateDict),[])
		for s in self.__states:
			s.marked = 0
		new.__states = [stateDict[i] for i in stateDict]
		new.__accept = [ stateDict[s.getID()] for s in self.__accept]
		return new


def TerminalNFA(char):
	# creates an NFA which accepts a single character
	stateA = NFA_state(stateCounter(),[])
	stateB = NFA_state(stateCounter(),[])
	stateA.addRelation(Relation(char,stateB))
	return NFA([stateA,stateB],stateA,[stateB])






def CreateNFA(ParseTree,nfa_dict):
	# creates an NFA from a parse tree of a regex
	#LR1_parser.Parser.print_parse_tree(ParseTree)
	if ParseTree.type == "PROGRAM": # Program -> Expr
		return CreateNFA(ParseTree.children[0],nfa_dict)
	elif ParseTree.type == "Expr": 
		if len(ParseTree.children) == 3: # Expr -> Expr "|" Term
			nfa =  CreateNFA(ParseTree.children[0],nfa_dict)
			nfa.alternate(CreateNFA(ParseTree.children[2],nfa_dict))
			return nfa
		else: # Expr -> Term
			return CreateNFA(ParseTree.children[0],nfa_dict)
	elif  ParseTree.type == "Term":
		if len(ParseTree.children) == 3: # Term -> Term . Factor
			nfa = CreateNFA(ParseTree.children[0],nfa_dict)
			nfa.concatenate(CreateNFA(ParseTree.children[2],nfa_dict))
			return nfa
		else: 							 # Term -> Factor
			return CreateNFA(ParseTree.children[0],nfa_dict)
	elif ParseTree.type == "Factor":
		if len(ParseTree.children) == 2: # Factor -> Lit "*"
			nfa = CreateNFA(ParseTree.children[0],nfa_dict)
			nfa.star()
			return nfa
		else: 								# Factor -> Lit
			return CreateNFA(ParseTree.children[0],nfa_dict)
	elif ParseTree.type == "Lit":
		if len(ParseTree.children) == 3: # Lit -> "(" Expr ")"
			return CreateNFA(ParseTree.children[1],nfa_dict)
		else: 							 # Lit -> letter
			return CreateNFA(ParseTree.children[0],nfa_dict)
	elif ParseTree.type == "id":
		try: # it's terminal
			newNFA = nfa_dict[ParseTree.string]
			return NFA.clone(newNFA)
		except KeyError:
			print "Cigar Lexer Generator Error: Unknown regex fragment used", ParseTree
			quit()
	elif ParseTree.type == "string":
		n = TerminalNFA("") # the null NFA
		for char in ParseTree.string:
			n.concatenate(TerminalNFA(char))
		return n
	else:
		print "Unexpected node type: " + ParseTree.type
		quit()

def printState(s):
	print "-------------------------------------------------------------"
	print "| State number: ", s.getID(), "\t\t\t\t|"
	print "-------------------------------------------------------------"
	for r in s.getRelations():
		print "|",r.get_character(),"-->",r.get_result_state().getID(), "\t\t\t\t|"
	print "-------------------------------------------------------------\n\n\n"

def printNFA(n):
	print "-------------------------------------------------------------"
	print "| Start:", n.getStart().getID(), "\t\t\t\t|"
	for s in n.getAcceptStates():
		print "| Accepts: ", s.getID(), "\t\t\t\t|"
	for s in n.getStates():
		printState(s)


if __name__ == "__main__":
	import sys
	import LR1_Parser
	source_name = sys.argv[1]
	grammar_name = "lexerRegex.parse"

	local_parser = LR1_parser.Parser(grammar_name)
	nfa = CreateNFA(local_parser.parse(open(source_name,"r").read()),{})
#	for s in nfa.getStates():
#		print "NEW S"
#		print s.getAllNextStates()
	printNFA(nfa)

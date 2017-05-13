# builds a DFA from an NFA
import NFA_builder
import LR1_parser

class DFAstateCounter:
	def __init__(self):
		self.i = 0
	def __call__(self):
		self.i += 1
		print "\r\tNumber of DFA states = ",self.i,
		return str(self.i -1)
	def decrement(self):
		self.i -=1

DFAstateCounter = DFAstateCounter()


class DFA_state:
	def __init__(self,nfa_set):
		self.s_id = DFAstateCounter()
		self.nfa_set =  set(nfa_set)
		self.transitions = {} # dict: char --> state


	def getClosure(self,nfa_states): #gets all NFA states one linked to ones in the set via null transitions
		changes = 1
		while changes:
			changes = 0
			new_items = set([])
			for identifier in self.nfa_set:
				nfaState = nfa_states[identifier]
				equivalent_items = set([state.getID() for state in nfaState.getNextStates("")]) #gets all the ids of states with null transitions from the nfastate
				if not (equivalent_items <= self.nfa_set):
					changes = 1
					new_items |= equivalent_items
			self.nfa_set |= new_items

	def __eq__(self,a):
		if isinstance(a,DFA_state): return self.nfa_set == a.nfa_set
		return False;

	def __ne__(self,a): return not (self == a)
	def __str__(self): #hack to give print behaviour
		string =  "-------------------------------------------------------------\n"
		string += ("| State number: " + str(self.s_id)).ljust(60) +"|\n"
		string += "-------------------------------------------------------------\n"
		for s in self.nfa_set:
			string += ("| contains: " + str(s)).ljust(60) + "|\n"

		string += "-------------------------------------------------------------\n"
		for c in self.transitions:
			string += ("|"+c+"-->"+ str(self.transitions[c].s_id)).ljust(60) + "|\n"
		string += "-------------------------------------------------------------\n\n\n"
		return string

class DFA:
	def __init__(self,nfa,alphabet):
		# builds a DFA from an NFA
		self.nfa_states = {s.getID():s for s in nfa.getStates()}
		self.start = DFA_state([nfa.getStart().getID()])
		self.start.getClosure(self.nfa_states)
		self.states = [self.start] #set of dfa states
		self.alphabet = alphabet
		changes = 1
		while changes:
			changes = 0
			for s in self.states:
					for character in self.alphabet:
						new_DFA_state = self.__getTransition(s,character)
						new_DFA_state.getClosure(self.nfa_states)
						if len(new_DFA_state.nfa_set) == 0:
							DFAstateCounter.decrement()
							continue
						# now to check if new_DFA is in the set:
						reduced_set = filter((lambda s: s == new_DFA_state), self.states)
						if len(reduced_set) == 0:
							s.transitions[character] = new_DFA_state
							self.states.append(new_DFA_state)
							changes = 1
						else:
							if character not in s.transitions:
								s.transitions[character] = reduced_set[0] # add transition to the found state
								DFAstateCounter.decrement() #decrement the state counter
								changes = 1

		#find accept states:
		self.accept = set([])
		#finds the accept states
		for  s in self.states:
			for n in s.nfa_set:
				if self.nfa_states[n] in nfa.getAcceptStates():
					self.accept.add(s.s_id)
		i = 0 #tries to merge equivalent states
		while i < len(self.states):
			a = self.states[i]
			i += 1
			j = 0
			while j < len(self.states):
				b = self.states[j]
				j += 1
				if a in self.states: # occasionally, a is removed
					if self.can_merge(a,b): # tests all pairs of states in the fsm to see if they can be merged
						self.merge_states(a,b) 
						i -= 1
						j -= 1
						a = self.states[i]

					


	def __getTransition(self,this_DFA_state,char):
		next_DFA_state = set([])
		for  nfa_id in this_DFA_state.nfa_set:
			next_DFA_state |= set([n.getID() for n in self.nfa_states[nfa_id].getNextStates(char)]) #gets the ids of each NFA state 
		return DFA_state(next_DFA_state)

	def __str__(self): # prints out a representation of the state
		string =  "-------------------------------------------------------------\n"
		string +=  ("| Start:" + str(self.start.s_id)).ljust(60) + "|\n"
		for s in self.accept:
			string += ("| Accepts: " + str(s)).ljust(60) + "|\n"
		string += "-------------------------------------------------------------\n\n\n\n"
		for s in self.states:
			string += s.__str__()
		return string

	def DFA_MATCH(self,s):
		# s is a string, try and match it
		current_state = self.start # start at the start state
		for c in s: # for every character in the string
			print current_state.s_id, "--"+c+"-->",
			if c in current_state.transitions: # find the transition associated with c
				current_state = current_state.transitions[c] # do state transition
				print current_state.s_id
			else: 											 # otherwise raise a failure condition
				current_state = "FAILURE"
				print current_state
				break
		if current_state == "FAILURE": return False
		return current_state.s_id in self.accept #check if the final state is an accepting state

	def can_merge(self,s1,s2):
		if (s1.s_id in self.accept)!=(s2.s_id in self.accept): # if one accepts and the other not, then not equivalent states
			return False
		else:
			if s1.transitions == s2.transitions: # if they have the same transitions
				return s1.s_id != s2.s_id # and are not the same stat, then they can be merged
			else: #could still be merged if they both share all their transitions with the merged state
				if len(s1.transitions) == len(s2.transitions):
					for c in s1.transitions:
						if not ((c in s1.transitions) and (c in s2.transitions)):
							return False
						if s1.transitions[c] == s2.transitions[c]: # if this transition is equal then test the next
							continue
						else:
							if s1.transitions[c] in [s1,s2] and s2.transitions[c] in [s1,s2]: #if transition not equal then check if it's in the shared set
								continue
							else:
								return False
					return True
				else:
					return False

	def merge_states(self,s1,s2):
		newState = DFA_state(s1.nfa_set|s2.nfa_set)
		DFAstateCounter.decrement()
		newState.s_id = str(s1.s_id)+"i"
		newState.transitions = s1.transitions
		if s1.s_id in self.accept:
			self.accept.add(newState.s_id)
			self.accept.remove(s1.s_id)
			self.accept.remove(s2.s_id)
		self.states.remove(s1)
		self.states.remove(s2)
		self.states.append(newState)
		for state in self.states:
			for key in state.transitions:
				if state.transitions[key] == s1 or state.transitions[key] == s2:
					state.transitions[key] = newState
		if s1 == self.start or s2 == self.start:
			self.start = newState

	def dictRepresentation(self): # creates a json representable version of the DFA
		state_dict = { s.s_id: { t: s.transitions[t].s_id for t in s.transitions} for s in self.states}
		#print self
		#print state_dict
		accept = [ a for a in self.accept]
		start = self.start.s_id

		return {"states":state_dict,"accept":accept,"start":start}





if __name__ == "__main__":
	import sys
	regex_file_name = sys.argv[1] #get a file with the regex
	string = sys.argv[2] 	  #get the string
	grammar_name = "regex.parse"
	local_parser = LR1_parser.Parser(grammar_name) #create an LR1 parser for regexes
	nfa = NFA_builder.CreateNFA(local_parser.parse(open(regex_file_name,"r").read())) #create an NFA
	dfa = DFA(nfa,"abcdefghijklmnopqrstuvwxyz")  									  #create a DFA from the NFA
	output = open("resultingDFA.txt",'w')  											  #writes the state structure of the DFA to a file
	output.write(dfa.__str__()) 				
	print dfa.DFA_MATCH(string)														  # tries to match the string



#!/usr/bin/python

## 	@package anasyn
# 	Syntactical Analyser package. 
#

import sys, argparse, re
import logging

import analex

logger = logging.getLogger('anasyn')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG
#nbVarDeclare = 0
#opUnaire
#opRel
#opMult
adr = 0
result=[]

class AnaSynException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
                return repr(self.value)

########################################################################				 	
#### Syntactical Diagrams
########################################################################				 

class SynAnalyser():
	## Attribute to store the different syntaxical units
	syntaxical_units = []
			
	## Saves the syntaxical units to a text file.
	# @param filename Name of the output file (if "" then output to stdout)
	def save_to_file(self, filename):
	
		print(self.syntaxical_units)
		print filename
		output_file = None
		if filename != "":
			try:
				output_file = open(filename, 'w')
			except:
				print "Error: can\'t open output file!"
				return
		else:
			print "!!"
			output_file = sys.stdout
		
		for i,su in enumerate(self.syntaxical_units):
			print i,su
			output_file.write("%s \n" % su)
			
		if filename != "":
			output_file.close()
		

def program(lexical_analyser):
	result.append("debutProg()")
	'''
	tra(), si il n y a pas d'autre fonctions, on n'en a pas besoin, il faut mettre apres la "procedure" ou "fonction"
	'''
	specifProgPrinc(lexical_analyser)
	lexical_analyser.acceptKeyword("is")
	corpsProgPrinc(lexical_analyser)
	result.append("finProg()")
	
def specifProgPrinc(lexical_analyser):
	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("Name of program : "+ident)
	
def  corpsProgPrinc(lexical_analyser):
	if not lexical_analyser.isKeyword("begin"):
		logger.debug("Parsing declarations")
		partieDecla(lexical_analyser)
		logger.debug("End of declarations")
		#reserver()#vars globales, non, dans le corps de DeclaVar
	lexical_analyser.acceptKeyword("begin")

	if not lexical_analyser.isKeyword("end"):
		logger.debug("Parsing instructions")
		suiteInstr(lexical_analyser)
		logger.debug("End of instructions")
			
	lexical_analyser.acceptKeyword("end")
	lexical_analyser.acceptFel()
	logger.debug("End of program")
	
def partieDecla(lexical_analyser):
        if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
                listeDeclaOp(lexical_analyser)
                if not lexical_analyser.isKeyword("begin"):
                        listeDeclaVar(lexical_analyser)
        
        else:
                listeDeclaVar(lexical_analyser)

def listeDeclaOp(lexical_analyser):
	declaOp(lexical_analyser)
	lexical_analyser.acceptCharacter(";")
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :
		listeDeclaOp(lexical_analyser)

def declaOp(lexical_analyser):
	if lexical_analyser.isKeyword("procedure"):
		procedure(lexical_analyser)
	if lexical_analyser.isKeyword("function"):
		fonction(lexical_analyser)

def procedure(lexical_analyser):
	lexical_analyser.acceptKeyword("procedure")
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("Name of procedure : "+ident)
    #tra()   
	partieFormelle(lexical_analyser)

	lexical_analyser.acceptKeyword("is")
	corpsProc(lexical_analyser)
       

def fonction(lexical_analyser):
	lexical_analyser.acceptKeyword(" n")
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("Name of function : "+ident)
	#tra()
        partieFormelle(lexical_analyser)

	lexical_analyser.acceptKeyword("return")
	nnpType(lexical_analyser)
        
	lexical_analyser.acceptKeyword("is")
	corpsFonct(lexical_analyser)

def corpsProc(lexical_analyser):
	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstr(lexical_analyser)
	lexical_analyser.acceptKeyword("end")

def corpsFonct(lexical_analyser):
	if not lexical_analyser.isKeyword("begin"):
		partieDeclaProc(lexical_analyser)
	lexical_analyser.acceptKeyword("begin")
	suiteInstrNonVide(lexical_analyser)
	lexical_analyser.acceptKeyword("end")

def partieFormelle(lexical_analyser):
	lexical_analyser.acceptCharacter("(")
	if not lexical_analyser.isCharacter(")"):
		listeSpecifFormelles(lexical_analyser)
	lexical_analyser.acceptCharacter(")")

def listeSpecifFormelles(lexical_analyser):
	specif(lexical_analyser)
	if not lexical_analyser.isCharacter(")"):
		lexical_analyser.acceptCharacter(";")
		listeSpecifFormelles(lexical_analyser)

def specif(lexical_analyser):
	listeIdent(lexical_analyser)
	lexical_analyser.acceptCharacter(":")
	if lexical_analyser.isKeyword("in"):
		mode(lexical_analyser)
                
	nnpType(lexical_analyser)

def mode(lexical_analyser):
	lexical_analyser.acceptKeyword("in")
	if lexical_analyser.isKeyword("out"):
		lexical_analyser.acceptKeyword("out")
		logger.debug("in out parameter")                
	else:
		logger.debug("in parameter")

def nnpType(lexical_analyser):
	if lexical_analyser.isKeyword("integer"):
		lexical_analyser.acceptKeyword("integer")
		logger.debug("integer type")
	elif lexical_analyser.isKeyword("boolean"):
		lexical_analyser.acceptKeyword("boolean")
		logger.debug("boolean type")                
	else:
		logger.error("Unknown type found <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Unknown type found <"+ lexical_analyser.get_value() +">!")

def partieDeclaProc(lexical_analyser):
	listeDeclaVar(lexical_analyser)

def listeDeclaVar(lexical_analyser):
	declaVar(lexical_analyser)
	if lexical_analyser.isIdentifier():
		listeDeclaVar(lexical_analyser)

def declaVar(lexical_analyser):
	#nbVarDeclare=0
	listeIdent(lexical_analyser)
	lexical_analyser.acceptCharacter(":")
	logger.debug("now parsing type...")
	nnpType(lexical_analyser)
	lexical_analyser.acceptCharacter(";")
	#reserver(nbVarDeclare)

def listeIdent(lexical_analyser):
	ident = lexical_analyser.acceptIdentifier()
	logger.debug("identifier found: "+str(ident))
	#reserver(1) ou #nbVarDeclare++ preferee
	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		listeIdent(lexical_analyser)

def suiteInstrNonVide(lexical_analyser):
	instr(lexical_analyser)
	if lexical_analyser.isCharacter(";"):
		lexical_analyser.acceptCharacter(";")
		suiteInstrNonVide(lexical_analyser)

def suiteInstr(lexical_analyser):
	if not lexical_analyser.isKeyword("end"):
		suiteInstrNonVide(lexical_analyser)

def instr(lexical_analyser):		
	if lexical_analyser.isKeyword("while"):
		boucle(lexical_analyser)
	elif lexical_analyser.isKeyword("if"):
		altern(lexical_analyser)
	elif lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
		es(lexical_analyser)
	elif lexical_analyser.isKeyword("return"):
		retour(lexical_analyser)
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()

		if lexical_analyser.isSymbol(":="):	
			#si ident est la variable globale
			#empiler(ad(ident))
			#si ident est la variable locale
			#empilerAd(ad(ident))
			#si ident est la variable parametre
			#empilerParam(ad(ident))			
			lexical_analyser.acceptSymbol(":=")
                        expression(lexical_analyser)
                        # affectation()
			logger.debug("parsed affectation")
		elif lexical_analyser.isCharacter("("):
			lexical_analyser.acceptCharacter("(")
			if not lexical_analyser.isCharacter(")"):
				listePe(lexical_analyser)

			lexical_analyser.acceptCharacter(")")
			logger.debug("parsed procedure call")
		else:
			logger.error("Expecting procedure call or affectation!")
			raise AnaSynException("Expecting procedure call or affectation!")
		
	else:
		logger.error("Unknown Instruction <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Unknown Instruction <"+ lexical_analyser.get_value() +">!")

def listePe(lexical_analyser):
	expression(lexical_analyser)
	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		listePe(lexical_analyser)

def expression(lexical_analyser):
	logger.debug("parsing expression: " + str(lexical_analyser.get_value()))

	exp1(lexical_analyser)
	if lexical_analyser.isKeyword("or"):
		lexical_analyser.acceptKeyword("or")
		exp1(lexical_analyser)
		#ou()
        
def exp1(lexical_analyser):
	logger.debug("parsing exp1")
	
        exp2(lexical_analyser)
	if lexical_analyser.isKeyword("and"):
		lexical_analyser.acceptKeyword("and")
		exp2(lexical_analyser)
		#et()
        
def exp2(lexical_analyser):
	logger.debug("parsing exp2")
        
	exp3(lexical_analyser)
	if	lexical_analyser.isSymbol("<") or \
		lexical_analyser.isSymbol("<=") or \
		lexical_analyser.isSymbol(">") or \
		lexical_analyser.isSymbol(">="):
		opRel(lexical_analyser)
		exp3(lexical_analyser)
		#opRel()
	elif lexical_analyser.isSymbol("=") or \
		lexical_analyser.isSymbol("/="): 
		opRel(lexical_analyser)
		exp3(lexical_analyser)
	
def opRel(lexical_analyser):
	logger.debug("parsing relationnal operator: " + lexical_analyser.get_value())
        
	if	lexical_analyser.isSymbol("<"):
		lexical_analyser.acceptSymbol("<")
        #opRel = inf()
	elif lexical_analyser.isSymbol("<="):
		lexical_analyser.acceptSymbol("<=")
        #opRel = infeg()
	elif lexical_analyser.isSymbol(">"):
		lexical_analyser.acceptSymbol(">")
        #opRel = sup()
	elif lexical_analyser.isSymbol(">="):
		lexical_analyser.acceptSymbol(">=")
        #opRel = supeg()
	elif lexical_analyser.isSymbol("="):
		lexical_analyser.acceptSymbol("=")
        #opRel = egal()
	elif lexical_analyser.isSymbol("/="):
		lexical_analyser.acceptSymbol("/=")
        #opRel = diff()
	else:
		msg = "Unknown relationnal operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp3(lexical_analyser):
	logger.debug("parsing exp3")
	exp4(lexical_analyser)	
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):
		opAdd(lexical_analyser)
		exp4(lexical_analyser)
		#opAdd()

def opAdd(lexical_analyser):
	logger.debug("parsing additive operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
		#opAdd = add()
                
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
		#opAdd = sous()
                
	else:
		msg = "Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def exp4(lexical_analyser):
	logger.debug("parsing exp4")
        
	prim(lexical_analyser)	
	if lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"):
		opMult(lexical_analyser)
		prim(lexical_analyser)
		#opMult()

def opMult(lexical_analyser):
	logger.debug("parsing multiplicative operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("*"):
		lexical_analyser.acceptCharacter("*")
        #opMult = mult()        
	elif lexical_analyser.isCharacter("/"):
		lexical_analyser.acceptCharacter("/")
        #opMult = div()        
	else:
		msg = "Unknown multiplicative operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def prim(lexical_analyser):
	logger.debug("parsing prim")
        
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-") or lexical_analyser.isKeyword("not"):
		opUnaire(lexical_analyser)
	elemPrim(lexical_analyser)
	#opUnaire()
	
def opUnaire(lexical_analyser):
	logger.debug("parsing unary operator: " + lexical_analyser.get_value())
	if lexical_analyser.isCharacter("+"):
		lexical_analyser.acceptCharacter("+")
        #opUnaire = ""?        
	elif lexical_analyser.isCharacter("-"):
		lexical_analyser.acceptCharacter("-")
        #opUnaire = moins()        
	elif lexical_analyser.isKeyword("not"):
		lexical_analyser.acceptKeyword("not")
        #opUnaire = non()        
	else:
		msg = "Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

def elemPrim(lexical_analyser):
	logger.debug("parsing elemPrim: " + str(lexical_analyser.get_value()))
	if lexical_analyser.isCharacter("("):
		lexical_analyser.acceptCharacter("(")
		expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")
	elif lexical_analyser.isInteger() or lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		valeur(lexical_analyser)
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()
		if lexical_analyser.isCharacter("("):			# Appel fonct
			lexical_analyser.acceptCharacter("(")
			if not lexical_analyser.isCharacter(")"):
				listePe(lexical_analyser)

			lexical_analyser.acceptCharacter(")")
			logger.debug("parsed procedure call")

			logger.debug("Call to function: " + ident)
		else:
			logger.debug("Use of an identifier as an expression: " + ident)
                        # ...
	else:
		logger.error("Unknown Value!")
		raise AnaSynException("Unknown Value!")

def valeur(lexical_analyser):
	if lexical_analyser.isInteger():
		entier = lexical_analyser.acceptInteger()
		logger.debug("integer value: " + str(entier))
		#empiler(str(entier))
		##si ident est la variable globale
			#empiler(ad(ident))
			#si ident est la variable locale
			#empilerAd(ad(ident))
			#si ident est la variable parametre
			#empilerParam(ad(ident))	
		#valeurPile()
                return "integer"
	elif lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		vtype = valBool(lexical_analyser)
                return vtype
	else:
		logger.error("Unknown Value! Expecting an integer or a boolean value!")
		raise AnaSynException("Unknown Value ! Expecting an integer or a boolean value!")

def valBool(lexical_analyser):
	if lexical_analyser.isKeyword("true"):
		lexical_analyser.acceptKeyword("true")	
		logger.debug("boolean true value")
		#empiler(1)
                
	else:
		logger.debug("boolean false value")
		lexical_analyser.acceptKeyword("false")	
        #empiler(0)
                
        return "boolean"

def es(lexical_analyser):
	logger.debug("parsing E/S instruction: " + lexical_analyser.get_value())
	if lexical_analyser.isKeyword("get"):
		lexical_analyser.acceptKeyword("get")
		lexical_analyser.acceptCharacter("(")
		ident = lexical_analyser.acceptIdentifier()
		lexical_analyser.acceptCharacter(")")
		logger.debug("Call to get "+ident)
		#si ident est la variable globale
			#empiler(ad(ident))
			#si ident est la variable locale
			#empilerAd(ad(ident))
			#si ident est la variable parametre
			#empilerParam(ad(ident))	
		#get()
	elif lexical_analyser.isKeyword("put"):
		lexical_analyser.acceptKeyword("put")
		lexical_analyser.acceptCharacter("(")
		expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")
		logger.debug("Call to put")
		#put()
	else:
		logger.error("Unknown E/S instruction!")
		raise AnaSynException("Unknown E/S instruction!")

def boucle(lexical_analyser):
	logger.debug("parsing while loop: ")
	lexical_analyser.acceptKeyword("while")
	#(ad1)
	expression(lexical_analyser)
	#tze(ad2)
	lexical_analyser.acceptKeyword("loop")
	suiteInstr(lexical_analyser)
	#tra(ad1)
	lexical_analyser.acceptKeyword("end")
	#(ad2)
	logger.debug("end of while loop ")

def altern(lexical_analyser):
	logger.debug("parsing if: ")
	lexical_analyser.acceptKeyword("if")

	expression(lexical_analyser)
    #tze(ad1)   
	lexical_analyser.acceptKeyword("then")
	suiteInstr(lexical_analyser)
	#tra(ad2)
	if lexical_analyser.isKeyword("else"):
		lexical_analyser.acceptKeyword("else")
		#(ad1)
		suiteInstr(lexical_analyser)
       
	lexical_analyser.acceptKeyword("end")
	logger.debug("end of if")
	#(ad2)
	
def retour(lexical_analyser):
	logger.debug("parsing return instruction")
	lexical_analyser.acceptKeyword("return")
	expression(lexical_analyser)
	#retourFonc()

	

########################################################################				 	
def main():
 	
	parser = argparse.ArgumentParser(description='Do the syntactical analysis of a NNP program.')
	parser.add_argument('inputfile', type=str, nargs=1, help='name of the input source file')
	parser.add_argument('-o', '--outputfile', dest='outputfile', action='store', \
                default="", help='name of the output file (default: stdout)')
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
	parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, \
                default=logging.INFO, help='show debugging info on output')
        parser.add_argument('-p', '--pseudo-code', action='store_const', const=True, default=False, \
                help='enables output of pseudo-code instead of assembly code')
        parser.add_argument('--show-ident-table', action='store_true', \
                help='shows the final identifiers table')
	args = parser.parse_args()

	filename = args.inputfile[0]
	f = None
	try:
		f = open(filename, 'r')
	except:
		print "Error: can\'t open input file!"
		return
		
	outputFilename = args.outputfile
	
  	# create logger      
  	LOGGING_LEVEL = args.debug
	logger.setLevel(LOGGING_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOGGING_LEVEL)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

        if args.pseudo_code:
        	#debutProg()
        	#if
                True#
        else:
                True#

	lexical_analyser = analex.LexicalAnalyser()
	
	lineIndex = 0
	for line in f:
		line = line.rstrip('\r\n')
		lexical_analyser.analyse_line(lineIndex, line)
		lineIndex = lineIndex + 1
	f.close()
	

	# launch the analysis of the program
	lexical_analyser.init_analyser()
	program(lexical_analyser)
		
        if args.show_ident_table:
                print "------ IDENTIFIER TABLE ------"
                #print str(identifierTable)
                print "------ END OF IDENTIFIER TABLE ------"

	syn_analyser = SynAnalyser()	
	syn_analyser.syntaxical_units.append("h222ah")
	syn_analyser.syntaxical_units.append("hah")
	syn_analyser.syntaxical_units.append("hah")
	syn_analyser.syntaxical_units.append("hah")
	syn_analyser.save_to_file(outputFilename) 
	

########################################################################				 

if __name__ == "__main__":
    main() 

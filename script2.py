import script1
from collections import Counter

import csv


with open("MichaelisMenten_CellML1.0.txt", "r") as f:
	lines = f.readlines()
outputfile = open("SBMLfile.txt", "wb")

annotationDict, humanNameList,stateNameList = script1.getAnnontation()
countSpecies = 0
countReactions = 0
counter = 1
parseState = False
parsing = False
parseParam = False
parseGen = False
initialRulesList = []
initialRulesNames = []
assignmentRulesList = []
assignmentRulesNames = []

f = open('MM-Nmatrix.csv', 'rb')
reader = csv.reader(f)
headers = reader.next()

column = {}
for h in headers:
	column[h] = []

for row in reader:
	for h, v in zip(headers, row):
		column[h].append(v)
speciesList = column['Species']

for line in lines:
		
	# The species and compartments need to be printed out
	# Count the number of Species and reactions 
	countSpecies = 0
	countReactions = 0		
	for k in annotationDict.values():
		if 'OPB_00340' in k:
			countSpecies = countSpecies + 1	
		if 'OPB_00593' in k:
			countReactions = countReactions + 1

	# Every third line is empty, the species need to be added in first
	if counter == 3:
		outputfile.write( "\n  // Compartments and Species:\n");
		outputfile.write( "  species ");
		for item in annotationDict.values():
			#print item, countSpecies
			if 'OPB_00340' in item and countSpecies > 1:
				outputfile.write(item[0] + ", ")
				countSpecies = countSpecies - 1

			elif 'OPB_00340' in item and countSpecies == 1:
				outputfile.write(item[0] + ";\n ")
				countSpecies = countSpecies - 1
				break
	counter = counter + 1

	if line.startswith("model") and  "__state" in line:
		parseState = True

	elif line.startswith("end"):
		parseState = False				

	# While we are not at the end of the state import section 
	if parseState:

		# Distinguish between the assignment rules and reactions
		if line.startswith("  // Assignment Rules:"):
			outputfile.write("\n  // Reactions:\n")
			parsing = True

		elif line.startswith("  // Rate Rules:"):
			outputfile.write("\n  // Assignment Rules:\n")
			for rule in assignmentRulesList:
				outputfile.write(rule)	
			parsing = False

		# While we are still between the assignment rule and rate rule part in the file
		if parsing:		
			reactionNamesplit = line.split(" := ")
			assignmentRuleName = reactionNamesplit[0].strip() # This could be a reaction, initial assignment or assignment rule
			
			for item in annotationDict.values():
				# Identify if the assignment rule is a reaction
				if assignmentRuleName in item and 'OPB_00593' in item:
					LHS = []
					RHS = []
					counting = 0
					for j in column[assignmentRuleName]:
						if int(j) > 0:
							term = j + speciesList[counting]
							RHS.append("+" + term)
						elif int(j) < 0:
							term_changeSign = int(j)
							term_changeSign = term_changeSign * -1
							term = "+" + `term_changeSign` + speciesList[counting]			
							LHS.append(term)
						else:
							counting = counting + 1
							continue
						counting = counting + 1
						
					leftside = ' '.join(LHS)
					rightside = ' '.join(RHS)		
					reaction = leftside + " -> " + rightside
					outputfile.write("  " + assignmentRuleName + ":" + reaction + "; " + reactionNamesplit[1])

				# Identify is the assignment rule is a initial assignmemt rule (not a reaction)								
				elif line.startswith("  q"):			
					initialRulesNames.append(line)		
					
				# Identify is the assignment rule is an assignmemt rule (not a reaction)							
				elif line.startswith("  u"):							
					assignmentRulesList.append(line)
					break				

	# Here, parseState = False, meaning that we have reached the end of the state import section	
	else:

		if line.startswith("model") and  "__param" in line:
			parseParam = True
			continue # skips the model __param() line

		elif line.startswith("end"):
			parseParam = False				

		# While we are not at the end of the param import section
		if parseParam:
			outputfile.write(line)

		# Here, parseParam = False, end of the param import section 		
		else:

			if line.startswith("model") and  "__module" in line: #change to general!!!!!!!!!!!
				outputfile.write("\n  // Species initializations:\n")				
				parseGen = True

			elif line.startswith("end"):
				parseGen = False				

			# While we are in the general section: must get species initials
			if parseGen:
				#outputfile.write(line)
				#// Variable initializations:
				if line.startswith("  q_0_"):
					renamedSpecieLine =line.replace("_0", "")
					outputfile.write(renamedSpecieLine)		
	
			# Here, parseGen = False, end of the general import section				
			#else:
				#print "K"
			#	outputfile.write(line)


outputfile.close()

# Regular expressions used to find and replace in file
import re 
# Read in the file
filedata = None
with open('SBMLfile.txt', 'r') as file :
  fileLine = file.read()

stateNameList.remove('t')
humanNameList.remove('time')

# Replace the target string - start of code from Tommy
patterns = []
for state, rename in zip(stateNameList, humanNameList):
	# This is to handle name replacement when there are more than 10 species i.e. to find and replace u11 and u1 separently 
	patterns.append((re.compile(state + '([^0-9]|$)'), rename + '\\1'))

for patt, rename in patterns:
	fileLine = patt.sub(rename, fileLine)
	fileLine = fileLine.replace("q_", "") # humanNameList still has q_ before the species names, etc.
# Replace the target string - end of code from Tommy

with open('SBMLfile.txt', 'w') as file:
  file.write(fileLine)

print "Success!"














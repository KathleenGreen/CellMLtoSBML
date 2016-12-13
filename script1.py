
def getAnnontation():

	from collections import defaultdict
	dictIDNameAnnotation = {}
	parameterNamelist = []
	parameterValuelist = []
	speciesValuelist = []
	with open("MichaelisMenten_CellML1.0.cellml") as f:
		lines = f.readlines()
	modelName = ""
	idNumberList = []
	annotationList = []
	counter = 1
	humanNameList = []
	stateNameList = []

	for line in lines:
		if "<model name=" in line:
			nameModelsplit = line.split("name=")
			nameWithQuotes = nameModelsplit[1].split()
			tempModelName = nameWithQuotes[0]
			modelName = tempModelName[1:-1]
		
		else:		
			if "<variable" in line:
				if "cmeta:id=" in line:
					# get the index and id number of the species, reaction or time i.e. everything except parameters	
					indexIDNo = line.find("cmeta:id=")
					tempID = line[indexIDNo + 10: indexIDNo + 22]
		
					# get the name of the species, reaction or time
					nameIDsplit = line.split("name=")
					nameWithQuotes = nameIDsplit[1].split()
					tempName = nameWithQuotes[0]
					tempName = tempName[1:-1]

					if "initial_value=" in nameIDsplit[0]:
						valueSplit = line.split("initial_value=")				
						valueWithQuotes = valueSplit[1].split()
						speciesValueQuotes = valueWithQuotes[0]
						speciesValue = speciesValueQuotes[1:-1] 
						#speciesValuelist.append(speciesValue)
						dictIDNameAnnotation.setdefault(tempID, []).append(tempName)
						dictIDNameAnnotation.setdefault(tempID, []).append(speciesValue)
						#d[tempID]= tempName
						#print (tempID, tempName)
					else:
						speciesValue = 'noinitial'	
						dictIDNameAnnotation.setdefault(tempID, []).append(tempName)
						dictIDNameAnnotation.setdefault(tempID, []).append(speciesValue)
			

			elif " <map_variables" in line:
						nameVar1split = line.split("variable_1=")				
						nameWithQuotesVar1 = nameVar1split[1].split()
						tempVar1Name = nameWithQuotesVar1[0]
						tempVar1Name = tempVar1Name[1:-1]
						humanNameList.append(tempVar1Name)

						nameVar2split = line.split("variable_2=")				
						nameWithQuotesVar2 = nameVar2split[1].split()
						tempVar2Name = nameWithQuotesVar2[0]
						tempVar2Name = tempVar2Name[1:-3]					
						stateNameList.append(tempVar2Name)			
	

			elif "<rdf:Description rdf:about=" in line:	

				splitLine = line.split("<rdf:Description rdf:about=")
				splitLine = splitLine[1]				
				idNumberAndAnnotation = splitLine[2:-3]

				if counter%2.0 != 0.0:
					idNumberList.append(idNumberAndAnnotation)			

				else:
					annotationID = idNumberAndAnnotation[-10:-1]
					annotationList.append(annotationID)		
				counter = counter + 1


	joinedIDandAnnotationList = [None]*(len(idNumberList)+len(annotationList))
	joinedIDandAnnotationList[::2] = idNumberList
	joinedIDandAnnotationList[1::2] = annotationList

	for j in joinedIDandAnnotationList:
		if j in dictIDNameAnnotation.keys():
			indexIDKey = joinedIDandAnnotationList.index(j)
			indexIDKey = indexIDKey + 1
			dictIDNameAnnotation.setdefault(j, [])
			dictIDNameAnnotation.setdefault(j,[]).append(joinedIDandAnnotationList[indexIDKey])

	#print parameterNamelist
	#print parameterValuelist
	#print speciesValuelist
	f.close()
	#print dictIDNameAnnotation
	return dictIDNameAnnotation,humanNameList,stateNameList

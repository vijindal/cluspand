import os
import re

class Parser:
    # Parses a given input file and returns a list of parameters for all structures.
    def parse(lattice_type, elements):
        #file_path = os.path.join(os.getcwd(), '../'+lattice_type+'_txt_files/'+file_name)
        #file_path = os.path.join(os.getcwd(), lattice_type+'_txt_files/'+file_name)
        file_name = elements[0]+'_'+elements[1]+'_'+lattice_type+'.txt'
        file_path = os.path.join(os.getcwd(),'data_files/'+file_name)
        f = open(file_path,"r")
        lines = f.readlines()
        
        structures_parameters_list = []
        structDataList=[] #list for holding structure data
        for i in range(len(lines)):
            l = lines[i] 
            if not " Structure PRE " in l:
                continue
            else:
                #print(l)
                #Getting structure name
                name = l[1:(l.find("#")-2)]  # i and l are the index and string of line containing " Structure PRE " respectively
                #Getting translation vectors
                a = list(map(float,re.findall("[+-]?\d+(?:\.\d+)?", lines[i+3])[1:]))
                b = list(map(float,re.findall("[+-]?\d+(?:\.\d+)?", lines[i+4])[1:]))
                c = list(map(float,re.findall("[+-]?\d+(?:\.\d+)?", lines[i+5])[1:]))
                #Getting source positions
                i += 8
                source_positions = {}
                while not " Structure POST " in lines[i]:
                    pos = list(map(float,re.findall("[+-]?\d+(?:\.\d+)?", lines[i])[1:]))
                    element = lines[i].split()[-1]
                    if element.find("_") != -1:
                        element = element[0:element.find("_")]
                    if element.find("+") != -1:
                        element = element[0:element.find("+")]
                    x = [i * pos[0] for i in a] 
                    y = [i * pos[1] for i in b] 
                    z = [i * pos[2] for i in c]
                    pos = [sum(tmp) for tmp in zip(x,y)]
                    pos = [sum(tmp) for tmp in zip(pos,z)]
                    if not element in source_positions:
                        source_positions[element] = []
                    source_positions[element].append(pos)
                    i+=1
                    #print( source_positions)
                # Getting total energy
                while not " DATA " in lines[i]:
                    i += 1
                #print(lines[i+2])
                #print(list(map(float,re.findall("[+-]?\d+(?:\.\d+)?", lines[i+2]))))
                total_energy = list(map(float,re.findall("[+-]?\d+(?:\.\d+)?", lines[i+2])))[1]
                # Generating a structure parameters list
                structure_parameters = [name, lattice_type, [a,b,c], source_positions, total_energy]
                structures_parameters_list.append(structure_parameters)
                #print(structure_parameters)
                while not " aflowlib.out " in lines[i]: #searching output line for the structure 
                    i += 1
                #print(lines[i+1])
                outputLine=lines[i+1].split(']  ')[1] #removing structure name from the output line
                #print( outputLine)
                structData = dict(item.split("=") for item in outputLine.split("| ")) #dictionary of structure data
                #print(structData['natoms'])
                #print(structData['stoichiometry'])
                if int(structData['natoms'])!=1: #adding a new key 'composition_frac' for composition in mol fraction
                    tempDict={'composition_frac':float(structData['stoichiometry'].split(',')[1])}
                    #print("tempDict",tempDict)
                else:# stoichiometry holds only one value in case of one atom structure 
                    #print("species",structData['species'], ", element[0] ",elements[0]) 
                    if structData['species'].strip() == elements[0].strip():
                        #print("matched")
                        tempDict={'composition_frac':0.0}
                    else:
                        #print("not matched")
                        tempDict={'composition_frac':1.0}
                    #print("tempDict",tempDict)
                structData.update(tempDict) 
                
                #Adding the structure_parameters in structures_parameters_list
                #print(structData['composition_frac'])
                structDataList.append(structData)
                
        return (structures_parameters_list,structDataList)

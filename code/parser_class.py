import os
import re

class Parser:
    # Parses a given input file and returns a list of parameters for all structures.
    def parse(lattice_type, file_name):
        #file_path = os.path.join(os.getcwd(), '../'+lattice_type+'_txt_files/'+file_name)
        #file_path = os.path.join(os.getcwd(), lattice_type+'_txt_files/'+file_name)
        file_path = os.path.join(os.getcwd(),'data_files/'+file_name)
        f = open(file_path,"r")
        lines = f.readlines()
        
        structures_parameters_list = []
        for i in range(len(lines)):
            l = lines[i]
            if not " Structure PRE " in l:
                continue
            else:
                #Getting structure name
                name = l[1:(l.find("#")-2)]
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
                # Getting total energy
                while not " DATA " in lines[i]:
                    i += 1
                total_energy = list(map(float,re.findall("[+-]?\d+(?:\.\d+)?", lines[i+2])))[1]
                # Generating a structure parameters list
                structure_parameters = [name, lattice_type, [a,b,c], source_positions, total_energy]
                #print(structure_parameters)
                #Adding the structure_parameters in structures_parameters_list
                structures_parameters_list.append(structure_parameters)
                
        return structures_parameters_list

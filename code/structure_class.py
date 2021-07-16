import os
from cluster_class import cluster
from structure_helper_class import structure_helper

#Custom round function
def myround(x, prec=2, base=.5):
    return [round(base * round(float(u)/base),prec) for u in x]

#Class for encapsulating the attributes of a 'structure'
class structure:
    
    #Constructor
    def __init__(self, parameters, max_distance, elements,
                 pure_element_0_min_energy, pure_element_1_min_energy):
        self.name_ = parameters[0]
        self.lattice_type_ = parameters[1]
        self.translation_vectors_ = parameters[2]
        self.source_positions_ = {}
        for atom,pos_list in parameters[3].items():
            self.source_positions_[atom] = []
            for pos in pos_list:
                self.source_positions_[atom].append(myround(pos))
        self.clusters_list_ = self.generate_clusters(max_distance, elements)
        self.actual_total_energy_ = parameters[4]
        self.total_energy_ = self.cal_delta_energy(pure_element_0_min_energy, 
                                              pure_element_1_min_energy, 
                                              elements)
#        self.total_energy_ = parameters[4]
        
    def cal_delta_energy(self, pure_0, pure_1, all_elements):
        comp = structure_helper.get_composition_ratio(self, all_elements)
        return self.actual_total_energy_ - comp*pure_1 - (1-comp)*pure_0
        
    #Printing method
    def print(self, print_clusters_info = False):
        print("--------------------------------------------------------------")
        print("Structure name :", self.name_)
        print("\nTranslation vectors :")
        for vector in self.translation_vectors_:
            print(vector)
        print("\nSource positions :")
        for atom,pos in self.source_positions_.items():
            print(atom, pos)
        if print_clusters_info:
            print("\nClusters :")
            for cluster_obj in self.clusters_list_:
                print("\nCorrelation =", cluster_obj.correlation_)
                print("Multiplicity =", cluster_obj.multiplicity_)
                print("Distance =", cluster_obj.distance_)
                print("Number of points =", cluster_obj.number_of_points_)
                print("Positions of points =", cluster_obj.points_positions_)
        else:  
            print("\nCorrelations :")
            print([x.correlation_ for x in self.clusters_list_])
        print("\nTotal Energy =",self.total_energy_)
        print("--------------------------------------------------------------")
        
    #Clusters generator
    def generate_clusters(self, max_distance, elements):
        # Generating directory and lat.in file
        cmd = 'makelat '+elements[0]+','+elements[1] +' '+ self.lattice_type_
        os.system(cmd)
        
        f = open(elements[0]+elements[1]+'_'+self.lattice_type_+'/lat.in','r')
        lines = f.readlines()
        f.close()
        
        retval = []
        
        #Generating str.in file
        f = open(elements[0]+elements[1]+'_'+self.lattice_type_+'/str.in','w')
        for i in range(3):
            f.write(lines[i])
            
        for vector in self.translation_vectors_:
            f.write(' '.join(str(x) for x in vector)+'\n')
            
        for atom,pos in self.source_positions_.items():
            for vector in pos:
                f.write(' '.join(str(x) for x in vector)+' '+atom+'\n')
        f.close()
        
        #Calculating correlations
        cmd = "(cd "+elements[0]+elements[1]+'_'+self.lattice_type_+";corrdump -s='str.in' -2="+max_distance+" -3="+max_distance+" -4="+max_distance+" > tmp.txt)"
        os.system(cmd)
        
        f = open(elements[0]+elements[1]+'_'+self.lattice_type_+'/tmp.txt','r')
        correlations_list = list(map(float, f.readlines()[0].split()))
        f.close()
        
        f = open(elements[0]+elements[1]+'_'+self.lattice_type_+'/clusters.out','r')
        clusters_read = ['']
        for line in f.readlines():
            clusters_read.append(line.strip())
        
        #List of cluster objects to be returned
        retval = []
        #Index position to iterate of correlations_list
        idx = 0
        #Generating cluster objects and appending to retval
        for i in range(len(clusters_read)-1):
            if clusters_read[i] == '':
                multiplicity = int(clusters_read[i+1])
                distance = float(clusters_read[i+2])
                number_of_points = int(clusters_read[i+3])
                i+=3
                points_positions = []
                for j in range(number_of_points):
                    i+=1
                    l = clusters_read[i]
                    points_positions.append([float(l.split()[k]) for k in range(3)])
                retval.append(cluster(correlations_list[idx], multiplicity, distance, number_of_points, points_positions))
                idx+=1
                
        f.close()
        
        # Removing the directory 
        cmd = 'rm -r '+elements[0]+elements[1]+'_'+self.lattice_type_
        os.system(cmd)
        
        return retval
            
            
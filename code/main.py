from parser_class import Parser
from structure_class import structure
from model_train_class import model_train
from structure_helper_class import structure_helper
from model_train_helper_class import model_train_helper
from ConvexHull import convex_hull

#Nb Ti V Zr
def main():
#    lattice_type = str(input("Enter lattice type : "))
#    file_name = str(input("Enter file name as <filename.txt> : "))
#    max_distance = float(input("Enter max. points distance : "))
    lattice_type = 'bcc'
    elements = ['Ti', 'V'] #don't invert
    max_distance = 3.4
#    elements = ['V', 'Nb'] #invert
#    max_distance = 3.516063
#    elements = ['Ti', 'Zr']
#    max_distance = 3.758550
#    elements = ['Nb', 'Zr']
#    max_distance = 3.758550
    file_name = elements[0]+'_'+elements[1]+'.txt'
    
    
    #Parsing the above entered file to get the list of parameters for all 
    #structures.
    try:
        file_name = elements[0]+'_'+elements[1]+'.txt'
        structures_parameters_list = Parser.parse(lattice_type, file_name)
    except:
        file_name = elements[1]+'_'+elements[0]+'.txt'
        structures_parameters_list = Parser.parse(lattice_type, file_name)
    
    pure_element_0_min_energy, pure_element_1_min_energy = structure_helper.get_pure_energies(
            structures_parameters_list, elements)     
    
    #Storing map from structure name to structure object for easier access.
    structure_name_to_object_map = {}
    #Getting the list of all the structure objects.
    for parameters in structures_parameters_list:
        try:
            structure_object = structure(parameters, str(max_distance), 
                                         elements, pure_element_0_min_energy, 
                                         pure_element_1_min_energy)
            structure_name_to_object_map[structure_object.name_] = structure_object
        except:
            continue        
    
#    composition_ratio_to_structure_names_list_ = structure_helper.get_composition_ratio_to_structure_names_list_map(
#            structure_name_to_object_map.values())
    
#    Printing the structures
#    for structure_object in structure_name_to_object_map.values():
#        structure_object.print()

    convex_hull.draw(structure_name_to_object_map)
    
    model_train_object = model_train(structure_name_to_object_map)
    
#    model_train_helper.verify_predictions(structure_name_to_object_map, 
#                                          model_train_object.lasso_object_, 'Lasso')

#    model_train_helper.verify_predictions(structure_name_to_object_map, 
#                                          model_train_object.lr_object_, 'LR')
#    convex_hull.draw(structure_name_to_object_map, model_train_object.lr_object_, 'LR')
    
#    model_train_helper.verify_predictions(structure_name_to_object_map, 
#                                          model_train_object.matinv_object_, 'Matrix Inversion')
    
# Calling main function
if __name__ == "__main__":
    main()

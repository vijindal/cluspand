class structure_helper:
    
    def get_all_elements_from_structures_list(structures_list):
        all_elements = set()
        for structure_object in structures_list:
            for element in structure_object.source_positions_.keys():
                all_elements.add(element)
        return list(all_elements)
    
    def get_pure_energies(structures_parameters_list, elements):
        pure_element_0_min_energy = None
        pure_element_1_min_energy = None
        for parameters in structures_parameters_list:
            if(len(parameters[3]) == 1 and elements[0] in parameters[3]):
                if pure_element_0_min_energy is not None:
                    pure_element_0_min_energy = min(pure_element_0_min_energy,
                                                    parameters[-1])
                else:
                    pure_element_0_min_energy = parameters[-1]
            if(len(parameters[3]) == 1 and elements[1] in parameters[3]):
                if pure_element_1_min_energy is not None:
                    pure_element_1_min_energy = min(pure_element_1_min_energy,
                                                    parameters[-1])
                else:
                    pure_element_1_min_energy = parameters[-1]
        
        assert(pure_element_0_min_energy != None)
        assert(pure_element_1_min_energy != None)
        return pure_element_0_min_energy, pure_element_1_min_energy
    
    def get_composition_ratio(structure_object, all_elements):
        x = 0.0
        y = 0.0
        #TODO : Generalize for more than binary.
        if all_elements[0] in structure_object.source_positions_:
            x = len(structure_object.source_positions_[all_elements[0]])
        if all_elements[1] in structure_object.source_positions_:
            y = len(structure_object.source_positions_[all_elements[1]])
        return y/(x+y)
    
    def get_composition_ratio_to_structure_names_list_map(structures_list):
        #Getting the union of elements present in all structures
        all_elements = structure_helper.get_all_elements_from_structures_list(structures_list)
    
        #Getting composition ratios for all structures:
        composition_ratio_to_structure_names_list_map = {}
        for structure_object in structures_list:
            composition_ratio = structure_helper.get_composition_ratio(structure_object, all_elements)
            if not composition_ratio in composition_ratio_to_structure_names_list_map:
                composition_ratio_to_structure_names_list_map[composition_ratio] = []
            composition_ratio_to_structure_names_list_map[composition_ratio].append(structure_object.name_)
        return composition_ratio_to_structure_names_list_map
    
    def get_min_energy_structure(structures_list):
        structures_list.sort(key=lambda x: x.total_energy_)
        return structures_list[0]
    
    def get_second_min_energy_structure(structures_list):
        structures_list.sort(key=lambda x: x.total_energy_)
        return structures_list[1]
        
        
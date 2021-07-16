from structure_helper_class import structure_helper

import numpy as np
import pandas as pd
from tabulate import tabulate

class model_train_helper:
    
    def get_prediction_dict(structure_name_to_object_map, model, model_str):
        
        composition_ratio_to_structure_names_list_map = structure_helper.get_composition_ratio_to_structure_names_list_map(structure_name_to_object_map.values())
        prediction_dict = {}
        for composition in sorted(composition_ratio_to_structure_names_list_map.keys()):
            structure_names_list = composition_ratio_to_structure_names_list_map[composition]
            
            name_to_energy_map = {}
            structure_objects_list = []
            
            for name in structure_names_list:
                structure_objects_list.append(structure_name_to_object_map[name])
            
            for structure_object in structure_objects_list:
                correlations = [x.correlation_ for x in structure_object.clusters_list_]
                multiplicities = [x.multiplicity_ for x in structure_object.clusters_list_]
                X = [a*b for a,b in zip(correlations, multiplicities)]
                predicted_energy = model.predict(np.array(X[2:]).reshape(1,-1))[0]
                if model_str == 'LR':
                    predicted_energy = predicted_energy[0]
                if model_str == 'Matrix Inversion':
                    predicted_energy = predicted_energy[0][0]
                name_to_energy_map[structure_object.name_] = predicted_energy
            
            prediction_dict[composition] = name_to_energy_map
            
        return prediction_dict
        
        
    # Given a model and all the structures, for each composition this function
    # predicts the total energy for every structure using the model and then
    # checks whether the structure predicted with minimum energy is same as
    # the actual structure with the minimum energy. This function also displays
    # the data generated in a tabular form.
    def verify_predictions(structure_name_to_object_map, model, model_str):
        composition_ratio_to_structure_names_list_map = structure_helper.get_composition_ratio_to_structure_names_list_map(structure_name_to_object_map.values())
        
        actual_struct_names_list = []
        actual_struct_actual_energy_list = []
        actual_struct_pred_energy_list = []
        pred_struct_names_list = []
        pred_struct_actual_energy_list = []
        pred_struct_pred_energy_list = []
        total_structs = []
        match = []
        
        for composition in sorted(composition_ratio_to_structure_names_list_map.keys()):
            structure_names_list = composition_ratio_to_structure_names_list_map[composition]
            
            structure_objects_list = []
            for name in structure_names_list:
                structure_objects_list.append(structure_name_to_object_map[name])
            
            prediction_dict = {}
            
            for structure_object in structure_objects_list:
                correlations = [x.correlation_ for x in structure_object.clusters_list_]
                multiplicities = [x.multiplicity_ for x in structure_object.clusters_list_]
                X = [a*b for a,b in zip(correlations, multiplicities)]
                predicted_energy = model.predict(np.array(X[2:]).reshape(1,-1))[0]
                prediction_dict[structure_object.name_] = predicted_energy
                
            actual_min_structure_name = structure_helper.get_min_energy_structure(structure_objects_list).name_
            pred_min_structure_name = min(prediction_dict.items(), key=lambda x: x[1])[0]
            
            actual_struct_names_list.append(actual_min_structure_name)
            actual_struct_actual_energy_list.append(structure_name_to_object_map[actual_min_structure_name].total_energy_)
            actual_struct_pred_energy_list.append(prediction_dict[actual_min_structure_name])
            pred_struct_names_list.append(pred_min_structure_name)
            pred_struct_actual_energy_list.append(structure_name_to_object_map[pred_min_structure_name].total_energy_)
            pred_struct_pred_energy_list.append(prediction_dict[pred_min_structure_name])
            total_structs.append(len(structure_names_list))
            if actual_min_structure_name == pred_min_structure_name:
                match.append('Yes')
            else:
                match.append('No')
        print('\n--------------------------------------------------------------')
        str = '\nResults from ' + model_str + ' :\n'
        print(str)
        pd.set_option('display.expand_frame_repr', False)
        df = pd.DataFrame({'Composition':sorted(composition_ratio_to_structure_names_list_map.keys()),
                           'Actual str':actual_struct_names_list, 
                           'Actual E (A)':actual_struct_actual_energy_list, 
                           'Pred E (A)':actual_struct_pred_energy_list, 
                           'Pred str':pred_struct_names_list, 
                           'Actual E (P)':pred_struct_actual_energy_list, 
                           'Pred E (P)':pred_struct_pred_energy_list,
                           'Total structures':total_structs,
                           'Match?':match})
        df.set_index('Composition')
        print(tabulate(df, headers='keys', tablefmt='psql'))  
            
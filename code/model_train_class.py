from structure_helper_class import structure_helper
from matrix_inversion_class import matrix_inversion

import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.linear_model import LinearRegression
from tabulate import tabulate
from ConvexHull import convex_hull

class model_train:
    
    #Constructor.
    def __init__(self, structure_name_to_object_map):
        self.hull_structures_list_ = self.generate_hull_structures_for_training_data(structure_name_to_object_map, True)
        self.X_training_datasets_list_, self.Y_training_datasets_list_, self.training_datasets_structure_names_list_ = self.generate_training_datasets_list(structure_name_to_object_map)
#        self.testing_dataset_structures_list_ = self.generate_structures_for_testing_data(structure_name_to_object_map)
#        self.X_training_data_, self.Y_training_data_ = self.generate_data_vectors('train')
#        self.X_testing_data_, self.Y_testing_data_ = self.generate_data_vectors('test')
#        self.lasso_object_ = self.get_lasso_object(structure_name_to_object_map)
#        self.lr_object_ = self.get_lr_object(structure_name_to_object_map)
        self.matinv_object_ = self.get_matinv_object(structure_name_to_object_map)
    
    #Generates a list of hull structures.
    def generate_hull_structures_for_training_data(self, structure_name_to_object_map, display_training_structs = False):
        hull_structures_list = []
        points_on_hull = convex_hull.get_convex_hull_points(structure_name_to_object_map,
                                                            False)
        for point in points_on_hull:
            hull_structures_list.append(point)
        
        if display_training_structs:
            print('\nHull structures :')
            for point in hull_structures_list:
                structure_name_to_object_map[point[2]].print()
                
        return hull_structures_list
    
    #Generates a list of training datasets
    def generate_training_datasets_list(self, structure_name_to_object_map):
        structure_names_hull = []
        X_hull = []
        Y_hull = []
        for point in self.hull_structures_list_:
            structure_object = structure_name_to_object_map[point[2]]
            correlations = [x.correlation_ for x in structure_object.clusters_list_]
            multiplicities = [x.multiplicity_ for x in structure_object.clusters_list_]
            x = [a*b for a,b in zip(correlations, multiplicities)]
            X_hull.append(x[2:])
            Y_hull.append([structure_object.total_energy_])
            structure_names_hull.append(point[2])
        assert(len(X_hull)<=4)
        
        X_training_datasets_list = []
        Y_training_datasets_list = []
        training_datasets_structure_names_list = []
        
        if len(X_hull) == 4:
            X_training_datasets_list.append(np.array(X_hull))
            Y_training_datasets_list.append(np.array(Y_hull))
            training_datasets_structure_names_list.append(np.array(structure_names_hull))
            
        elif len(X_hull) == 3:
            for structure_name, structure_object in structure_name_to_object_map.items():
                if structure_name not in [p[2] for p in self.hull_structures_list_]:
                    correlations = [x.correlation_ for x in structure_object.clusters_list_]
                    multiplicities = [x.multiplicity_ for x in structure_object.clusters_list_]
                    x = [a*b for a,b in zip(correlations, multiplicities)]
                    X_hull.append(x[2:])
                    Y_hull.append([structure_object.total_energy_])
                    structure_names_hull.append(structure_name)
                    X_training_datasets_list.append(np.array(X_hull))
                    Y_training_datasets_list.append(np.array(Y_hull))
                    training_datasets_structure_names_list.append(np.array(structure_names_hull))
                    X_hull.pop()
                    Y_hull.pop()
                    structure_names_hull.pop()
        
        elif len(X_hull) == 2:
            for structure_name, structure_object in structure_name_to_object_map.items():
                if structure_name not in structure_names_hull:
                    correlations = [x.correlation_ for x in structure_object.clusters_list_]
                    multiplicities = [x.multiplicity_ for x in structure_object.clusters_list_]
                    x = [a*b for a,b in zip(correlations, multiplicities)]
                    X_hull.append(x[2:])
                    Y_hull.append([structure_object.total_energy_])
                    structure_names_hull.append(structure_name)
                    for structure_name, structure_object in structure_name_to_object_map.items():
                        if structure_name not in structure_names_hull:
                            correlations = [x.correlation_ for x in structure_object.clusters_list_]
                            multiplicities = [x.multiplicity_ for x in structure_object.clusters_list_]
                            x = [a*b for a,b in zip(correlations, multiplicities)]
                            X_hull.append(x[2:])
                            Y_hull.append([structure_object.total_energy_])
                            structure_names_hull.append(structure_name)
                            X_training_datasets_list.append(np.array(X_hull))
                            Y_training_datasets_list.append(np.array(Y_hull))
                            training_datasets_structure_names_list.append(np.array(structure_names_hull))
                            X_hull.pop()
                            Y_hull.pop()
                            structure_names_hull.pop()
                    X_hull.pop()
                    Y_hull.pop()
                    structure_names_hull.pop()

        return X_training_datasets_list, Y_training_datasets_list, training_datasets_structure_names_list
        
    def get_matinv_object(self, structure_name_to_object_map):
        print('--------------------------------------------------------------')
        print('Matrix Inversion:')
        X_data = []
        Y_data = []
        for structure_object in structure_name_to_object_map.values():
            correlations = [x.correlation_ for x in structure_object.clusters_list_]
            multiplicities = [x.multiplicity_ for x in structure_object.clusters_list_]
            x = [a*b for a,b in zip(correlations, multiplicities)]
            X_data.append(x[2:])
            Y_data.append([structure_object.total_energy_])
    
        matrix_inversion_object = matrix_inversion(self.X_training_datasets_list_, 
                                                   self.Y_training_datasets_list_,
                                                   self.training_datasets_structure_names_list_,
                                                   np.array(X_data), 
                                                   np.array(Y_data))
        
        print('\nCECs = \n', matrix_inversion_object.CEC_best_)
        print('\nStructures used = ', matrix_inversion_object.used_structure_names_list)
        convex_hull.draw(structure_name_to_object_map, True, matrix_inversion_object, 'Matrix Inversion')
        return matrix_inversion_object
        
    
#    def get_lasso_object(self, structure_name_to_object_map):
#        print('--------------------------------------------------------------')
#        print('Lasso :')
#        alphas = [0.0001, 0.0003, 0.0007, 0.001, 0.003, 0.007, 0.01, 0.03, 0.07]
#        lasso_list = []
#        for alpha_ in alphas:
#            lasso = Lasso(alpha=alpha_)
#            lasso.fit(self.X_training_datasets_list_[0], self.Y_training_datasets_list_[0])
#            train_score=lasso.score(self.X_training_datasets_list_[0], self.Y_training_datasets_list_[0])
#            lasso_list.append((train_score, lasso))
#        lasso_list.sort(key = lambda x: x[0], reverse = True)
#        lasso_best = lasso_list[0][1]
#        test_score=lasso_best.score(self.X_training_datasets_list_[0], self.Y_training_datasets_list_[0])
#        print("\nLasso test score =", test_score)
#        print("\nFor training data:\n")
#        results = pd.DataFrame({'Actual':self.Y_training_datasets_list_[0][:,0], 'Predicted':lasso_best.predict(self.X_training_datasets_list_[0])[:]})
#        print(tabulate(results, headers='keys', tablefmt='psql'))
##        print("\nFor testing data:\n")
##        results = pd.DataFrame({'Actual':self.Y_testing_data_[:,0], 'Predicted':lasso_best.predict(self.X_testing_data_)[:]})
##        print(tabulate(results, headers='keys', tablefmt='psql'))
#        print("\nCECs =\n", lasso_best.coef_.reshape(4,1))
##        convex_hull.draw(structure_name_to_object_map, lasso_best, 'Lasso')
##        return lasso_best
    
#    def get_lr_object(self, structure_name_to_object_map):
#        print('--------------------------------------------------------------')
#        print('Linear Regression :')
#        lr = LinearRegression()
#        lr.fit(self.X_training_data_, self.Y_training_data_)
#        lr_test_score=lr.score(self.X_testing_data_, self.Y_testing_data_)
#        print("\nLR test score =",lr_test_score)
#        print("\nFor training data:\n")
#        results = pd.DataFrame({'Actual':self.Y_training_data_[:,0], 'Predicted':lr.predict(self.X_training_data_)[:,0]})
#        print(tabulate(results, headers='keys', tablefmt='psql'))
#        print("\nFor testing data:\n")
#        results = pd.DataFrame({'Actual':self.Y_testing_data_[:,0], 'Predicted':lr.predict(self.X_testing_data_)[:,0]})
#        print(tabulate(results, headers='keys', tablefmt='psql'))
#        print("\nCECs =\n", lr.coef_.reshape(15,1))
#        return lr
        
    
        
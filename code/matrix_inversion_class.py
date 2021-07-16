from structure_helper_class import structure_helper
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score
from tabulate import tabulate

class matrix_inversion:
    
    def __init__(self, X_matrices, Y_matrices, structure_names_list, X_data, Y_data):
        self.X_matrices_ = X_matrices
        self.Y_matrices_ = Y_matrices
        self.structure_names_list_ = structure_names_list
        self.X_inverted_matrices_ = self.generate_inverted_matrices()
        self.CEC_list_ = self.generate_CEC_list()
        self.CEC_best_, self.used_X_matrices, self.used_structure_names_list = self.get_best_CEC(X_data, Y_data)
    
    def generate_inverted_matrices(self, display_matrix = False):
        X_inverted_matrices = []
        y_index_to_delete = []
        for i,matrix in enumerate(self.X_matrices_):
            try:
                if display_matrix:
                    print('\nMatrix to be inverted :')
                    print(matrix)
                inv_matrix = np.linalg.inv(matrix)
                if display_matrix:
                    print('\nInverted matrix :')
                    print(inv_matrix)
                X_inverted_matrices.append(inv_matrix)
            except:
                y_index_to_delete.append(i)
        self.X_matrices_ = [i for j, i in enumerate(self.X_matrices_) if j not in y_index_to_delete]
        self.Y_matrices_ = [i for j, i in enumerate(self.Y_matrices_) if j not in y_index_to_delete]
        self.structure_names_list_ = [i for j, i in enumerate(self.structure_names_list_) if j not in y_index_to_delete]
        assert(len(self.Y_matrices_) != 0)
        return X_inverted_matrices
    
    def generate_CEC_list(self, display_CECs = False):
        CEC_list = [np.matmul(a,b) for a,b in zip(self.X_inverted_matrices_, self.Y_matrices_)]
        if display_CECs:
            print('\nCECs:\n')
            for CEC in CEC_list:
                print(CEC)
        return CEC_list

    def get_best_CEC(self, X_data, Y_data, print_results = False):
        error_to_CEC_index_map_ = {}
        predictions_list = []
        for index in range(len(self.CEC_list_)):
            error = 0
            for i,row in enumerate(X_data):
                error += (np.matmul(row.reshape(1,4), self.CEC_list_[index])-Y_data[i])**2
            error_to_CEC_index_map_[error[0][0]] = index
        min_error = min(error_to_CEC_index_map_.keys())
        print(min_error)
        if print_results:
            predictions = (np.array(predictions_list[error_to_CEC_index_map_[min_error]])).reshape(np.shape(Y_data))
            print('\nMatrix Inversion error = ', min_error)
            results = pd.DataFrame({'Actual':Y_data[:,0], 'Predicted':predictions[:,0]})
            print('\nFor training data:\n')
            print(tabulate(results, headers='keys', tablefmt='psql'))
        index = error_to_CEC_index_map_[min_error]
        return self.CEC_list_[index], self.X_matrices_[index], self.structure_names_list_[index]
    
    def predict(self, X_input):
        predictions = []
        for row in X_input:
            predictions.append(np.matmul(row.reshape(1,4), self.CEC_best_))
        return np.array(predictions)
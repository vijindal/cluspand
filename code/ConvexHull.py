from structure_helper_class import structure_helper
from model_train_helper_class import model_train_helper

import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

class convex_hull:
    
    def get_convex_hull_points(structure_name_to_object_map, draw_hull = True, model = None, model_str = None):
        
        #Getting a map from composition ratio to list of structure names
        composition_ratio_to_structure_names_list_map = structure_helper.get_composition_ratio_to_structure_names_list_map(structure_name_to_object_map.values())
        
        points = []
        points_x = []
        points_y = []
        
        if model is not None:
            prediction_dict = model_train_helper.get_prediction_dict(structure_name_to_object_map, model, model_str)
            for composition, name_to_energy_map in prediction_dict.items():
                for name, energy in name_to_energy_map.items():
                    if name not in model.used_structure_names_list:
                        continue
                    points.append((composition, energy, name))
                    points_x.append(composition)
                    points_y.append(energy)
                    
        else:
            for composition, structure_names in composition_ratio_to_structure_names_list_map.items():
                for name in structure_names:
                    points.append((composition, structure_name_to_object_map[name].total_energy_, name))
                    points_x.append(composition)
                    points_y.append(structure_name_to_object_map[name].total_energy_)
        
        """Computes the convex hull of a set of 2D points.
    
        Input: an iterable sequence of (x, y) pairs representing the points.
        Output: a list of vertices of the convex hull in counter-clockwise order,
          starting from the vertex with the lexicographically smallest coordinates.
        Implements Andrew's monotone chain algorithm. O(n log n) complexity.
        """
        # Sort the points lexicographically (tuples are compared lexicographically).
        # Remove duplicates to detect the case we have just one unique point.
        points = sorted(set(points))
    
        # Boring case: no points or a single point, possibly repeated multiple times.
        if len(points) <= 1:
            return points
        lower = []
        # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
        # Returns a positive value, if OAB makes a counter-clockwise turn,
        # negative for clockwise turn, and zero if the points are collinear.
        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        if draw_hull:
            plt.scatter(points_x, points_y, marker='.')
        return lower
        
    def draw(structure_name_to_object_map, draw_hull = True, model = None, model_str = None):
    
        # Build lower hull 
        lower = convex_hull.get_convex_hull_points(structure_name_to_object_map, 
                                                   draw_hull, model, model_str)            
        print('\nPoints used for Convex Hull :\n')
        pd.set_option('display.expand_frame_repr', False)
        df = pd.DataFrame({'Composition':[lower[i][0] for i in range(len(lower))],
                           'Structure name':[lower[i][2] for i in range(len(lower))],
                           'Structure energy':[lower[i][1] for i in range(len(lower))]})
        df.set_index('Composition')
        print(tabulate(df, headers='keys', tablefmt='psql'))
            
        lower_x = [lower[i][0] for i in range(len(lower))]
        lower_y = [lower[i][1] for i in range(len(lower))]
        if draw_hull:
            plt.plot(lower_x, lower_y , marker='.', color='black')
            plt.show()
    

# Class for cluster information

class cluster:
    
    #Constructor
    def __init__(self, correlation, multiplicity, distance, number_of_points, points_positions):
        self.correlation_ = correlation
        self.multiplicity_ = multiplicity
        self.distance_ = distance
        self.number_of_points_ = number_of_points
        self.points_positions_ = points_positions


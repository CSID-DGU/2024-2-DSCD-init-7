import numpy as np
import itertools


def generate_combinations_3d(data, num_parts=5):
    # Convert data to numpy array for easier manipulation
    data_values = data.values
    
    # Split data into equal parts
    part_size = len(data_values) // num_parts
    parts = [data_values[i * part_size:(i + 1) * part_size] for i in range(num_parts)]
    
    # Generate all possible combinations from the parts (row-wise combinations)
    combinations = list(itertools.product(*parts))
    
    # Convert combinations to a 3D numpy array
    combinations_3d = np.array(combinations)
    
    return combinations_3d
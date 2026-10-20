import numpy as np
from utils.voice_features import extract_voice_features

def verify_voice_match(file_path, stored_vector, threshold=50):
    input_vec = extract_voice_features(file_path)

    distance = np.linalg.norm(input_vec - stored_vector)

    return (distance < threshold), float(distance)

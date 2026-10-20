import librosa
import numpy as np

def extract_voice_features(file_path):
    y, sr = librosa.load(file_path, sr=None)

    # remove silence noise
    y, _ = librosa.effects.trim(y, top_db=25)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
    mfcc_mean = np.mean(mfcc.T, axis=0)

    return mfcc_mean

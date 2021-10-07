from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from util.model import HierarchicalPoissonRegression 
from joblib import load
import numpy as np


pipeline = None
labelencoder = None
label_to_id = {}


def load_model():
    global pipeline
    global labelencoder
    global label_to_id
    pipeline = load('trained_model.joblib')
    labelencoder = load('label_encoder.joblib')
    label_to_id = {}
    for i, l in enumerate(labelencoder.classes_):
        label_to_id[l] = np.array([i])


def get_subject_group(label):
    return label_to_id.get(label, None)


def predict(subject_group, eda, hr, offload = 0):
    # n-samples paramter weighs time against accuracy of the result, keep low for realtime estimates
    return pipeline.predict(np.array([[eda, hr, offload]]), group=subject_group, n_samples=100)
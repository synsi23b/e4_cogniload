from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import os
from joblib import load

from util.preprocessing import load_proprocessed_subject_data

subjects = [f for f in os.listdir('dataset') if '.' not in f]
subject_count = len(subjects)
dfs = []
for sub in subjects:
    df = load_proprocessed_subject_data(sub)
    df['subject'] = sub
    dfs.append(df)
data = pd.concat(dfs)

pipe = load('trained_model.joblib')
le = load('label_encoder.joblib')

# prepare data
data = data[data.score != 0] # remove rest period
y = data.score.to_numpy() # we are predicting backward digit span scores
X = data[['EDA', 'HR', 'offload']].to_numpy() # these are our predictors 
subj = le.fit_transform(data.subject.to_numpy()) # convert subj IDs to integer codes

subid_group_map = {}
subid_x_map = {}
subid_y_map = {}
for sub in subjects:
    subid_group_map[sub] = subj[subj == sub]
    subid_x_map[sub] = X[subj == sub]
    subid_y_map[sub] = y[subj == sub]

def plot_subj(sub):
    yhat = pipe.predict(X[subj == sub], group = subj[subj == sub])
    ysub = y[subj == sub]

    plt.scatter(ysub, yhat)
    plt.xlabel('actual score')
    plt.ylabel('predicted score')
    plt.title('model predictions for subject %d'%sub)
    plt.show()

# for example 6
plot_subj(6)

def plot_subj_new(data, group, ysub):
    #yhat = pipe.predict(X[subj == sub], group = subj[subj == sub])
    yhat = pipe.predict(data, group=group)
    #ysub = y[subj == sub]

    plt.scatter(ysub, yhat)
    plt.xlabel('actual score')
    plt.ylabel('predicted score')
    plt.title('model predictions for subject %d'%sub)
    plt.show()

for sub in subjects:
    group = subid_group_map[sub]
    x = subid_x_map[sub]
    y = subid_y_map[sub]
    plot_subj_new(x, group, y)
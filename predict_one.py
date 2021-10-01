# you'll need to remind Python of the class definitions if in a new process
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from util.model import HierarchicalPoissonRegression 
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import os
from joblib import load
from util.preprocessing import load_proprocessed_subject_data


# subjects = [f for f in os.listdir('dataset') if '.' not in f]
# subject_count = len(subjects)
# dfs = []
# for sub in subjects:
#     df = load_proprocessed_subject_data(sub)
#     df['subject'] = sub
#     dfs.append(df)
# data = pd.concat(dfs)

pipe = load('trained_model.joblib')
le = load('label_encoder.joblib')
label_to_sub = {}
for i, l in enumerate(le.classes_):
    label_to_sub[l] = i


# prepare data
# data = data[data.score != 0] # remove rest period
# y = data.score.to_numpy() # we are predicting backward digit span scores
# X = data[['EDA', 'HR', 'offload']].to_numpy() # these are our predictors 
# subj = le.transform(data.subject.to_numpy()) # convert subj IDs to integer codes


# def plot_subj(sub):
#     yhat = pipe.predict(X[subj == sub], group = subj[subj == sub])
#     ysub = y[subj == sub]

#     plt.scatter(ysub, yhat)
#     plt.xlabel('actual score')
#     plt.ylabel('predicted score')
#     plt.title('model predictions for subject %d'%sub)
#     plt.show()

# for example 6
#plot_subj(6)


# label_group_map = {}
# label_x_map = {}
# label_y_map = {}
# for label in subjects:
#     sub = label_to_sub[label]
#     label_group_map[label] = subj[subj == sub]
#     label_x_map[label] = X[subj == sub]
#     label_y_map[label] = y[subj == sub]


# def plot_subj_new(data, group, ysub, sub):
#     #yhat = pipe.predict(X[subj == sub], group = subj[subj == sub])
#     yhat = pipe.predict(data, group=group)
#     #ysub = y[subj == sub]
#     plt.scatter(ysub, yhat)
#     plt.xlabel('actual score')
#     plt.ylabel('predicted score')
#     plt.title(f'model predictions for subject {sub}')
#     plt.show()


#for sub in subjects:
#    group = label_group_map[sub]
#    x = label_x_map[sub]
#    y = label_y_map[sub]
#    plot_subj_new(x, group, y, sub)

def predict_new(eda, hr, sub_id):
    # offload always zero? always one?
    data = np.array([[eda, hr, 0], [eda, hr, 1]])
    sub = np.array([sub_id]*len(data))
    return pipe.predict(data, group=sub)

value = predict_new(0.02, 86, 8)
print(value)
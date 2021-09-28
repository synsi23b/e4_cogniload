
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from time import time
import os
from util.preprocessing import load_proprocessed_subject_data
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import mean_absolute_error
#from util.preprocessing import StandardScaler
from util.model import HierarchicalPoissonRegression # custom model
from joblib import dump

subjects = [f for f in os.listdir('dataset') if '.' not in f]
subject_count = len(subjects)
dfs = []
for sub in subjects:
    df = load_proprocessed_subject_data(sub)
    df['subject'] = sub
    dfs.append(df)
data = pd.concat(dfs)
#data.head()

# build model pipeline 
le = LabelEncoder()
pipe = Pipeline([
    ('scaler', StandardScaler()), # standardize predictor variables
    ('glm', HierarchicalPoissonRegression()) # regression
])

# prepare data
data = data[data.score != 0] # remove rest period
y = data.score.to_numpy() # we are predicting backward digit span scores
X = data[['EDA', 'HR', 'offload']].to_numpy() # these are our predictors 
subj = le.fit_transform(data.subject.to_numpy()) # convert subj IDs to integer codes

# test model performance on hold-out (test) data
logo = LeaveOneGroupOut() # hold out blocks
cv_scores = []
for train, test in logo.split(X, y, data.block):
    pipe.fit(
        X[train,:], y[train], 
        glm__group = subj[train], 
        glm__inference_type = 'nuts'
    )
    yhat = pipe.predict(X[test,:], group = subj[test])
    loss = mean_absolute_error(y[test], yhat)
    cv_scores.append(loss)

# Note that part of the reason the model seems to perform so well is that it remembers 
# information about the mean of each subject. What we really care about is its predictive 
# power _within_ a subject, which isn't always as great as it is for the full dataset. 
# That said, let's fit now the full model and see what its predictions look like.
print("The model is, on average, {:.2f} points off.".format(np.mean(cv_scores)))

pipe.fit(X, y, glm__group = subj, glm__inference_type = 'nuts')

# To make predictions, the model draws samples from the Bayesian posterior distribution p(score | EDA, HR, offload). 
# The more samples it draws, the better its approximation to the posterior will be. However, drawing samples takes time, 
# and you want predictions to be generated quickly. So there's a tradeoff between precision and speed that you can toggle 
# with the `n_samples` parameter at inference time. I've set the default value to 100, but you can alter it to your needs.
t1 = time()
num = 100
yhat = pipe.predict(X, group = subj, n_samples = num)
t2 = time()
print("With {:.0f} samples, predictions take {:.2f} seconds".format(num, t2 - t1))

plt.scatter(y, yhat)
plt.xlabel('actual score')
plt.ylabel('predicted score')
plt.title('model predictions for all subjects')
plt.show()

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

# Of course all these predictions are off of single samples of EDA/HR, and you'll want to consider multiple samples at once. 
# I'm guessing performance will improve when aggregating across time. Just maintain a rolling average of the model predictions.

# You can also use the model to predict the probability that the score falls with an interval, 
# rather than just a point prediction. This is useful if you're trying to predict whether a subject 
# is going to fall below a certain performance threshold. For some obscure `sklearn` reasons, 
# the syntax for making this prediction is slightly more complicated
proba = pipe[-1].predict_proba(pipe[0].transform(X), group = subj, high = 5, low = 0)
# When you train a model, it's always a good idea to look at the fitted parameters, so their posterior distributions are plotted below.
ax = pipe[-1].plot_posterior()
# One last thing to note is that the model predictions depend on the value of `offload` 
# (or in the original dataset termonology, the `help` indicator), which is obviously 
# confounded with the subjects' level of cognitive effort. Since you're going to have robots 
# offer help when the subject's performance is predicted to be low (relative to their own performance), 
# predictions may not be reliable immediately after help is initiated. 
# 
# Thus, you should allow an appropriate adjustment period after help begins. 
# (I don't know what an "appropriate" adjustment period is, 
# I assume just until the EDA has had time to level off. You'll have to use your judgement.


#save model and ID-to-integer thing
dump(pipe, 'trained_model.joblib') # stores model
dump(le, 'label_encoder.joblib') # stores subject ID to int code crosswalk
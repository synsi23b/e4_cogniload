import pandas as pd
import numpy as np
import os

from scipy.signal import butter, lfilter
from sklearn.preprocessing import StandardScaler as Scaler
from sklearn.base import TransformerMixin


def load_data(sub, data_type):
	fpath = os.path.join('dataset', sub, '%s.csv'%data_type)
	with open(fpath, 'r') as f:
		tmin = float(f.readline().split(',')[0])
		fs = float(f.readline().split(',')[0])
		if data_type == 'ACC':
			hdr = ['x', 'y', 'z']
		else:
			hdr = [data_type]
		df = pd.read_csv(f, names = hdr)
	times = np.array(range(df.shape[0]))/fs + tmin
	df['timestamps'] = times
	return df, fs

def load_tags(sub):
	fpath = os.path.join('dataset', sub, 'tags.csv')
	with open(fpath, 'r') as f:
		txt = f.read()
	tags = [float(s) for s in txt.split('\n') if s]
	tags = np.array(tags)
	return tags

def load_indicators(sub, tags):
	fpath = os.path.join('.', 'score_and_help_indicator.csv')
	ind = pd.read_csv(fpath)
	loads = [ind['%dbds'%(trial+1)].loc[ind.name == sub].values[0] 
		 for trial in range(tags.shape[0]//2-1)]
	offload = [ind['%dhelp'%(trial+1)].loc[ind.name == sub].values[0] 
		 for trial in range(tags.shape[0]//2-1)]
	loads = np.array([0] + loads) # starts with rest a.k.a. no load
	offload = np.array([0] + offload)
	return loads, offload

def load_proprocessed_subject_data(sub):

	# load data
	eda, eda_fs = load_data(sub, 'EDA')
	hr, hr_fs = load_data(sub, 'HR')
	acc, acc_fs = load_data(sub, 'ACC')

	# create anti-alias filter
	fs = min(eda_fs, hr_fs, acc_fs) # the lowest sampling rate
	lc = fs/2 # lowpass cutoff frequency 
	def lowpass(sgnl, sgnl_srate):
		b, a = butter(1, lc, btype = 'highpass', fs = sgnl_srate)
		return lfilter(b, a, sgnl)
	def lowpass_df(sgnl_df):
		t = sgnl_df.timestamps
		dat_fs = 1/(t[1] - t[0])
		for col in sgnl_df.columns:
			if col != 'timestamps':
				dat = sgnl_df[col]
				sgnl_df[col] = lowpass(dat, dat_fs)
		return sgnl_df

	# we don't need to lowpass HR cause it's already the lowest freq
	eda = lowpass_df(eda)
	acc = lowpass_df(acc)

	data = pd.merge_asof(hr, eda, on = 'timestamps')
	data = pd.merge_asof(data, acc, on = 'timestamps')
	data.dropna(inplace = True)
	data['score'] = 0 # placeholder
	data['offload'] = 0 # placeholder 

	tags = load_tags(sub)
	scores, offloads = load_indicators(sub, tags)

	dfs = []
	for i in range(len(scores)):
		ii = i*2
		jj = ii + 1
		ends = (tags[ii], tags[jj])
		trial = (data.timestamps > ends[0]) & (data.timestamps < ends[1])
		df = data[trial]
		df.score = scores[i]
		df.offload = offloads[i]
		df['block'] = i
		dfs.append(df)   
	df = pd.concat(dfs)
	df = df.drop(columns = ['timestamps'])
	m = np.max(df.score)
	df['delta'] = m - df.score # difference from max score
	return df






	# 














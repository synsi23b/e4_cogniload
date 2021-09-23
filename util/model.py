import numpy as np
import pymc3 as pm
import theano
import theano.tensor as tt

from pmlearn.base import BayesianModel, BayesianRegressorMixin
from pmlearn.exceptions import NotFittedError

class HierarchicalPoissonRegression(BayesianModel, BayesianRegressorMixin):
	"""
	Custom Hierachical Poisson Regression built using PyMC3.
	"""

	def __init__(self):
		super(HierarchicalPoissonRegression, self).__init__()
		self.num_cats = None # number of categories for mutlilevel model

	def create_model(self):
		"""
		Creates and returns the PyMC3 model.
		Note: The size of the shared variables must match the size of the
		training data. Otherwise, setting the shared variables later will
		raise an error. See http://docs.pymc.io/advanced_theano.html
		Returns
		----------
		the PyMC3 model
		"""
		model_input = theano.shared(
			np.zeros([self.num_training_samples, self.num_pred]))

		model_output = theano.shared(
			np.zeros(self.num_training_samples, dtype = 'int'))

		model_cats = theano.shared(
			np.zeros(self.num_training_samples, dtype = 'int'))

		self.shared_vars = {
			'model_input': model_input,
			'model_output': model_output,
			'model_cats': model_cats
		}

		model = pm.Model()

		with model:
			mu_alpha = pm.Normal('mu_alpha', mu = 0, sd = 1)
			sigma_alpha = pm.HalfNormal('sigma_alpha', sd = 1)

			mu_beta = pm.Normal('mu_beta', mu = 0, sd = 1)
			sigma_beta = pm.HalfNormal('sigma_beta', sd = 1)

			alpha = pm.Normal('alpha', mu = mu_alpha, sd = sigma_alpha,
							  shape = (self.num_cats,))
			betas = pm.Normal('beta', mu = mu_beta, sd = sigma_beta,
							  shape = (self.num_cats, self.num_pred))

			c = model_cats

			linear_function = alpha[c] + tt.sum(betas[c] * model_input, 1)

			# exponential link function
			mu = np.exp(linear_function)
			# and poisson likelihood 
			y = pm.Poisson("y", mu = mu, observed = model_output)

		return model

	def save(self, file_prefix):
		params = {
			'inference_type': self.inference_type,
			'num_cats': self.num_cats,
			'num_pred': self.num_pred,
			'num_training_samples': self.num_training_samples
		}

		super(HierarchicalPoissonRegression, self).save(file_prefix, params)

	def load(self, file_prefix):
		params = super(HierarchicalPoissonRegression,
					   self).load(file_prefix, load_custom_params = True)

		self.inference_type = params['inference_type']
		self.num_cats = params['num_cats']
		self.num_pred = params['num_pred']
		self.num_training_samples = params['num_training_samples']

	def fit(self, X, y, group, inference_type = 'advi', minibatch_size = None,
			inference_args=None):
		"""
		Train the Hierarchical Regression model
		Parameters
		----------
		X : numpy array, shape [n_samples, n_features]
		y : numpy array, shape [n_samples, ]
		group : e.g. subject ID, numpy array, shape [n_samples, ]
		inference_type : string, specifies which inference method to call.
		   Defaults to 'advi'. Currently, only 'advi' and 'nuts' are supported
		minibatch_size : number of samples to include in each minibatch for
		   ADVI, defaults to None, so minibatch is not run by default
		inference_args : dict, arguments to be passed to the inference methods.
		   Check the PyMC3 docs for permissable values. If no arguments are
		   specified, default values will be set.
		"""
		cats = group # to be consistent with pymc-learn source code
		self.num_cats = len(np.unique(cats))
		self.num_training_samples, self.num_pred = X.shape

		self.inference_type = inference_type

		if y.ndim != 1:
			y = np.squeeze(y)

		if not inference_args:
			inference_args = self._set_default_inference_args()

		self.cached_model = self.create_model()

		if minibatch_size:
			with self.cached_model:
				minibatches = {
					self.shared_vars['model_input']: pm.Minibatch(
						X, batch_size = minibatch_size),
					self.shared_vars['model_output']: pm.Minibatch(
						y, batch_size = minibatch_size),
					self.shared_vars['model_cats']: pm.Minibatch(
						cats, batch_size = minibatch_size)
				}

				inference_args['more_replacements'] = minibatches
		else:
			self._set_shared_vars({
				'model_input': X,
				'model_output': y,
				'model_cats': cats
			})
	
		self._inference(inference_type, inference_args)

		return self

	def predict(self, X, group, n_samples = 100):
		"""
		Predicts values of new data with a trained Linear Regression model
		Parameters
		----------
		X : numpy array, shape [n_samples, n_features]
		group: level from which to predict (e.g. what subject is this)
		return_std : Boolean flag
		   Boolean flag of whether to return standard deviations with mean
		   values. Defaults to False.
		"""

		if self.trace is None:
			raise NotFittedError('Run fit on the model before predict.')

		num_samples = X.shape[0]

		if self.cached_model is None:
			self.cached_model = self.create_model()

		self._set_shared_vars({'model_input': X,
							   'model_output': np.zeros(num_samples).astype(int),
							   'model_cats': group})

		ppc = pm.fast_sample_posterior_predictive(
			self.trace, 
			model = self.cached_model, 
			samples = n_samples
			)

		return ppc['y'].mean(axis = 0)

	def predict_proba(self, X, group, high, low = 0, n_samples = 100):
		'''
		Returns probability that y is in interval [low, high)
		'''

		if self.trace is None:
			raise NotFittedError('Run fit on the model before predict.')

		num_samples = X.shape[0]

		if self.cached_model is None:
			self.cached_model = self.create_model()

		self._set_shared_vars({'model_input': X,
							   'model_output': np.zeros(num_samples).astype(int),
							   'model_cats': group})

		ppc = pm.fast_sample_posterior_predictive(
			self.trace, 
			model = self.cached_model, 
			samples = n_samples
			)

		return np.mean(np.logical_and(ppc['y'] >= low, ppc['y'] < high))

	def score(self, X, y, group, n_samples = 1000):
		"""
		Scores new data with a trained model.
		Parameters
		----------
		X : numpy array, shape [n_samples, n_features]
		y : numpy array, shape [n_samples, ]
		cats : numpy array, shape [n_samples, ]
		"""
		from sklearn.metrics import mean_poisson_deviance
		return mean_poisson_deviance(y, self.predict(X, group, n_samples))

	def plot_posterior(self):
		'''
		plots posterior distributions and traces for all parameters
		'''
		from arviz import from_pymc3, plot_trace
		if self.trace is None:
			raise NotFittedError('Run fit on the model before predict.')
		trc = from_pymc3(self.trace)
		ax = plot_trace(trc)
		return ax



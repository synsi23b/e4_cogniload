Example code for training the model, as well as for saving and loading the pretrained model, is found in `fit-model.ipynb`. The source code for the model itself, as well as some functions to help preprocess the data, are found in the `util` directory, which can be imported as a Python module.

To install the dependencies, I recommend loading `environment.py` with Anaconda using the command `conda env create --file environment.yml`. One of the dependencies, `pymc-learn`, will cause a whole lot of trouble if you `pip install` it (specifically, it will install of conflicting version of Theano that breaks newer version of `pymc3`), so it must be installed from my [fork](https://github.com/john-veillette/pymc-learn) of the package. The conda environment file should do this for you automatically.

after installing the evironment, it can be activated by using
`source ~/anaconda3/bin/activate && conda activate eda`

add data into the dataset folder organized by the subject names. these should also appear in the score_and_help_indicator.csv (xlsx version is just there to creat the csv, if thats what you prefer)

than run `python3 retrain_modell.py` to add the new people to the pretrained model. 
Than look at README.md
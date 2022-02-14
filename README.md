e4_cogniload

# Installation

the model runs inside a conda environment, the setup of that is described README_modell.md

# Information about the machine learning model

detailed information is in README_modell.md, email.txt and fit_modell.ipynb as well as comments in the source code in util/modell.py

# To train the model:
- put unzipped empatica files into the dataset folder, in a subfolder named after the participant
- edit the score_and_help_indicator.csv file to include the new participant and the session that was recoreded
- run retrain_modell.py (currently, I dont know if there is any cross correlation between participants, but the more, the longer it takes)

# To run the actual calculation

configure the participants to look for in the file cogni_streamer.py and run it. It will look for empatica data on the LSL network of those participatns, calculate their load and publish the result again to LSL

# other scripts: 

e4_emulator.py reads empatica files in the "dataset" folder and outputs directly, as if the people are wearing the wristband just now.

e4_lowpass.py attempts to read the same stream, lowpass filters the heart rate and returns a sample of hr, gsr and acc vector length.
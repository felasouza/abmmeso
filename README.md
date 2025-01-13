# ABMMeso

## Description
This project is a Python Library for traffic simulation algorithm based on the Link Transmission Model, but with distinctions to allow each vehicle to be tracked invidividually.

The underlying model (Link Transmission Model) is a computationally efficient algorithm that is able to fairly well simulate macroscopic traffic while being fast or at least faster than cell-based approaches such as the cell transmission model.

As a macroscopic model, the model originally is not able to track vehicles individually as microscopic models do. Having this feature is essential for Agent-Based-Model packages such as POLARIS and where the original model had been proposed and implemented. The first paper is [here](https://www.sciencedirect.com/science/article/pii/S1877050919305824) in open access and a sequel is under review. 

Note: the implementation here is not the same as the POLARIS implementation (which accounts for more elements, such as AV's), has DTA integrated and a tigher integration with the whole environment. Here is an implementation by the same author (me, Felipe de Souza) for adding features and new models and to compare with the continuous model that is not present on POLARIS. 

## Usage
For now I (or we...) did not have any packaging so you need to either clone the repository from git or download itself. An introduction to using it through Python can be found at Jupyter-Notebook introduction.ipynb

It is also possible to run through command line which can be useful for whoever does not want to dive into the Python code itself, but wants to run some scenarios based on some inputs and check the CSV outputs.

I will assume you can open a command line and I will assume you can run Python by calling python 

Let's say you have your c:\Myproject, put abmmeso there such that exist c:\MyProject\abmmeso, c:\MyProject\abmmeso\demand, and etc (change the c:\Myproject as needed based on your folder structure)

on your command prompt:

>> cd c:\Myproject
<br>

>> python -m abmmeso abmmeso/samples/example-json-files-inputs/sample.json

you will see some csv outputs on the same folder (abmmeso/samples/example-json-files-inputs/). There are other .json inputs there.

# Clone the repository
git clone https://github.com/felasouza/abmmeso.git

## Contributing
I am happy to accept changes from contributors. I am still setting up the whole thing here so there is no specific guidelines other than having a proper unittest for the added module(s).


## Contact
For more information or contact information, you can find in [this website](http://www.felipedesouza.net).

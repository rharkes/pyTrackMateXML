[![MyPy](https://github.com/rharkes/pyTrackMateXML/actions/workflows/mypy.yml/badge.svg)](https://github.com/rharkes/pyTrackMateXML/actions/workflows/mypy.yml)
[![Black](https://github.com/rharkes/pyTrackMateXML/actions/workflows/black.yml/badge.svg)](https://github.com/rharkes/pyTrackMateXML/actions/workflows/black.yml)
[![PyTest](https://github.com/rharkes/pyTrackMateXML/actions/workflows/pytest.yml/badge.svg)](https://github.com/rharkes/pyTrackMateXML/actions/workflows/pytest.yml)


# pyTrackMateXML
For opening ImageJ TrackMate .xml files with python. Enables users to follow intensity traces based on TrackMate tracking results.

Alternative options are found [here](https://imagej.net/plugins/trackmate/#interoperability-with-python).

## TrackMate
From: https://imagej.net/TrackMate

TrackMate is available through Fiji and is based on a publication. If you use it successfully for your research please be so kind to cite the authors work: Tinevez, JY.; Perry, N. & Schindelin, J. et al. (2017), ["TrackMate: An open and extensible platform for single-particle tracking."](http://www.sciencedirect.com/science/article/pii/S1046202316303346), Methods 115: 80-90, PMID 27713081 (on Google Scholar). 

## Instalation
* Clone / download the repository
* `pip install -e .`

## Example
See this [Jupyternotebook](examples/demo_PyTrackMateXML.ipynb)

## Development
* Clone the repository
* `pip install -e .[dev]`
* Make sure you can run these commands without errors:
  * `black .`
  * `mypy`
  * `pytest`
# STMtools: Space Time Matrix Toolbox

[![DOI](https://zenodo.org/badge/556716843.svg)](https://zenodo.org/badge/latestdoi/556716843)

`STMtools` is an Xarray extension for Space-Time Matrix data. At this stage, it is implemented for PSI-InSAR processing.
## Installation

First, clone this repository to your local file system:

```bash
git clone git@github.com:MotionbyLearning/stmtools.git
```

It is strongly recommended to install `stmtools` under an independent Python environment, e.g. an independent [conda](https://docs.conda.io/en/latest/miniconda.html) environment. If `conda` is already installed in your system, you can create a new environment by:

```bash
conda create -n stm_demo python=3.10
```

A new environment named `stm_demo` will be created. Then you can activate it by:

```bash
conda activate stm_demo
```

After creating a new environment, you can install `stmtools` using `pip`:

```bash
cd stmtools
pip install .
```

## Usage example

An [example Jupyter Notebook](examples/demo_stm.ipynb) is available to demonstrate the usage of `stmtools`. Please follow the instructions inside the notebook to excute the demo.
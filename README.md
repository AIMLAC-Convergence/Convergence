[![Run tests](https://github.com/DrewBarratt90/Convergence/actions/workflows/pytest.yaml/badge.svg)](https://github.com/DrewBarratt90/Convergence/actions/workflows/pytest.yaml)

# Convergence


Repository for the convergence project aiming to deliver a state-of-the art auto-bidder.

## Setting things up:


### Pre-requisites:

You should have the `conda` environment manger installed. This ensures a consistent development environment - regardless of the machine you are using, in turn making issue-spotting simpler.
Note that each submodule should also include a `requirements.txt` file which includes packages specific to the module which can then be installed with `pip` (will also be needed for containerisation).

### Step 1: Make a directory
```bash
CONV_LOC=$HOME/CONV_software  # set this to wherever you like
CONV_SOFTWARE=${CONV_LOC}/Convergence 
mkdir -p $CONV_LOC && cd $CONV_LOC
```
### Step 2: Clone this repo

```
git clone https://github.com/DrewBarratt90/Convergence.git
```

### Step 3: Set up the conda env
```bash
CONDA_DIR=/opt/anaconda3    # or where conda is installed on your machine
cd $CONV_SOFTWARE 
conda env create -f environment.yml
```

Then, create the following bash script for easy set up:
(to activate do: `source $init_script`)

```bash
init_script="$HOME/start_conv_env.sh"  # change to whatever you want
echo "CONDA_DIR=$CONDA_DIR
CONV_SOFTWARE=$CONV_SOFTWARE
conda activate convergence-env
cd \$CONV_SOFTWARE
export PYTHONNOUSERSITE=true
export PYTHONPATH=\"\$PWD:\$PYTHONPATH\"" > $init_script
```


# Convergence

Repository for the AIMLAC Coding Challenge group named Convergence, aiming to deliver a state-of-the art auto-bidder using Cloud Native technologies.

The project as currently constituted is designed for use on Google Cloud, although it can be installed locally for development purposes.

## Local Installation
Please note that due to the way retraining is currently maintained, it is not possible to run the purchase model retraining locally. However, a copy of the model is stored in the repo for local development use.

### Step 1: Clone this repo
```
git clone https://github.com/AIMLAC-Convergence/Convergence.git
```

### Step 2: Set up the conda env
```
cd $CONV_SOFTWARE 
conda create --name convergence-env
```

### Step 3: Build pip prerequisites
```
pip install -r requirements.txt
```

### Step 4: Install local MySQL and set up database
Instructions for setting up local MySQL vary, please check https://dev.mysql.com/doc/mysql-getting-started/en/ for more details.

### Step 5. Modify settings for local use
Modify settings.yaml as noted to use the local database.

### Step 6: Run
```
python exec_function.py settings.yaml
```

## Google Cloud Installation
Setting up the Google Cloud version of the project requires a number of Google Cloud services to be activated. These are described in more detail in [the Cloud documentation](cloud.md).

Once the Cloud services are activated and set up, the Cloud Build system is used for Continuous Integration and Deployment. Any new version of the code which is added to the main branch (generally via a pull request) will result in a rebuild of the main project, while any new version of the code which is added to the retrain_model branch will result in a rebuild of the retrain function. These will be automatically built into containers, deployed onto the Google Cloud servers and used during the next scheduled activation of the system.

Finally, the static website functionality within the web/static folder is not served directly from the container, but from a Google Cloud Web Storage bucket. At present there is no Continuous Deployment for these files and updates will need to be transferred there directly using the Google Cloud Console. 
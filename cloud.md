# Google Cloud setup for Convergence

The Convergence project is intended to be used in a "web native" approach and is designed to be used from Google Cloud. (Information on potential conversion to other cloud services is included below.)

Before installing Convergence, a number of Google Cloud services will need to be set up from the Google Cloud Console. 

### 1: Project and Billing
The existing project is named "aimlac-containers"; you will likely need to perform a search-and-replace with the name of your new project, or ask for access to the original. Once you have your project, set up Billing using your academic credit code. 

### 2: Cloud Run and Artifact Registry
The main project runs on a Cloud Run instance, which activates only when triggered and shuts itself down afterwards. Make sure Cloud Run and Artifact Registry are both available from your Google Cloud Console. (You do not need to create these services as they will be created for you by the build process.)

### 3: Cloud SQL and Storage
Create a new SQL instance in the europe-north1 region named "convergenced". 
Additionally, create a new Storage bucket named "convergenced-public" in the same region and activate "web bucket" functionality on it. Copy the files from the /web/static folder into this bucket.

### 4: Cloud Build
Activate Cloud Build and set up 2 new Cloud Build triggers. (We called ours CI-Build and CI-Build-Retrain, but you can call them anything). Set the source for both to your Github fork of this repository. For branch, enter ^(main)$ and ^(retrain_model)$ for each. Set the configuration to Cloud Build Configuration File, located in the repository at /cloudbuild.yaml. Now manually trigger both Cloud Build pathways to set things up inside the project.

### 5: Set up the retrain instance
Create a Cloud Compute instance named 'retrain-ml-docker-3' within the 'europe-north1-a' region. You should select a Compute instance with facilities sufficient to run the retrain cycle; you'll want at least 4Gb of RAM but everything else is optional. When asked for the source details, point it to the 'retrain' container stored within Artifact Registry and select the 'latest' tag. 

### 6: Set up the daily triggers
We use Cloud Scheduler to run the instances as needed. Set up two Cloud Scheduler jobs, one targeting the Cloud Compute retrain instance from 5, one set to HTTP and accessing the Cloud Run URL (which is listed within Cloud Run on Console once it has been built). Instructions on doing the latter are here: https://cloud.google.com/run/docs/triggering/using-scheduler including some important notes on setting up service accounts for access purposes.

Once all these steps are completed, you should be able to access the web page and once the jobs trigger, data should appear inside the graphs. Consult the Logs within the Google Cloud instance for any problems along the way (and there almost certainly will be problems). Good luck!
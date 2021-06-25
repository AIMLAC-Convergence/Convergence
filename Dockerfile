FROM continuumio/miniconda3

WORKDIR /app

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "convergence-env", "/bin/bash", "-c"]

# The code to run when container is started:
COPY run_modules.py .
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "convergence-env", "python", "run_modules.py"]
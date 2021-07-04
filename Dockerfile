FROM continuumio/miniconda3

WORKDIR /app

# Create the environment:
ENV FLASK_APP=app/run_modules.py
ENV FLASK_RUN_HOST=0.0.0.0

#RUN apt-get -y install gcc musl-dev

EXPOSE 8080

COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "convergence-env", "/bin/bash", "-c"]

# The code to run when container is started:
COPY run_modules.py /app
COPY convergence_modules /app/convergence_modules
COPY utils /app/utils
COPY settings.yaml /app

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "convergence-env", "python", "run_modules.py", "settings.yaml"]
#ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "convergence-env", "python", "hello.py"]
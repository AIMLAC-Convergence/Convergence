FROM continuumio/miniconda3

WORKDIR /app

# Create the environment:
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

#RUN apt-get -y install gcc musl-dev

EXPOSE 80

COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "convergence-env", "/bin/bash", "-c"]

# The code to run when container is started:
COPY run_modules.py .
COPY convergence-modules .
COPY utils .
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "convergence-env", "python", "run_modules.py"]
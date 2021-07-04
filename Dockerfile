FROM python:3.8-slim-buster

WORKDIR /app

# Create the environment:
ENV FLASK_APP=app/exec_function.py
ENV FLASK_RUN_HOST=0.0.0.0

RUN apt-get update && apt-get install -y git

EXPOSE 8080

COPY requirements.txt /app/requirements.txt
RUN pip install --no-input -r /app/requirements.txt

ARG aimlac_IP=34.72.51.59
ENV AIMLAC_CC_MACHINE=$aimlac_IP

# The code to run when container is started:
COPY exec_function.py /app
COPY convergence_modules /app/convergence_modules
COPY Model /app/Model
COPY utils /app/utils
COPY settings.yaml /app
COPY web /app/web

ENTRYPOINT ["python", "exec_function.py", "settings.yaml"]
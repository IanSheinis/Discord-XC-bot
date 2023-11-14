# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.11.5
FROM python:${PYTHON_VERSION}-slim as base



RUN apt-get update && \
      apt-get -y install sudo

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1


WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user

RUN apt-get update && apt-get install -y tzdata
#CHANGE TO YOUR TIMEZONE 
ENV TZ=US/Pacific
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone



# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Create the logs directory and give write permission to 'admin'
# RUN mkdir -p /app/logs && chown -R admin:admin /app/logs

COPY . .

USER root

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    admin

#RUN chown -R admin:admin /app/logs
#RUN chown -R admin:admin sqlite_databases
#Know it's bad practice but gave up on troubleshooting where to give permission
RUN chown -R admin:admin /app

# #RUN sudo chmod 666 /app/logs/infos.log
# RUN sudo chmod 666 /app/logs

USER admin


# Copy the source code into the container.


# Expose the port that the application listens on.
EXPOSE 8000

#COPY C:\Users\milik\OneDrive\Desktop\XC bot\requirements.txt

#RUN pip3 install -r requirements.txt
# Run the application.
CMD python application.py

# Use an official Python runtime as a parent image
FROM python:3.5

# Install curl
# RUN apt-get update && apt-get install -y \
#   curl \
#   && rm -rf /var/lib/apt/lists/*

# Install docker client    
# ENV DOCKER_CHANNEL stable
# ENV DOCKER_VERSION 17.03.1-ce
# ENV DOCKER_API_VERSION 1.27
# RUN curl -fsSL "https://download.docker.com/linux/static/${DOCKER_CHANNEL}/x86_64/docker-${DOCKER_VERSION}.tgz" \
#   | tar -xzC /usr/local/bin --strip=1 docker/docker


# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install  -r requirements.txt
RUN pip install flask-migrate

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_CONFIG development
ENV FLASK_ENV development
ENV FLASK_APP application.py
ENV FLASK_DEBUG 1
ENV SQLALCHEMY_TRACK_MODIFICATIONS False


# ## DATABASE :
RUN pip install flask-migrate
RUN rm -rf migrations

# # #Create setup for migrations - Only once
RUN flask db init

# # #To generate Migrations files
# RUN flask db migrate

# # # #To apply changes
# RUN flask db upgrade 

# COPY migrations /app/migrations

# Run app.py when the container launches
# CMD ["python", "application.py"]
CMD ["flask", "run", "--host", "0.0.0.0"]


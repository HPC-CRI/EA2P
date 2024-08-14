# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install apt-utils to avoid debconf warnings
RUN apt-get update && \
    apt-get install -y apt-utils

# Install necessary system packages
RUN apt-get update && \
    apt-get install -y powercap-utils dmidecode libopenmpi-dev

# Copy the requirements file and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Clean up APT when done to reduce image size
RUN apt-get clean
# Copy the rest of the application code into the container
COPY . .

# RUN pip install ea2p  # Uncomment this and comment the line below to work with local version of EA2P or not. You can also replace with 'git clone https://github.com/HPC-CRI/EA2P.git' to use the lastest version of the app.
COPY ../EA2P /usr/src/app/EA2P # add 'sys.path.append("/usr/src/app/ea2p")' to your code to specify the EA2P source dir to your application

# Set the environment variables if needed
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES all
ENV PYTHONUNBUFFERED=1

# Run the application: replace "./sleep.py" by your App and "60" by your app parameter is applicable.
CMD ["python", "./sleep.py", "60"]

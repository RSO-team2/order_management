# Use an official Python runtime as a parent image.
FROM python

# Set the working directory to /app
WORKDIR ./

# Copy the current directory contents into the container at /app
ADD . ./

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
RUN ["python3", "./setup.py"]

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME=Order-Management

# Run app.py when the container launches
CMD ["python3", "./api/app.py"]
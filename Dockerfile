# Use an official Python runtime as a parent image.
FROM python

# Set the working directory to /app
WORKDIR /api

# Copy the current directory contents into the container at /app
ADD . /api

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]
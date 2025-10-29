FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
EXPOSE 5000
# This Dockerfile sets up a Python 3.9 environment, copies the application code into the container,
# installs the required dependencies from requirements.txt, and runs the application using app.py.
# The application listens on port 5000.
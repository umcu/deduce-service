FROM python:3.11-slim

WORKDIR /app

# Install Git
RUN apt-get -y update
RUN apt-get -y install git

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the remaining files
COPY deduce-service/. /app

# Run app
ENV FLASK_APP deduce_app.py
ENTRYPOINT ["flask"]
CMD ["run", "--host=0.0.0.0"]

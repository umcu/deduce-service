FROM python:3.7-slim

WORKDIR /app

# First install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the remaining files
COPY . /app

# Run app
ENV FLASK_APP deduce_app.py
ENTRYPOINT ["flask"]
CMD ["run", "--host=0.0.0.0"]
# Deduce Service

> :warning: This repository is no longer maintained/updated, but please feel free to use it for inspiration.

Web Service for [Deduce](https://github.com/vmenger/deduce), to be used in pipelines such as [CogStack-NiFi](https://github.com/cogstack/cogstack-nifi).



## Installation
```bash
docker-compose up
```

The API should now be available at http://localhost:5000/

## Usage
- Use `/deidentify` for de-identification of a single text.
- Use `/deidentify_bulk` for de-identification of multiple texts.
See documentation in Swagger UI for the specific data format.
  
## Tests
In your IDE of choice, add a run configuration for `test/test_service.py` and set the working directory to the root directory of this repository.

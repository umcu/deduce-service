import deduce
import multiprocessing
import utils
from flask import Flask, request
from flask_restx import Resource, Api, fields
from werkzeug.middleware.proxy_fix import ProxyFix
import logging


class ErrorLoggingApi(Api):

    def handle_error(self, e):
        self.logger.error(e)
        super().handle_error(e)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = ErrorLoggingApi(
    app,
    title="Deduce Web Service",
    description="API to de-identify text using Deduce",
    version='1.0'
)
api.logger.setLevel(logging.INFO)

# Load example data
example_data = utils.load_single_example_text()
example_data_bulk = utils.load_multiple_example_texts()


class NullableString(fields.String):
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable string'


# Define input (payload) and output (response) models
# Todo: Add remaining Deduce arguments, including examples & tests
payload_model = api.model(
    'payload',
    {
        'text': NullableString(example=example_data['text'], required=True),
        'patient_first_names': fields.String(example=example_data['patient_first_names'],
                                             description='Multiple names can be separated by white space'),
        'patient_surname': fields.String(example=example_data['patient_surname']),
        'id': fields.Integer(example=example_data['id'], required=False),
        'dates': fields.Boolean(example=example_data['dates'], required=False, default=True)
    }
)

response_model = api.model(
    'response',
    {
        'text': fields.String, 'id': fields.Integer(required=False)
    }
)

payload_model_bulk = api.model(
    'payloadbulk',
    {
        'texts': fields.List(fields.Nested(payload_model), example=example_data_bulk['texts'], required=True)
    }
)

response_model_bulk = api.model(
    'responsebulk',
    {
        'texts': fields.List(fields.Nested(response_model))
    }
)


@api.route('/deidentify')
class DeIdentify(Resource):
    @api.expect(payload_model, validate=True)
    @api.marshal_with(response_model)
    def post(self):
        # Retrieve input data
        data = request.get_json()

        # Run Deduce pipeline
        response = annotate_text(data)

        return response


@api.route('/deidentify_bulk')
class DeIdentifyBulk(Resource):
    @api.expect(payload_model_bulk, validate=True)
    @api.marshal_list_with(response_model_bulk)
    def post(self):
        # Retrieve input data
        data = request.get_json()

        api.logger.info(f"Received {len(data['texts'])} texts in deidentify_bulk, starting to process...")

        # Run Deduce pipeline
        response = annotate_text_bulk(data['texts'])

        api.logger.info(f"Done processing {len(data['texts'])} texts.")

        return response


def annotate_text(data):
    """
    Run a single text through the Deduce pipeline
    """
    # Remove ID from object
    record_id = None
    if 'id' in data:
        record_id = data['id']
        del data['id']

    # Run Deduce pipeline
    annotated_text = deduce.annotate_text(**data)
    deidentified_text = deduce.deidentify_annotations(annotated_text)

    # Format result
    result = {'text': deidentified_text}

    # Add the ID if it was passed along
    if record_id is not None:
        result['id'] = record_id

    return result


def annotate_text_bulk(data):
    """
    Run multiple texts through the Deduce pipeline in parallel
    """
    with multiprocessing.Pool() as pool:
        result = pool.map(annotate_text, data)

    # Format result
    result = {'texts': result}
    return result


if __name__ == "__main__":
    app.run(port=5000)

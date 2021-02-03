import deduce
from flask import Flask, request
from flask_restx import Resource, Api, fields
import multiprocessing


app = Flask(__name__)
api = Api(
    app,
    title="Deduce Web Service",
    description="API to de-identify text using Deduce",
)

# Set example data, as provided in Deduce documentation
example_data = {'text': 'Dit is stukje tekst met daarin de naam Jan Jansen. De patient J. Jansen (e: '
                        'j.jnsen@email.com, t: 06-12345678) is 64 jaar oud en woonachtig in Utrecht. Hij werd op 10 '
                        'oktober door arts Peter de Visser ontslagen van de kliniek van het UMCU.',
                'patient_first_names': 'Jan',
                'patient_surname': 'Jansen'}

# Define input (payload) and output (response) models
payload_model = api.model('payload', {'text': fields.String(example=example_data['text'], required=True),
                                      'patient_first_names': fields.String(example=example_data['patient_first_names']),
                                      'patient_surname': fields.String(example=example_data['patient_surname'])})
payload_model_bulk = api.model('payloadbulk', {'texts': fields.List(fields.Nested(payload_model),
                                                                    example=[example_data]*3)})
response_model = api.model('response', {'text': fields.String})
response_model_bulk = api.model('responsebulk', {'texts': fields.List(fields.Nested(payload_model),
                                                                      example=[example_data]*3)})


@api.route('/deidentify')
class DeIdentify(Resource):
    @api.expect(payload_model)
    @api.marshal_with(response_model)
    def post(self):
        # Retrieve input data
        data = request.get_json()

        # Run Deduce pipeline
        response = annotate_text(data)

        return response


@api.route('/deidentify_bulk')
class DeIdentifyBulk(Resource):
    @api.expect(payload_model_bulk)
    # @api.marshal_list_with(response_model_bulk)
    def post(self):
        # Retrieve input data
        data = request.get_json()

        # Run Deduce pipeline
        response = annotate_text_bulk(data['texts'])

        return response


def annotate_text(data):
    """
    Run a single text through the Deduce pipeline
    :param data:
    :return:
    """
    annotated_text = deduce.annotate_text(**data)
    deidentified_text = deduce.deidentify_annotations(annotated_text)

    # Format result
    result = {'text': deidentified_text}
    return result


def annotate_text_bulk(data):
    """
    Run multiple texts through the Deduce pipeline in parallel
    :param data:
    :return:
    """
    with multiprocessing.Pool() as pool:
        result = pool.map(annotate_text, data)

    # Format result
    result = {'texts': result}
    return result


if __name__ == "__main__":
    app.run()

import deduce
from flask import Flask, request
from flask_restx import Resource, Api, fields

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

# Define input (payload) and output (response) model
payload_model = api.model('payload', {'text': fields.String(example=example_data['text'], required=True),
                                      'patient_first_names': fields.String(example=example_data['patient_first_names']),
                                      'patient_surname': fields.String(example=example_data['patient_surname'])})
response_model = api.model('response', {'text': fields.String})


@api.route('/deidentify')
class DeIdentify(Resource):
    @api.expect(payload_model)
    @api.marshal_with(response_model)
    def post(self):
        # Retrieve input data
        data = request.get_json()

        # Run Deduce pipeline
        annotated_text = deduce.annotate_text(*data)

        # annotated_text = deduce.annotate_text(*data)
        deidentified_text = deduce.deidentify_annotations(annotated_text)

        # Format response
        response = {'text': deidentified_text}
        return response


if __name__ == "__main__":
    app.run()

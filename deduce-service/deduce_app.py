import logging
import multiprocessing
from typing import Optional

import deduce
from deduce.person import Person
from deduce_model import initialize_deduce
from examples import example_text, example_texts
from flask import Flask, abort, request
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix

deduce_model = initialize_deduce()
__version__ = '0.0.1'

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(
    app,
    title="Deduce Web Service",
    description=f"API to de-identify text using Deduce v{deduce.__version__}",
)
api.logger.setLevel(logging.INFO)


class NullableString(fields.String):
    __schema_type__ = ["string", "null"]
    __schema_example__ = "nullable string"


payload_model = api.model(
    "payload",
    {
        "text": NullableString(example=example_text["text"], required=True),
        "patient_first_names": fields.String(
            example=example_text["patient_first_names"],
            description="Multiple names can be separated by white space",
        ),
        "patient_surname": fields.String(example=example_text["patient_surname"]),
        "id": fields.String(example=example_text["id"], required=False),
        "disabled": fields.List(
            fields.String(), example=example_text["disabled"], required=False
        ),
    },
)

response_model = api.model(
    "response", {"text": fields.String, "id": fields.String(required=False), "version": fields.String()}
)

payload_model_bulk = api.model(
    "payloadbulk",
    {
        "texts": fields.List(
            fields.Nested(payload_model),
            example=example_texts["texts"],
            required=True,
        ),
        "disabled": fields.List(
            fields.String(), example=example_texts["disabled"], required=False
        ),
    },
)

response_model_bulk = api.model(
    "responsebulk", {"texts": fields.List(fields.Nested(response_model))}
)


@api.route("/deidentify")
class DeIdentify(Resource):
    @api.expect(payload_model, validate=True)
    @api.marshal_with(response_model)
    def post(self):

        data = request.get_json()

        if data["text"] is None:
            return format_result(data, output_text=None)

        return annotate_text(data)


@api.route("/deidentify_bulk")
class DeIdentifyBulk(Resource):
    @api.expect(payload_model_bulk, validate=True)
    @api.marshal_list_with(response_model_bulk)
    def post(self):

        data = request.get_json()
        num_texts = len(data["texts"])

        if "disabled" in data:
            for record in data["texts"]:
                record["disabled"] = data["disabled"]

        api.logger.info(
            f"Received {num_texts} texts in " f"deidentify_bulk, starting to process..."
        )

        response = annotate_text_bulk(request.get_json()["texts"])

        api.logger.info(f"Done processing {num_texts} texts.")

        return response


def format_result(input_data: dict, output_text: Optional[str]) -> dict:

    result = {
        "text": output_text,
        "version": f"deduce_{deduce_model.__version__}_deduce-service_{__version__}"
    }

    if input_data.get("id", None):
        result["id"] = input_data["id"]

    return result


def annotate_text(data):
    """
    Run a single text through the Deduce pipeline
    """

    deduce_args = {"text": data["text"]}

    if ("patient_first_names" in data) or ("patient_surname" in data):
        deduce_args["metadata"] = dict()
        deduce_args["metadata"]["patient"] = Person.from_keywords(
            patient_first_names=data.get("patient_first_names", None),
            patient_surname=data.get("patient_surname", None),
        )

    if data.get("disabled", None):
        deduce_args["disabled"] = set(data["disabled"])

    try:
        doc = deduce_model.deidentify(**deduce_args)
    except (
        AttributeError,
        IndexError,
        KeyError,
        MemoryError,
        NameError,
        OverflowError,
        RecursionError,
        RuntimeError,
        StopIteration,
        TypeError,
    ) as e:
        api.logger.exception(e)
        abort(
            500,
            f"Deduce encountered this error when processing a text: {e}. For full traceback, see logs.",
        )
        return

    return format_result(data, output_text=doc.deidentified_text)


def annotate_text_bulk(data):
    """
    Run multiple texts through the Deduce pipeline in parallel
    """
    with multiprocessing.Pool() as pool:
        result = pool.map(annotate_text, data)

    result = {"texts": result}
    return result


if __name__ == "__main__":
    app.run(port=5000)

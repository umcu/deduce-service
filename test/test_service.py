import pytest
import json
import utils
from deduce_app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_deidentify(client):
    example_data = utils.load_single_example_text()
    response = client.post("/deidentify",
                           data=json.dumps(example_data),
                           headers={"Content-Type": "application/json"})
    data = response.get_json()

    # Test whether the patient name is removed
    assert "Jansen" not in data['text']

    # Test whether the patient name has been replaced
    assert "<PATIENT>" in data['text']

    # Test whether other functional parts are still included
    assert "ontslagen van de kliniek" in data['text']


def test_deidentify_bulk(client):
    example_data_bulk = utils.load_multiple_example_texts()
    response = client.post("/deidentify_bulk",
                           data=json.dumps(example_data_bulk),
                           headers={"Content-Type": "application/json"})
    data = response.get_json()

    # Test whether multiple results are returned
    assert len(data['texts']) == 2

    # Test whether de-identification of the second text was done correctly
    assert "Jong" not in data['texts'][1]['text']

    # Test whether the adjective use of "jong" was included
    assert "jong" in data['texts'][1]['text']

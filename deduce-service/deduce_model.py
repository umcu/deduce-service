from deduce import Deduce


def initialize_deduce():

    model = Deduce()

    # override standard, bit better for html rendering
    model.processors["redactor"].open_char = "["
    model.processors["redactor"].close_char = "]"

    return model

from deduce import Deduce


def initialize_deduce():

    model = Deduce()

    # override standard, bit better for html rendering
    model.processors["post_processing"]["redactor"].open_char = "["
    model.processors["post_processing"]["redactor"].close_char = "]"

    return model

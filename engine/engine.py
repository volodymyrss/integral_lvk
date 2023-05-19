
from odafunction.executors import default_execute_to_value
from odafunction.func.urifunc import URIipynbFunction
import os

def run_workflow(workflow, input):
    f = URIipynbFunction.from_uri("file://" + os.path.abspath(workflow))
    print("found as", f)
    f = f(**input)
    print("found parameters applied as", f)
    return default_execute_to_value(f, cached=True)['output_values']

def sequence(input):
    run_workflow("workflows/iobserve.ipynb", input)
    run_workflow("workflows/integralallsky.ipynb", input)

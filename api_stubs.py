# Auto-generated API stubs

import os
from langchain.output_parsers import PydanticOutputParser
from langchain import PromptTemplate
from langchain.llms import OpenAI

if not os.environ.get("OPENAI_API_KEY"):
    raise Exception("Please set your OpenAI API key as an environment variable.")

llm = OpenAI(temperature=0.9)

from model import IsFluffyResponse


def isPetFluffy(event, context):
    template = """
## Objective

Generate outputs for a Python AWS Lambda function with the following OpenAPI schema:

:/is_fluffy:
  post:
    description: Returns whether the pet is fluffy or not.
    operationId: isPetFluffy
    requestBody:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/IsFluffyRequest'
    responses:
      '200':
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IsFluffyResponse'
        description: successful operation
    summary: Is the pet fluffy?

IsFluffyRequest:
  properties:
    pet_type:
      description: The type of Pet
      example: cat
      type: string
  required:
  - pet_type
  type: object

IsFluffyResponse:
  properties:
    is_fluffy:
      type: boolean
  required:
  - is_fluffy
  type: object
# Inputs

The Lambda function was invoked with the following event:

{event}

# Instructions

{format_instructions}

# Outputs

"""

    parser = PydanticOutputParser(pydantic_object=IsFluffyResponse)
    prompt = PromptTemplate(template=template, input_variables=["event"], partial_variables={"format_instructions": parser.get_format_instructions()})
    input = prompt.format_prompt(event=event)
    output = llm(input.to_string())
    return parser.parse(output).dict()


def petAlwaysFluffy(event, context):
    template = """
## Objective

Generate outputs for a Python AWS Lambda function with the following OpenAPI schema:

:/is_fluffy:
  get:
    description: Returns true
    operationId: petAlwaysFluffy
    responses:
      '200':
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IsFluffyResponse'
        description: successful operation
    summary: Returns true

IsFluffyResponse:
  properties:
    is_fluffy:
      type: boolean
  required:
  - is_fluffy
  type: object
# Inputs

The Lambda function was invoked with the following event:

{event}

# Instructions

{format_instructions}

# Outputs

"""

    parser = PydanticOutputParser(pydantic_object=IsFluffyResponse)
    prompt = PromptTemplate(template=template, input_variables=["event"], partial_variables={"format_instructions": parser.get_format_instructions()})
    input = prompt.format_prompt(event=event)
    output = llm(input.to_string())
    return parser.parse(output).dict()


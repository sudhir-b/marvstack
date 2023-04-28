import os
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from model import IsFluffyResponse

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    raise Exception("Please set your OpenAI API key as an environment variable.")

llm = OpenAI(temperature=0.9)

# Flow:
#   Input is an OpenAPI yaml document or a structured description of endpoint(s) and their inputs/outputs
#   For each endpoint, a python function is created
#   For each function, endpoint information (i.e. summary & description) is turned into a prompt template
#   For each function, the prompt is used with langchain as the body as below
#   A serverless template is used to create a serverless stack with all the functions and endpoints

parser = PydanticOutputParser(pydantic_object=IsFluffyResponse)


def is_pet_fluffy(pet_type):
    prompt = PromptTemplate(
        template="""
## Objective

Generate outputs for a function with the following OpenAPI schema:

/is_fluffy:
  post:
    summary: Is the pet fluffy?
    description: Returns whether the pet is fluffy or not.
    operationId: isPetFluffy
    requestBody:
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/IsFluffyRequest"
    responses:
      "200":
        description: successful operation
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/IsFluffyResponse"

components:
  schemas:
    IsFluffyRequest:
      type: object
      required:
        - pet_type
      properties:
        pet_type:
          type: string
          description: The type of Pet
          example: cat
    IsFluffyResponse:
      type: object
      required:
        - is_fluffy
      properties:
        is_fluffy:
          type: boolean

# Inputs

The function was called with the following inputs:

pet_type: {pet_type}

# Instructions 

{format_instructions}

# Outputs

""",
        input_variables=["pet_type"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    _input = prompt.format_prompt(pet_type=pet_type)
    return llm(_input.to_string())


print(parser.get_format_instructions())

result = is_pet_fluffy("cat")
print(result)


# once, the result has been something like: {is_fluffy: true}
# and the parser has complained the key is not in double quotes

result = parser.parse(result)

print(result)

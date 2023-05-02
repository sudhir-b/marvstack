import os
import yaml
import subprocess


def get_component_definition(spec, ref):
    definitions = spec["components"]["schemas"]
    return definitions[ref]


def generate_stub_functions(openapi_yaml, output_file_path):
    with open(openapi_yaml, "r") as f:
        spec = yaml.safe_load(f)

    with open(output_file_path, "w") as f:
        f.write("# Auto-generated API stubs\n\n")

        # f.write("try:\n")
        # f.write("    import unzip_requirements\n")
        # f.write("except ImportError:\n")
        # f.write("    pass\n\n")

        f.write("import os\n")
        f.write("from langchain.output_parsers import PydanticOutputParser\n")
        f.write("from langchain import PromptTemplate\n")
        f.write("from langchain.llms import OpenAI\n")

        f.write("\n")
        f.write('if not os.environ.get("OPENAI_API_KEY"):\n')
        f.write(
            '    raise Exception("Please set your OpenAI API key as an environment variable.")\n\n'
        )

        f.write("llm = OpenAI(temperature=0.9)\n\n")

        components = set()
        function_definitions = []

        for path, path_item in spec["paths"].items():
            for method, operation in path_item.items():
                operation_id = operation.get("operationId")
                if not operation_id:
                    print(
                        f"Skipping {method.upper()} {path} due to missing operationId"
                    )
                    continue

                objective = f"## Objective\n\nGenerate outputs for a Python AWS Lambda function with the following OpenAPI schema:\n\n:"

                # Build template string
                template = f'"""\n{objective}{yaml.dump({path: {method: operation}}, default_flow_style=False)}'

                # Add component definitions to template
                request_body = operation.get("requestBody")
                if request_body:
                    request_schema = request_body["content"]["application/json"][
                        "schema"
                    ]
                    if "$ref" in request_schema:
                        ref = request_schema["$ref"]
                        component = ref.split("/")[-1]
                        definition = get_component_definition(spec, component)
                        template += f"\n{yaml.dump({component: definition}, default_flow_style=False)}"

                response_component = None

                responses = operation.get("responses", {})
                for response in responses.values():
                    response_schema = response["content"]["application/json"]["schema"]
                    if "$ref" in response_schema:
                        ref = response_schema["$ref"]
                        response_component = ref.split("/")[-1]
                        components.add(response_component)
                        definition = get_component_definition(spec, response_component)
                        template += f"\n{yaml.dump({response_component: definition}, default_flow_style=False)}"

                inputs = "# Inputs\n\nThe Lambda function was invoked with the following event:\n\n{event}\n\n"

                instructions = "# Instructions\n\n{format_instructions}\n\n"

                outputs = "# Outputs\n\n"

                template = template + inputs + instructions + outputs + '"""\n'

                function_definition = f"def {operation_id}(event, context):\n"
                function_definition += f"    template = {template}\n"

                if response_component:
                    function_definition += f"    parser = PydanticOutputParser(pydantic_object={response_component})\n"

                function_definition += '    prompt = PromptTemplate(template=template, input_variables=["event"], partial_variables={"format_instructions": parser.get_format_instructions()})\n'
                function_definition += "    input = prompt.format_prompt(event=event)\n"
                function_definition += "    output = llm(input.to_string())\n"
                function_definition += "    return parser.parse(output).dict()\n\n"

                function_definitions.append(function_definition)

        f.write(f"from model import {', '.join(components)}\n\n")
        f.write("\n")
        f.write("\n".join(function_definitions))


def generate_model(openapi_yaml):
    command = f"datamodel-codegen --input {openapi_yaml} --input-file-type openapi --output model.py"
    subprocess.run(command, shell=True)


def generate_serverless_yaml(openapi_yaml):
    with open(openapi_yaml, "r") as f:
        spec = yaml.safe_load(f)

    with open("serverless.template.yaml", "r") as f:
        template = yaml.safe_load(f)

    template["functions"] = {}

    for path, path_item in spec["paths"].items():
        for method, operation in path_item.items():
            operation_id = operation.get("operationId")
            if not operation_id:
                print(f"Skipping {method.upper()} {path} due to missing operationId")
                continue

            template["functions"][operation_id] = {
                "handler": "api_stubs." + operation_id,
                "events": [{"httpApi": {"path": path, "method": method.upper()}}],
            }

    template["provider"]["environment"] = {"OPENAI_API_KEY": "${env:OPENAI_API_KEY}"}

    with open("serverless.yaml", "w") as f:
        yaml.dump(template, f)


if __name__ == "__main__":
    openapi_yaml = "openapi.yaml"
    output_file_path = "api_stubs.py"

    generate_stub_functions(openapi_yaml, output_file_path)
    generate_model(openapi_yaml)

    print(f"Generated stubs file: {os.path.abspath(output_file_path)}")

    # print("Running black...")
    # subprocess.run(["black", output_file_path])
    # print("Running isort...")
    # subprocess.run(["isort", output_file_path])

    generate_serverless_yaml(openapi_yaml)

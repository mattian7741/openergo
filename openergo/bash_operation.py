# import json
# import logging
# import subprocess
# from typing import Any

# from .operation import Operation


# class BashOperation(Operation):
#     def __init__(self, command_template, bindings):
#         super().__init__()
#         self.command_template = command_template
#         self.bindings = bindings

#     def resolve_nested_bindings(self, bindings, kwargs):
#         resolved = {}
#         for key, value in bindings.items():
#             if isinstance(value, str) and value.startswith('{') and value.endswith('}'):
#                 path = value[1:-1].split('.')
#                 try:
#                     data = kwargs
#                     for p in path:
#                         data = data[p]
#                     resolved[key] = data
#                 except KeyError:
#                     logging.error(f"Binding for {key} using path {value} not found in provided arguments")
#                     raise ValueError(f"Binding for {key} not provided correctly")
#             else:
#                 resolved[key] = value
#         return resolved

#     def execute(self) -> Any:
#         try:
#             final_bindings = self.resolve_nested_bindings(self.bindings, kwargs)
#             if 'name' in final_bindings:
#                 command = f"./{
#                     self.command_template} '{
#                     final_bindings['name']}'"
#                 print(f"Executing command: {command}")  # Debugging print
#                 result = subprocess.check_output(command, shell=True, text=True).strip()
#                 return json.dumps({"result": result})
#             else:
#                 return json.dumps({"error": "Binding for 'name' not resolved"})
#         except ValueError as ve:
#             return json.dumps({"error": str(ve)})
#         except subprocess.CalledProcessError as e:
#             logging.error(f"Bash command failed: {e}")
#             return json.dumps({"error": str(e)})


# def execute(self, **kwargs) -> Any:
#     try:
#         # Resolve bindings considering nested dictionary structures
#         final_bindings = self.resolve_nested_bindings(self.bindings, kwargs)
#         # Format the command with resolved bindings
#         command = f"bash {
#             self.command_template} {
#             final_bindings['name']}"  # Update to format command correctly
#         result = subprocess.check_output(command, shell=True, text=True).strip()
#         return json.dumps({"result": result})
#     except ValueError as ve:
#         return json.dumps({"error": str(ve)})
#     except subprocess.CalledProcessError as e:
#         logging.error(f"Bash command failed: {e}")
#         return json.dumps({"error": str(e)})

#     def execute(self, **kwargs) -> Any:
#         try:
#             # Resolve bindings considering nested dictionary structures
#             final_bindings = self.resolve_nested_bindings(self.bindings, kwargs)
#             # Format the command with resolved bindings
#             command = self.command_template.format(**final_bindings)
#             result = subprocess.check_output(command, shell=True, text=True).strip()
#             return json.dumps({"result": result})
#         except ValueError as ve:
#             return json.dumps({"error": str(ve)})
#         except subprocess.CalledProcessError as e:
#             logging.error(f"Bash command failed: {e}")
#             return json.dumps({"error": str(e)})

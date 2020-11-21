import os
import random
import string
import subprocess
import traceback
from typing import Dict, List

import yaml
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

executable = os.environ.get('TAM_CMD', 'tam-eval')

def exec_cmd(command: str) -> str:
  split_cmd = [v for v in command.split(" ") if v]
  try:
    return subprocess.check_output(
      split_cmd,
      stderr=subprocess.STDOUT
    ).decode('utf-8')
  except subprocess.CalledProcessError:
    print(traceback.format_exc())
    print(f"[tam_server:server] call to {executable} failed ^^")
    return ''


def exec_yaml_cmd(command: str) -> Dict:
  return yaml.load(exec_cmd(command))


def exec_yamls_cmd(command: str) -> List[Dict]:
  return list(yaml.load_all(exec_cmd(command), Loader=yaml.FullLoader))


def rand_str(string_len=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(string_len))


def fmt_inlines(assignments: Dict) -> str:
  expr_array = []
  for assignment in list(assignments.items()):
    key_expr, value = assignment
    expr_array.append(f"--set {key_expr}={value}")
  return " ".join(expr_array)


@app.route('/simple_values')
def simple_values():
  values_dict = exec_yaml_cmd(f"{executable} values")
  return jsonify(data=values_dict)


@app.route('/values', methods=['POST'])
def values():
  flags = request.json.get('flags')
  values_dict = exec_yaml_cmd(f"{executable} values {flags}")
  return jsonify(data=values_dict)


@app.route('/template', methods=['POST'])
def template():
  attrs = request.json
  assignments = attrs.get('assignments', {})
  inlines = attrs.get('inlines', {})
  flags = attrs.get('flags')
  release_name = request.args.get('release_name', '')

  tmp_file_name = f"/tmp/values-{rand_str(20)}"

  with open(tmp_file_name, 'w') as file:
    file.write(yaml.dump(assignments))

  args = f"-f {tmp_file_name} {fmt_inlines(inlines)} {flags}"
  res_dicts = exec_yamls_cmd(f"{executable} template {release_name} {args}")
  os.remove(tmp_file_name)

  return jsonify(data=res_dicts)


@app.route('/')
def simple_template():
  release_name = request.args.get('release_name', '')
  res_dicts = exec_yamls_cmd(f"{executable} template {release_name} .")
  return jsonify(data=res_dicts)


app.config["cmd"] = ["bash"]
print(f"[tam_server:server] starting with tam exec '{executable}'")
app.run(host='0.0.0.0', port=5005, debug=True)

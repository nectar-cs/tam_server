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
  return yaml.load(exec_cmd(command), Loader=yaml.FullLoader)


def exec_yamls_cmd(command: str) -> List[Dict]:
  return list(yaml.load_all(exec_cmd(command), Loader=yaml.FullLoader))


def rand_str(string_len=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(string_len))


@app.route('/values')
def values():
  values_dict = exec_yaml_cmd(f"{executable} values . {fmt_cmd_args()}")
  return jsonify(data=values_dict)


@app.route('/info')
def info():
  return jsonify(
    executable=executable,
    flask_env=app.env
  )


@app.route('/template', methods=['POST'])
def template():
  tmp_file_name = f"/tmp/values-{rand_str(20)}"

  with open(tmp_file_name, 'w') as file:
    file.write(yaml.dump(request.json or {}))

  full_cmd = f"{compile_template_cmd()} -f {tmp_file_name}"
  res_dicts = exec_yamls_cmd(full_cmd)
  os.remove(tmp_file_name)

  return jsonify(data=res_dicts)


@app.route('/')
def simple_template():
  res_dicts = exec_yamls_cmd(compile_template_cmd())
  return jsonify(data=res_dicts)


def compile_template_cmd():
  release_name = request.args.get('release_name', '')
  return f"{executable} template {release_name} . {fmt_cmd_args()}"


def fmt_cmd_args() -> str:
  return request.args.get('args', '')


app.config["cmd"] = ["bash"]
print(f"[tam_server:server] starting with tam exec '{executable}'")
app.run(host='0.0.0.0', port=5005)

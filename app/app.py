from flask import Flask, request
from pyspell import spell
import json
import re


app = Flask(__name__)
slm = spell.lcsmap('[\\s]+')
regex = r"^([\w-]+\s[\d:,]+)\s([\w]+)\s(\[\w+\])\s(.*)$"


def _parse_log(log_data):
	if not log_data:
		return {}
	log_fields = parse_log_regex(log_data)
	obj = slm.insert(log_fields["msg"])

	result = {
		"original": log_data,
		"eventTemplate": obj.get_sequence(),
		"parameterList": obj.param(log_data),
	}

	return result


def parse_log_regex(log_str):
	comp = re.compile(regex)
	res = comp.match(log_str)
	return {
		"datetime": res.group(1),
		"level": res.group(2),
		"pid": res.group(3),
		"msg": res.group(4),
	}

@app.route('/log', methods=["POST"])
def add_log():
	log_data = request.get_data().decode('UTF-8')
	log_data = log_data.strip('\n')
	parsed_log = _parse_log(log_data)

	# store_parsed_log_to_db(parsed_log)
    # model_result = run_classifier_model(parsed_log)
	# store_model_result_to_db(model_result)

	# send "alert" when model result is error 

	return json.dumps(parsed_log)


@app.route('/bulk', methods=["POST"])
def bulk_logs():
	log_data = request.get_data().decode('UTF-8')
	logs = log_data.split('\n')
	for log in logs:
		_parse_log(log)
	return slm.tojson()


@app.route('/mappings', methods=["GET", "DELETE"])
def mappings():
	if request.method == 'DELETE':
		global slm
		slm = spell.lcsmap('[\\s]+')
	return slm.tojson()


if __name__ == '__main__':
	app.run(host='0.0.0.0')

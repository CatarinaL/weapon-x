import csv
import io
import json
import re
from flask import Flask, make_response, request

from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key

import modeleval
from pyspell import spell

from datetime import datetime


# INITIALISE FLASK APP
app = Flask(__name__)
CORS(app)

# INITIALISE MODEL
model = modeleval.ModelEval()

# INITIALISE SPELL LOG MAPPINGS
def load_mappings():
    s = spell.load('mappings.pickle')
    return s or spell.lcsmap("[\\s]+")
slm = load_mappings()

# INITIALISE DYNAMO DB CLIENT
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
DYNAMO_TABLE_NAME = "processedlogs"

regex = r"^([\w-]+\s[\d:,]+)\s([\w]+)\s(\[[^\]]+\])\s(.*)$"


def _parse_log(log_data):
    if not log_data:
        return {}
    log_fields = parse_log_regex(log_data)
    if not log_fields:
        return {}
    obj = slm.insert(log_fields["msg"])

    result = {
        "original": log_data,
        "eventTemplate": obj.get_sequence(),
        "parameterList": obj.param(log_data),
        "datetime": log_fields["datetime"],
        "loglevel": log_fields["level"],
        "pid": log_fields["pid"],
    }

    return result


def parse_log_regex(log_str):
    comp = re.compile(regex)
    res = comp.match(log_str)
    return (
        {
            "datetime": res.group(1),
            "level": res.group(2),
            "pid": res.group(3),
            "msg": res.group(4),
        }
        if res
        else {}
    )


@app.route("/log", methods=["POST"])
def add_log():
    log_data = request.get_data().decode("UTF-8")
    log_data = log_data.strip("\n")
    parsed_log = _parse_log(log_data)

    return json.dumps(parsed_log)


@app.route("/bulk", methods=["POST"])
def bulk_logs():
    log_data = request.get_data().decode("UTF-8")
    logs = log_data.split("\n")
    for log in logs:
        _parse_log(log)
    return slm.tojson()


@app.route("/bulk_to_csv", methods=["POST"])
def bulk_csv():
    log_data = request.get_data().decode("UTF-8")
    csv_data = _logs_to_csv(log_data)
    output = make_response(csv_data)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"

    return output


@app.route("/predict_log/<filename>", methods=["POST"])
def predict_log_file(filename):
    log_data = request.get_data().decode("UTF-8")
    csv_data = _logs_to_csv(log_data)
    res = model.evaluate(csv_data)
    persist_result(filename, res)
    res["predictions"] = {
        k: float(v) for k, v in res["predictions"].items()
    }
    return json.dumps(res)


def _logs_to_csv(log_data):
    si = io.StringIO()
    cw = csv.writer(si)
    logs = log_data.split("\n")
    return_logs = [
        [
            "template",
            "parameters",
            "datetime",
            "loglevel",
            "pid",
        ],
    ]
    for log in logs:
        parsed = _parse_log(log)
        if parsed:
            return_logs.append(
                [
                    parsed["eventTemplate"],
                    parsed["parameterList"],
                    parsed["datetime"],
                    parsed["loglevel"],
                    parsed["pid"],
                ]
            )
    cw.writerows(return_logs)
    return si.getvalue()


def persist_result(filename, evaluation_result):
    
    table = dynamodb.Table(DYNAMO_TABLE_NAME)
    table.put_item(Item = {
        "filename": filename,
        "result": evaluation_result,
        "updated": datetime.utcnow().isoformat()
    })


@app.route("/mappings", methods=["GET", "DELETE"])
def mappings():
    if request.method == "DELETE":
        global slm
        slm = spell.lcsmap("[\\s]+")
    return slm.tojson()


@app.route("/save_mappings", methods=["POST"])
def serialise_mappings():
    spell.save('mappings.pickle', slm)
    return slm.tojson()


def stringify_dynamo_result(entry):
    return {
        "filename": entry["filename"],
        "result": {
            "sequences": [int(seq) for seq in entry["result"]["sequences"]],
            "predictions": {
                k: float(v) for k, v in 
                entry["result"]["predictions"].items()
            }
        }
    }


@app.route("/processed", methods=["GET"])
def list_processed_files():
    table = dynamodb.Table(DYNAMO_TABLE_NAME)
    response = table.scan()
    return json.dumps([stringify_dynamo_result(entry) for entry in response["Items"]])


@app.route("/processed/<filename>", methods=["GET"])
def get_processed_file(filename):
    table = dynamodb.Table(DYNAMO_TABLE_NAME)
    response = table.query(
        KeyConditionExpression=Key('filename').eq(filename)
    )
    return json.dumps([stringify_dynamo_result(entry) for entry in response["Items"]])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)

import boto3
import json
import os
import time
import re
from enum import Enum

print('Loading function')
dynamo = boto3.client('dynamodb')


OPERATIONS = {
    'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
    'GET': lambda dynamo, x: dynamo.scan(**x),
    'POST': lambda dynamo, x: dynamo.put_item(**x),
    'PUT': lambda dynamo, x: dynamo.update_item(**x),
}

class LogStatus(Enum):
    ERROR = 1
    OK = 0

def analysis_handler(input_str, application):
    line = read_log(input_str)
    if line:
        status = log_status(line)
        if status in (LogStatus.ERROR,):
            result = persist_result(line, status, application)
            return f"Persisted {line} of application {application}. Operation result: {result}"
        return "Log not persisted"
    return "Unable to parse log"

def persist_result(line, status, application):
    #upsert to DB
    payload = {
         "Item": {
            "application": {
                "S": application
            },
            "logID": {
                "S": (application + "_" + str(time.time()))
            },
            "message": {
                "S": line
            },
            "status": {
                "S": str(status)
            }
        },
        "TableName": "testDB" #TODO
    }
    return get_operations()["POST"](dynamo, payload)

def log_status(line):
    """
    analyses content of valid log line
    returns LogStatus result
    v1: use regex
    """
    error = re.compile(r"ERROR\W")
    print(error.search(line))
    if error.search(line):
        return LogStatus.ERROR
    return LogStatus.OK

def read_log(input_str):
    #clean "empty" lines - whitesapces, tabs, etc
    #handle IO exception
    #return line in the correct format for analysis 
    line = input_str
    return line

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def get_verb(event):
    try:
        return event["httpMethod"]
    except KeyError:
        return event["requestContext"]['http']["method"]


def get_operations():
    if "true" != os.environ.get("executelocal", "false").lower():
        return OPERATIONS
    return {
        'GET': lambda dynamo, x: {
                "Items": [{
                    "logID": {
                        "S": "log_123"
                    },
                    "application": {
                        "S": "testApp"
                    },
                    "result": {
                        "S": "worked!"
                    }
                }],
                "Count": 1,
                "ScannedCount": 1,
            },

        'POST': lambda dynamo, x: {
            "ResponseMetadata": {
                "RequestId": "5RIHIBC4V8S4AGJ7QQTGVKLPCRVV4KQNSO5AEMVJF66Q9ASUAAJG",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "server": "Server",
                    "date": "Wed, 13 Jan 2021 21:15:32 GMT",
                    "content-type": "application/x-amz-json-1.0",
                    "content-length": "2",
                    "connection": "keep-alive",
                    "x-amzn-requestid": "5RIHIBC4V8S4AGJ7QQTGVKLPCRVV4KQNSO5AEMVJF66Q9ASUAAJG",
                    "x-amz-crc32": "2745614147"
                },
                "RetryAttempts": 0
            }
        }
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    print("Received Event: " + json.dumps(event, indent=2))

    verb = get_verb(event)
    operations = get_operations()
    if verb in operations:
        payload = event['queryStringParameters'] if verb == 'GET' else json.loads(event['body'])

        if verb == "POST":
            print(f"Received POST with payload: {payload}")
            result = analysis_handler(payload["log"], payload["application"])
            print("Result: " + result)
            return respond(None, result)

        result = operations[verb](dynamo, payload)
        return respond(None, result)
    else:
        return respond(ValueError('Unsupported method "{}"'.format(verb)))

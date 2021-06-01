# weapon-x
Log analysis - ML pipeline - TU Dublin BSc Business Analytics final year project 2020

## App

* 
* Log ingestion: line by line (to support stream) or bulk (for batch processing)
* Log parsing: regex to split log blocks. The log message is further parsed using the Spell algorithm, based on the implementation by _inoue.tomoya_ at https://github.com/bave/pyspell
* TODO/WIP: anomaly detection model, log classification model, user interface

### Local development

* Clone repo and from the project root folder spin up docker container to run the Flask application using:
```
docker-compose up
```

## Endpoints



## Dynamo DB
No-SQL key-value database available in the AWS ecosystem.

***AWS proof of concept for next phase of the project, so it's still separated from rest of logic***

### Create a table for test AWS app
Table name:	testDB
Primary partition key:	application (String)
Primary sort key:	logID (String)

## Test AWS application 
A simple backend (read/write to DynamoDB) with a RESTful API endpoint using Amazon API Gateway. Based on the Lambda blueprint at https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway-blueprint.html
Route was configured to accept ANY verb request to the base url; this can be done in API Gateway > Routes. The gateway-id is the one corresponding to the lambda integration - see Integration details for route.

### Test AWS app: GET table contents
```
curl -X GET https://{gateway-id}.execute-api.eu-west-1.amazonaws.com/?TableName=testDB 
```
Sample response:
```
{
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
    "ResponseMetadata": {
        "RequestId": "DGRAGDV0D9SAJ63IR0ORJAS7ERVV4KQNSO5AEMVJF66Q9ASUAAJG",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            "server": "Server",
            "date": "Wed, 13 Jan 2021 21:22:38 GMT",
            "content-type": "application/x-amz-json-1.0",
            "content-length": "119",
            "connection": "keep-alive",
            "x-amzn-requestid": "DGRAGDV0D9SAJ63IR0ORJAS7ERVV4KQNSO5AEMVJF66Q9ASUAAJG",
            "x-amz-crc32": "2296749171"
        },
        "RetryAttempts": 0
    }
}
```
Verify: should match state in DynamoDB > testDB > Items AWS console.

### Test AWS app: POST item to database
```
curl -X POST https://{gateway-id}.execute-api.eu-west-1.amazonaws.com/ -H "Content-Type: application/json" --data-binary @- <<DATA
{ 
  "Item": {
        "application": {
            "S": "testApp"
        },
        "logID": {
            "S": "log_123"
        },
        "result": {
            "S": "worked!"
        }
    },
  "TableName": "testDB"
}
DATA
```
Sample response:

```
{
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
```

---
Why *weapon X*?
Logs, Logan, Wolverine, Weapon X.

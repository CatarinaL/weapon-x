# weapon-x
Log analysis - ML pipeline - TU Dublin BSc Business Analytics final year project 2020/21

## App

/backend
* Log ingestion: line by line (to support stream) or bulk (for batch processing)
* Log parsing: regex to split log blocks. The log message is further parsed using the Spell algorithm, based on the implementation by _inoue.tomoya_ at https://github.com/bave/pyspell
* LSTM-based log classification model (Tensorflow)

/frontend
* Basic Next.js user interface

### Local development

* Clone repo, cd into '/backend', and spin up the docker container to run the Flask application using:

```
docker-compose up
```

## API Endpoints



## Dynamo DB
No-SQL key-value database available in the AWS ecosystem.

## Other directories in this repo

* /prototype contains the first experiments using lambdas and API gateway to serve the app
* /models are serialized versions of the ML models and encoders produced (for reproducibility)
* /data contains the parsed csvs (for reproducibility)

---
Why *weapon X*?
Logs, Logan, Wolverine, Weapon X.

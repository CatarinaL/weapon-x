# weapon-x
Log analysis - ML pipeline - TU Dublin BSc Business Analytics final year project 2020/21

## App

/backend
* Log ingestion: line by line (to support stream) or bulk (for batch processing)
* Log parsing: regex to split log blocks. The log message is further parsed using the Spell algorithm, based on the implementation by _inoue.tomoya_ at https://github.com/bave/pyspell
* LSTM-based log classification model (Tensorflow)

![app_logic_flow](https://user-images.githubusercontent.com/1586447/120364877-abd44480-c305-11eb-9a1b-bc91a5ba148f.png)

![fyp_architecture](https://user-images.githubusercontent.com/1586447/120364956-c4445f00-c305-11eb-9259-32d5e29a2f8e.png)

/frontend
* Basic Next.js user interface

### Local development

* Clone repo, cd into '/backend', and spin up the docker container to run the Flask application using:

```
docker-compose up
```

## API Endpoints

#### /predict_log/ \<filename>
method: POST
returns: JSON of predictions for sequences in file
  
#### /processed
method: GET
returns: JSON of database entries containing filename, predictions and model result
  
#### /processed/\<filename>
method: POST
returns: JSON of database entry corresponding to a file

#### /mappings
method: GET, DELETE
returns: JSON containing Longest Common Subsequence map of extracted log templates (Spell algorithm)
  
## Dynamo DB
No-SQL key-value database available in the AWS ecosystem.

## Other directories in this repo

* /prototype contains the first experiments using lambdas and API gateway to serve the app
* /models are serialized versions of the ML models and encoders produced (for reproducibility)
* /data contains the parsed csvs (for reproducibility)

---
Why *weapon X*?
Logs, Logan, Wolverine, Weapon X.

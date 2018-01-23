Deidre
===========

## IMPORTANT WARNING

Do not commit PHI to this repo!

## Overview

The purpose of Deidre is to de-identify Redox messages.  This is necessary to remove PHI from health records to comply
with HIPAA requirements.

HHS publishes a 
[guidance document](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html#standard) 
on de-identification that defines exactly which fields in a health record need to obfuscated. 

The concept here is that Deidre takes a JSON schema and a JSON data document, and produces a de-identified JSON data
document from this.  Any PHI in the source data document will be replaced with arbitrary values in the resulting file. 

All PHI names are replaced with alliterative arbitrary names. These are generated randomly but
consistently within a single execution from the source's first name.  For example, a user Robert Q. Smith may always
have their name be 'Tommy T. Thompson' across all messages de-identified. MRNs will also have a consistent mapping 
within a single execution.

##  Setting up a dev environment

### Dependencies

* Python 3.6.x (or [pyenv](https://github.com/pyenv/pyenv))
* [pipenv](http://pipenv.org)

### Setting up

```bash
pipenv install --dev
```

### Running the linter

```bash
pipenv run pycodestyle .
```

### Running the tests

```bash
pipenv run pytest tests
```

### Running de-id

**WARNING: these files contain PHI -- keep them safe!**

Create a directory with all of your PHI messages as individual JSON files, e.g., redox_msgs_phi

Enter pipenv for deidre:

```bash
pipenv shell
```

Then run the deid script on those files:
```bash
python deid.py \
  --schemas=schemas/patientadmin-arrival.json,schemas/flowsheet-new.json,schemas/results-new.json,schemas/surgicalscheduling-new.json 
  --mappings=schemas/patientadmin-arrival-map.json,schemas/flowsheet-new-map.json,schemas/results-new-map.json,schemas/surgicalscheduling-new-map.json
  --input=redox_msgs_phi \
  --output=redox_msgs_deided
```

### Running replay

Enter pipenv for deidre:

```bash
pipenv shell
```

--verification-token redox-trivialkey deid_files/*.json
```

or if there are a lot:

### Notes

* Processing will exception out if any string or boolean typed attribute is not defined in the map.  This is 
relevant when the schema is updated, as you get immediate feedback as to which attributes need to have methods mapped
to them.
* null typed attributes are always null (None), no no concern there.
* object and array are always iterated over, so no values are explicitly set there.
* Currently supported datamodels are SurgicalScheduling PatientAdmin Flowsheet Results, here are Redox's (incorrect) 
json schemas:
    * http://developer.redoxengine.com/data-models/SurgicalScheduling.html
    * http://developer.redoxengine.com/data-models/PatientAdmin.html
    * http://developer.redoxengine.com/data-models/Flowsheet.html
    * http://developer.redoxengine.com/data-models/Results.html

# maieutical-labs-challenge

## What this project does

It answers this problem:

```
Il tuo compito è di creare un sistema per monitorare la disponibilità di un
sito web. Il sistema deve prevedere una API HTTP che riceva in ingresso la
richiesta di effettuare il controllo per una data URL.

Per ogni controllo vogliamo salvare in database il tempo di risposta, lo status
code e se il contenuto della risposta fa il match con una espressione regolare
opzionalmente inviata alla API.
```

## How it works

This software needs `Docker` and `make` to be conveniently run.

### Installation, running, test running

There are 6 `make` targets to run:

* `install_and_run`
  * Builds the docker image, launches the database migrations, create a superuser with username `g` and password `g`
    and leaves the Django instance running in background, reachable at `http://127.0.0.1:8000`.
    Admin panel is reachable at `http://127.0.0.1:8000/admin`
* `install`
  * Same as before but adds a `docker-compose down`, so you will need to start the project by hand
* `start`
  * Launches an already installed project
* `stop`
  * Alias for `docker-compose down`
* `test`
  * Launches the test suite with the basic Django test runner
* `coverage`
  * Installs `coverage` (left out from the requirements file to not have it in "production"), runs it on the test
    suite and generates the HTML report in the directory `htmlcov`

### What data to send the program

The path accepting data is `/`, the root path.

It accepts, via `POST` method, a json object with this shape:
```json
{
  "url": "string that contains an url with http or https schema",
  "regex": "string that contains a regex" // Optional
}
```

The program will reply, in case the data you submitted is valid, with an object with this shape:
```json
{
  "uuid": "string that contains an UUID" // Always present. UUID of your request.
  "url": "string that contains an url with http or https schema", // Always present
  "failed_request": bool, // Always present. The server was able to do a request to the website you asked for?
  "regex": "string that contains a regex", // Optional, only present if you passed a regex; mirrors back the argument you passed
  "roundtrip": "string that contains the number of seconds that the request took", // Optional, only present if the request did not fail. It's a stringified float
  "status_code": int, // Optional, only present if the request did not fail. Integer with the status code.
  "matches_regex": bool, // Optional, only present if you passed a regex. Tells if it has been possible to find a match
}
```
with a status code of `201`.

In case you submit invalid data, you will get a response of this shape:
```json
{
    "validation_errors": {
        "wrong data field": ["List of validation messages to correct"]
    }
}
```

with a status code of `400`. There can be more than one wrong data field and more than one message per field.

## Why I designed it like I did

Read the [journal](JOURNAL.md) for the technical spiegone.

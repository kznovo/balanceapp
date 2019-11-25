# Income/Expense tracker

- Uses google spreadsheets as DB

## Requirements

- Python 3.6>=
- MacOS/Linux(Ubuntu)
- `secret` file to manage flask session
- `config.ini` file
- `client_secret.json` file (create credentials at https://console.developers.google.com/ and download the json)

## Quickstart

- on your machine

```console
scripts/gen_secret
scripts/install
scripts/run
```

- or on docker

```
docker build -t <name> .
docker run <name>
```

## API

- [GET] /db/<db name>
  Returns <db name> data from the spreadsheet
- [POST] /db/<db name>
  Appends data from body json to the <db name> spreadsheet.
  json members reflect the actual columns in the sheet.

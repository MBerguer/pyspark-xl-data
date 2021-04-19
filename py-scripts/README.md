# Extractions scripts

## Setup

1. Install python 3.9 (currently using 3.9.1, default in macOS BigSur)
2. Install dependencies with pip
   ```
   pip install --pre -r requirements.txt
   ```

> Notice in stock macOS python 3.9.1 is available as `python3` command and pip as `pip3` command.

## Scripts

### extract_info_from_gh_api

Fetch repositories data from Github API. Repositories are given by URL and read from a text file passed in as first argument.

Example of use:

```bash
source .env
python3 extract_info_from_gh_api.py repos.txt 
```

The result will be stored in the `output/repos.json` file.
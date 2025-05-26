# Frontend Demo Project
This a front end application written in [reflex.dev](https://reflex.dev/) that will be used query a database and display the results in a table.
The app will connect to the api service layer running as the middletier. The api layer will be responsible for connecting to the database and returning data in json format.

# Requirements
The assumption here is you have a mac. Please adapt for linux or windows.
- Python 3.11+
- uv (pip3 install uv)
Most of the requirements are captured in [pyproject.toml](./pyproject.toml) file.

## Installation
1. Download the zip file.
2. Create virtual environment: `uv venv`
3. Activate virtual environment: `source .venv/bin/activate`
4. Install requirements: `uv sync`
5. Run app: `reflex run`
6. Open browser and navigate to http://localhost:3000

# Usage
- Navigate to the home page at http://localhost:3000
- Click on "New Request"
- Set to "GET"
- Set URL to middletier url: http://localhost:8000/items/
    - NOTE: it's important the url endpoint ends in a trailing slash "/"
- Add Headers
    - key: medical_record_number
    - value: 1000
    - X-API-Key: `<whatever you set>`
- You should see the table populate with data.
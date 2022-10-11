# Data Products

## Prerequisites

* Python 3.9+
* [Poetry](https://python-poetry.org/docs/)
* PostgreSQL or Docker
* [Caddy](https://caddyserver.com/v2)

## Setup

0. If using Poetry, run `poetry env use $(pyenv which python)` to ensure Poetry is using the right Python configuration.

1. Install dependencies with Poetry. This will also create a virtual environment at `.venv` if it does not exist yet.

   ```bash
   poetry install
   ```

2. Activate the virtual environment. The command is different depending on your OS and shell.
   Alternatively, `poetry shell` may work, but it might not launch the correct shell.

   | OS                            | Shell                           | Command                          |
   |-------------------------------|---------------------------------|----------------------------------|
   | Windows                       | PowerShell (preferred)          | `.venv/Scripts/Activate.ps1`     |
   | Windows                       | Command Prompt (don't use this) | `.venv/Scripts/activate.bat`     |
   | Windows                       | Unix shell (eg. Git Bash)       | `source .venv/Scripts/activate`  |
   | Unix-like (eg. Ubuntu, macOS) | Unix shell (eg. bash, zsh)      | `source .venv/bin/activate`      |
   | Unix-like                     | fish                            | `source .venv/bin/activate.fish` |

3. Set up the database. Refer to [Database setup](#database-setup) for instructions on setting up the database locally
   or within Docker.

4. Run database migrations.

   ```bash
    alembic upgrade head
   ```

5. Set up pre-commit hooks.

   ```bash
   pre-commit install
   ```

6. Start the development server. This will listen on localhost:8000

   ```bash
   python app.py
   ```

## Database setup

### Option 1: Local PostgreSQL installation

1. Use `psql` to create a new user and database for the application with appropriate permissions:

   ```bash
   echo "create user dataproducts login password 'password';
   create database dataproducts owner dataproducts;
   alter user dataproducts createdb;" | psql -d postgres
   ```

### Option 2: Running PostgreSQL in Docker

1. Create a volume to persist the database between container restarts:

   ```bash
   docker volume create dataproducts_db
   ```

2. Start the database container:

   ```bash
   docker run -d -v dataproducts_db:/var/lib/postgresql/data -e POSTGRES_USER=dataproducts -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dataproducts -p 5432:5432 --name dataproducts_db postgres
   ```

## Heroku Poetry Buildpack setup

This removes need to generate `runtime.txt` and `requirements.txt` as they are auto generated. [Source](https://elements.heroku.com/buildpacks/moneymeets/python-poetry-buildpack)

```bash
heroku buildpacks:clear
heroku buildpacks:add https://github.com/moneymeets/python-poetry-buildpack.git
heroku buildpacks:add heroku/python
heroku config:set PYTHON_RUNTIME_VERSION=3.9.14
heroku config:set POETRY_VERSION=1.2.1
heroku config:set POETRY_EXPORT_DEV_REQUIREMENTS=1
heroku config:set DISABLE_POETRY_CREATE_RUNTIME_FILE=0
```

## Notes

1. Generate migration with alembic:

    ```bash
    mkdir -p db/versions
    alembic revision --autogenerate -m 'initial DB model commit'
    ```

2. Apply migration

    ```bash
    alembic upgrade head
    ```

2. Undo migration

    ```bash
    alembic downgrade -1
    ```

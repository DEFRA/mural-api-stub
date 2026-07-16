# mural-api-stub

This is work-in-progress. See [To Do List](./TODO.md)

- [mural-api-stub](#mural-api-stub)
  - [Requirements](#requirements)
    - [Python](#python)
    - [Linting and Formatting](#linting-and-formatting)
    - [Docker](#docker)
  - [Local development](#local-development)
    - [Setup & Configuration](#setup--configuration)
    - [Development](#development)
    - [Testing](#testing)
    - [Production Mode](#production-mode)
  - [API endpoints](#api-endpoints)
  - [Custom Cloudwatch Metrics](#custom-cloudwatch-metrics)
  - [Pipelines](#pipelines)
    - [Dependabot](#dependabot)
    - [SonarCloud](#sonarcloud)
  - [Licence](#licence)
    - [About the licence](#about-the-licence)

## Requirements

### Python

Please install python `>= 3.12` and `pipx` in your environment. This template uses [uv](https://github.com/astral-sh/uv) to manage the environment and dependencies.

```python
# install uv via pipx
pipx install uv

# sync dependencies
uv sync

# source python venv
source .venv/bin/activate

# install the pre-commit hooks
pre-commit install
```

This opinionated template uses the [`Fast API`](https://fastapi.tiangolo.com/) Python API framework.

### Environment Variable Configuration

The application uses Pydantic's `BaseSettings` for configuration management in `app/config.py`, automatically mapping environment variables to configuration fields. Configuration is loaded using `python-dotenv` which supports both `.env` files and environment variables.

In CDP, environment variables and secrets need to be set using CDP conventions. See links below:
- [CDP App Config](https://github.com/DEFRA/cdp-documentation/blob/main/how-to/config.md)
- [CDP Secrets](https://github.com/DEFRA/cdp-documentation/blob/main/how-to/secrets.md)

For local development - see [instructions below](#local-development).

### Linting and Formatting

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting Python code.

#### Running Ruff

To run Ruff from the command line:

```bash
# Run linting with auto-fix
uv run ruff check . --fix

# Run formatting
uv run ruff format .
```

#### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to run linting and formatting checks automatically before each commit.

The pre-commit configuration is defined in `.pre-commit-config.yaml`

To set up pre-commit hooks:

```bash
# Set up the git hooks
pre-commit install
```

To run the hooks manually on all files:

```bash
pre-commit run --all-files
```

#### VS Code Configuration

For the best development experience, configure VS Code to use Ruff:

1. Install the [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) for VS Code
2. Configure your VS Code settings (`.vscode/settings.json`):

```json
{
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": "explicit",
        "source.organizeImports.ruff": "explicit"
    },
    "ruff.lint.run": "onSave",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    }
}
```

This configuration will:

- Format your code with Ruff when you save a file
- Fix linting issues automatically when possible
- Organize imports according to isort rules

#### Ruff Configuration

Ruff is configured in the `.ruff.toml` file

### Docker

This repository uses Docker throughput its lifecycle i.e. both for local development and the environments. A benefit of this is that environment variables & secrets are managed consistently throughout the lifecycle

See the `Dockerfile` and `compose.yml` for details

## Local development

### Setup & Configuration

Follow the convention below for environment variables and secrets in local development.

**Environment variables:** `.env` file in the project root.

**Compose directory:** The `compose/` directory contains helper scripts and environment configurations:
- `compose/floci/start.d/10-setup-resources.sh` - This script is used to set up the necessary AWS resources in the local Floci environment. It runs when the Floci container starts, ensuring that your local AWS environment is ready for development.

**Libraries:** Ensure the python virtual environment is configured and libraries are installed using `uv sync`, [as above](#python)

**Pre-Commit Hooks:** Ensure you install the pre-commit hooks, as above

### Development

This app can be run locally by either using the Docker Compose project or project scripts.

#### Using Docker Compose

To run the application using Docker Compose, you can use the following command:

```bash
docker compose up --build
```

If you want to enable hot-reloading, you can press the `w` key once the compose project is running to enable `watch` mode.

#### Using Project Scripts

To run the application using the project scripts, you can use the following command:

```bash
uv run --env-file .env mural-api-stub
```

### Testing

Ensure the python virtual environment is configured and libraries are installed using `uv sync`, [as above](#python)

Testing follows the [FastApi documented approach](https://fastapi.tiangolo.com/tutorial/testing/); using pytest & starlette.

To test the application run:

```bash
uv run pytest
```

## API endpoints

| Endpoint                           | Method | Description                           |
| :--------------------------------- | :----- | :------------------------------------ |
| `GET: /health`                     | GET    | Health check endpoint                 |
| `POST: /api/public/v1/authorization/oauth2/token` | POST | Fake OAuth2 token endpoint (stub tokens, no credential validation) |
| `GET: /api/public/v1/murals/{id}`  | GET    | Get a mural (board)                   |
| `GET: /api/public/v1/murals/{id}/widgets` | GET    | Get widgets in a mural with pagination |
| `GET: /docs`                       | GET    | Automatic API Swagger docs            |

### Example cURL requests

#### Health check

```bash
curl http://localhost:8085/health
```

Response (200):
```json
{"status": "ok"}
```

#### OAuth2 token (fake)

Real OAuth is out of scope for this stub (see [developers.mural.co/public/docs/oauth](https://developers.mural.co/public/docs/oauth)), but the MCP server calls Mural's token endpoint constantly to keep its 15-minute access token fresh. This endpoint returns freshly generated stub tokens for both `authorization_code` and `refresh_token` grants, without validating any credentials. It accepts either form-encoded or JSON request bodies.

```bash
# authorization_code grant (form-encoded)
curl -s -X POST http://localhost:8085/api/public/v1/authorization/oauth2/token \
  -d grant_type=authorization_code -d client_id=x -d client_secret=y \
  -d code=abc -d redirect_uri=http://localhost/cb

# refresh_token grant (JSON)
curl -s -X POST http://localhost:8085/api/public/v1/authorization/oauth2/token \
  -H 'Content-Type: application/json' \
  -d '{"grant_type":"refresh_token","refresh_token":"old"}'
```

Response (200):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 900
}
```

Error (400, unknown/missing `grant_type`):
```json
{
  "error": "unsupported_grant_type",
  "error_description": "Unsupported grant_type: 'client_credentials'"
}
```

#### Get a mural

```bash
# Retrieve a mural by ID (using workspace.board format or default workspace)
curl http://localhost:8085/api/public/v1/murals/workspace1.board1
```

Response (200):
```json
{
  "value": {
    "id": "board1",
    "title": "Demo Board",
    ...
  }
}
```

Error (404):
```json
{
  "code": "MURAL_NOT_FOUND",
  "message": "Mural not found: workspace1.missing"
}
```

#### Get mural widgets

```bash
# Get all widgets in a mural
curl http://localhost:8085/api/public/v1/murals/workspace1.board1/widgets

# Get widgets with pagination (limit 10 per page)
curl "http://localhost:8085/api/public/v1/murals/workspace1.board1/widgets?limit=10"

# Get the next page using the cursor from the previous response
curl "http://localhost:8085/api/public/v1/murals/workspace1.board1/widgets?limit=10&next=10"

# Filter by widget type(s) (comma-separated)
curl "http://localhost:8085/api/public/v1/murals/workspace1.board1/widgets?type=sticky,text"

# Filter by parent ID (for nested widgets)
curl "http://localhost:8085/api/public/v1/murals/workspace1.board1/widgets?parentId=parent123"

# Combine filters and pagination
curl "http://localhost:8085/api/public/v1/murals/workspace1.board1/widgets?type=sticky&parentId=parent123&limit=5"
```

Response (200):
```json
{
  "value": [
    {
      "id": "widget1",
      "type": "sticky",
      "parentId": null,
      ...
    },
    {
      "id": "widget2",
      "type": "text",
      "parentId": "parent123",
      ...
    }
  ],
  "next": "2"
}
```

Error responses (400):
```json
{
  "code": "PAGINATION_INVALID",
  "message": "Invalid pagination token: abc"
}
```

```json
{
  "code": "LIMIT_INVALID",
  "message": "Invalid limit: 0"
}
```

Error (404):
```json
{
  "code": "MURAL_NOT_FOUND",
  "message": "Mural not found: workspace1.missing"
}
```

## Custom Cloudwatch Metrics

Uses the [aws embedded metrics library](https://github.com/awslabs/aws-embedded-metrics-python). An example can be found in `metrics.py`

In order to make this library work in the environments, the environment variable `AWS_EMF_ENVIRONMENT=local` is set in the app config. This tells the library to use the local cloudwatch agent that has been configured in CDP, and uses the environment variables set up in CDP `AWS_EMF_AGENT_ENDPOINT`, `AWS_EMF_LOG_GROUP_NAME`, `AWS_EMF_LOG_STREAM_NAME`, `AWS_EMF_NAMESPACE`, `AWS_EMF_SERVICE_NAME`

## Pipelines

### Dependabot

We have added an example dependabot configuration file to the repository. You can enable it by renaming
the [.github/example.dependabot.yml](.github/example.dependabot.yml) to `.github/dependabot.yml`

### SonarCloud

Instructions for setting up SonarCloud can be found in [sonar-project.properties](./sonar-project.properties)

## Licence

THIS INFORMATION IS LICENSED UNDER THE CONDITIONS OF THE OPEN GOVERNMENT LICENCE found at:

<http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3>

The following attribution statement MUST be cited in your products and applications when using this information.

> Contains public sector information licensed under the Open Government license v3

### About the licence

The Open Government Licence (OGL) was developed by the Controller of Her Majesty's Stationery Office (HMSO) to enable
information providers in the public sector to license the use and re-use of their information under a common open
licence.

It is designed to encourage use and re-use of information freely and flexibly, with only a few conditions.

FROM python:3.9-slim-buster

# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Get build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-dev build-essential libssl-dev libffi-dev rustc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade poetry

# Create working directory
WORKDIR /bot

# Copy depenencies and lockfile
COPY pyproject.toml poetry.lock /bot/

# Get the bot dependencies, then remove build dependencies
RUN poetry install --no-dev --no-interaction --no-ansi \
    && apt-get purge -y --auto-remove python3-dev build-essential libssl-dev libffi-dev rustc \
    && rm -rf /var/lib/apt/lists/*

# Copy source
COPY . .

# Run the app
ENTRYPOINT [ "python3" ]
CMD [ "-m", "griffinbot" ]

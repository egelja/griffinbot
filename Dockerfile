FROM python:3.9-slim-buster

# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Pipenv
RUN pip install -U pipenv

# Create working directory
WORKDIR /bot

# Download dependenices
COPY Pipfile* ./
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-dev build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pipenv sync --system \
    && apt-get purge -y --auto-remove python3-dev build-essential

# Copy source
COPY . .

# Run the app
ENTRYPOINT [ "python3" ]
CMD [ "-m", "griffinbot" ]

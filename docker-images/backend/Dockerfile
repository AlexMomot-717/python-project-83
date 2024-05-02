FROM python:3.11.7

WORKDIR /app

# Copy the source code into the container.
COPY pyproject.toml poetry.lock /app/
COPY page_analyzer /app/page_analyzer

# Install Poetry
RUN pip install poetry

# Skipping virtualenv creation
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install

# configure the container to run in an executed manner
ENTRYPOINT ["gunicorn", "-w", "5", "-b", "0.0.0.0:8000", "page_analyzer:app"]

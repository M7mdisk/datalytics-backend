FROM python:3.9-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libpq-dev libjpeg-dev zlib1g-dev \
    && pip3 install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc build-essential

FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m app

USER app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /api

COPY . .

ENTRYPOINT ["python3","manage.py"]
CMD ["runserver", "0.0.0.0:8000"]

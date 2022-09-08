FROM python:3.10

RUN mkdir /app
WORKDIR /app

ADD data/my-crontab /etc/cron.d/my-crontab
RUN chmod 0644 /etc/cron.d/my-crontab
RUN touch /var/log/cron.log

COPY pyproject.toml /app
COPY update_scores.* /app
ENV PYTHONPATH=${PYTHONPATH}:${PWD}
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

RUN apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | apt-key add - && \
    echo "deb https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
    apt-get update && \
    apt-get -y install \
    doppler \
    uuid-runtime \
    cron \
    vim

RUN crontab /etc/cron.d/my-crontab

CMD cron && tail -f /var/log/cron.log
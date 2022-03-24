FROM python:3.9

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV VERIFY_REQUEST_URL ${VERIFY_REQUEST_URL:-https://laozi-testnet4.bandchain.org/api/oracle/v1/verify_request}
ENV ENDPOINT_URL ${ENDPOINT_URL:-https://local.example}
ENV ALLOW_DATA_SOURCE_IDS ${ALLOW_DATA_SOURCE_IDS:-}
ENV HEADER_KEY ${HEADER_KEY}
ENV HEADER_VALUE ${HEADER_VALUE}

WORKDIR $APP_HOME

COPY ./ ./

RUN python -m pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

CMD exec sanic main:app --host=${HOST:-0.0.0.0} --port=${PORT:-8080} --fast

FROM python:3.9

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ./ ./

RUN python -m pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["sanic", "main:app", "--host=0.0.0.0", "--fast"]

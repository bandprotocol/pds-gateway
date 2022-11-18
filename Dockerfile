FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ./ ./

RUN python -m pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--host=0.0.0.0"]

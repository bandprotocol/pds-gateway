FROM python:3.9

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

WORKDIR $APP_HOME

COPY ./ ./

RUN python -m pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

CMD exec sanic main:app --host=0.0.0.0 --port=$PORT --fast
# CMD exec python main.py


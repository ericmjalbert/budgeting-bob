FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install  -r /app/requirements.txt

COPY . /app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:my_app"]


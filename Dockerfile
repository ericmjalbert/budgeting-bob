FROM python:3.9

# RUN apt-get update \
#     && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
#         libsqlite3-dev \
#         python3-pip \
#         python3-setuptools \
#     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install  -r /app/requirements.txt

COPY . /app

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:my_app"]


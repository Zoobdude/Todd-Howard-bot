FROM python:slim

COPY ./src/logic.py /logic.py
COPY ./src/requirements.txt /requirements.txt
COPY ./src/main.py /main.py

# Create a volume for the json data
VOLUME /data

RUN pip install -r /requirements.txt

CMD ["python", "/main.py"]
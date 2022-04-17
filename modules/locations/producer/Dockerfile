FROM python:3.7-alpine

WORKDIR .

RUN apk add --no-cache gcc g++ musl-dev linux-headers libc-dev
COPY producer/requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 50001

COPY producer/ .
COPY ./proto/ .

RUN python3 -m grpc_tools.protoc -I./ --python_out=. --grpc_python_out=. ./location.proto


CMD ["python3", "producer.py"]
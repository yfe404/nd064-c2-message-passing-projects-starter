from os import environ as env
from kafka import KafkaProducer

from concurrent import futures
import logging

from retry import retry

import grpc
import location_pb2
import location_pb2_grpc

TOPIC_NAME = env.get("TOPIC_NAME")
KAFKA_HOST = env.get("KAFKA_HOST")
KAFKA_PORT = env.get("KAFKA_PORT")

KAFKA_SERVER = f'{KAFKA_HOST}:{KAFKA_PORT}'


@retry(tries=5, delay=2)
def init_producer():
    return KafkaProducer(bootstrap_servers=KAFKA_SERVER)


class LocationServicer(location_pb2_grpc.Location):

    def __init__(self):
        pass

    def AddLocation(self, request, context):
        logging.warning(request)
        event = request.SerializeToString()

        producer.send(TOPIC_NAME, event)
        producer.flush()

        return location_pb2.Response()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    location_pb2_grpc.add_LocationServicer_to_server(
        LocationServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    producer = init_producer()
    serve()

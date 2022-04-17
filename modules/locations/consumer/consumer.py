from os import environ as env
from kafka import KafkaConsumer

from concurrent import futures
import logging

from retry import retry

import grpc
import location_pb2
import location_pb2_grpc

import models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from geoalchemy2.functions import ST_AsText, ST_Point

TOPIC_NAME = env.get("TOPIC_NAME")
KAFKA_HOST = env.get("KAFKA_HOST")
KAFKA_PORT = env.get("KAFKA_PORT")

KAFKA_SERVER = f'{KAFKA_HOST}:{KAFKA_PORT}'


DB_USERNAME = env.get("DB_USERNAME")
DB_NAME = env.get("DB_NAME")
DB_HOST = env.get("DB_HOST")
DB_PORT = env.get("DB_PORT")
DB_PASSWORD = env.get("DB_PASSWORD")

engine = create_engine(
    f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
Session = sessionmaker()
Session.configure(bind=engine)

session = Session()

@retry(tries=5, delay=2)
def init_consumer():
    return KafkaConsumer(TOPIC_NAME, bootstrap_servers=KAFKA_SERVER)


if __name__ == '__main__':
    logging.basicConfig()
    consumer = init_consumer()

    for message in consumer:

        location = location_pb2.LocationRequest()
        location.ParseFromString(message.value)

        logging.warning(f"Received : {location}")

        coordinate = ST_Point(location.latitude, location.longitude)

        
        payload = {
            "person_id": location.person_id,
            "coordinate": coordinate
        }
        
        new_location = models.Location(**payload)
        session.add(new_location)
        session.commit()

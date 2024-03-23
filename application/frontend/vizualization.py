import argparse
import json
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

from confluent_kafka import Consumer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    with open(args.config) as conf:
        config = json.load(conf)

    topic = config['inference_topic']
    consumer_conf = {'bootstrap.servers': config['bootstrap.servers'], 'group.id': 'my_consumers'}

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])
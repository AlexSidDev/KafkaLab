import argparse
from confluent_kafka import Producer
import json
import random
import time
from transformers import AutoTokenizer

from preprocess_utils import process_sample, TokenizerNER


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    with open(args.config) as conf:
        config = json.load(conf)

    topic = config["preprocess_topic"]

    conf = {'bootstrap.servers': config['bootstrap.servers']}
    producer = Producer(conf)

    data_path = config['data_path']
    with open(data_path, 'r') as fin:
        data = fin.read().split('\n\n')

    num_samples = len(data)

    labels_mapping = config['labels_mapping']

    tokenizer = AutoTokenizer.from_pretrained(config['model'])
    processor = TokenizerNER(tokenizer, labels_mapping)

    while True:
        sample_ind = random.randint(1, num_samples - 1)  # first row is not valid
        sample = data[sample_ind]
        if sample.startswith('-DOCSTART-'):
            continue
        red_sample = process_sample(sample)
        processed_sample = processor(red_sample)
        processed_sample['words'] = red_sample['words']

        producer.produce(topic, key='1', value=json.dumps(processed_sample))
        producer.flush()

        time.sleep(5)
        time.sleep(random.random() * 5)




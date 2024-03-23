import argparse
import json
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

from confluent_kafka import Consumer, Producer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    with open(args.config) as conf:
        config = json.load(conf)

    topic = config['preprocess_topic']
    consumer_conf = {'bootstrap.servers': config['bootstrap.servers'], 'group.id': 'my_consumers'}

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    producer_conf = {'bootstrap.servers': config['bootstrap.servers']}
    producer = Producer(producer_conf)
    producer_topic = config["inference_topic"]

    labels_mapping = config['labels_mapping']

    device = config['device']
    model = AutoModelForTokenClassification.from_pretrained(config['model']).to(device)

    while True:
        msg = consumer.poll(1000)

        if msg is not None:
            print(msg.value())
            sample_data = json.loads(msg.value().decode('utf-8'))
            labels = sample_data.pop('labels')
            word_inds = sample_data.pop('word_inds')

            input_ids = torch.tensor(sample_data['input_ids'], dtype=torch.int64).to(device).unsqueeze(0)
            logits = model(input_ids=input_ids).logits
            preds = torch.argmax(logits, -1)[0]

            outputs = {'preds': preds, 'labels': labels, 'word_inds': word_inds}
            producer.produce(producer_topic, key='1', value=json.dumps(processed_sample))
            producer.flush()



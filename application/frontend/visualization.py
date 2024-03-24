import argparse
import json
import streamlit as st
import torch

from confluent_kafka import Consumer

from visualization_utils import PredsToHTMLProcessor


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config.json')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    with open(args.config) as conf:
        config = json.load(conf)

    topic = config['inference_topic']
    consumer_conf = {'bootstrap.servers': config['bootstrap.servers'],
                     'group.id': 'my_consumers'}

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    st.set_page_config(
        page_title="Automatic named entity highlighting",
        layout="wide",
    )

    reversed_labels_mapping = {v: k for k, v in config["labels_mapping"].items()}
    model_output_processor = PredsToHTMLProcessor(reversed_labels_mapping, config["colors_mapping"])

    markdown = st.sidebar.markdown(
        "<h2>Automatic named entity highlighting</h2>"
        "<h4>Entities:</h4>"
        "<ul>"
        f"<li><span style='background-color:rgba(255, 255, 128, .8)'>Person</span></li>"
        f"<li><span style='background-color:rgba(30,129,176, .7)'>Organization</span></li>"
        f"<li><span style='background-color:rgba(228,52,52, .7)'>Location</span></li>"
        f"<li><span style='background-color:rgba(200, 114, 226, .7)'>Miscellaneous</span></li>"
        "<li>Background</span></li>"
        "</ul>",
        unsafe_allow_html=True,
    )

    while True:
        msg = consumer.poll(1000)
        if msg is not None:

            data = json.loads(msg.value().decode('utf-8'))
            html_string = model_output_processor.process_model_output(data['preds'], data['words'], data['word_inds'])
            st.write(html_string, unsafe_allow_html=True)



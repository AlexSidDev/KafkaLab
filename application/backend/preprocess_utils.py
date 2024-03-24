import torch
from transformers import PreTrainedTokenizer


def process_sample(sample: str):
    lines = sample.split('\n')
    words = []
    ner_labels = []
    for line in lines:
        split_line = line.split()
        words.append(split_line[0])
        ner_labels.append(split_line[-1])
    return {'words': words, 'labels': ner_labels}


class TokenizerNER:
    def __init__(self, base_tokenizer: PreTrainedTokenizer, labels_mapping: dict):
        self.base_tokenizer = base_tokenizer
        self.labels_mapping = labels_mapping

    def __call__(self, sample: dict):
        tokenized_inputs = self.base_tokenizer(sample['words'], truncation=True,
                                               is_split_into_words=True,
                                               add_special_tokens=False)

        row_tokens, word_inds = tokenized_inputs['input_ids'], tokenized_inputs.word_ids()

        row_labels = []
        for word_ind in word_inds:
            label = sample['labels'][word_ind]
            label = self.labels_mapping[label]
            row_labels.append(label)

        return {'input_ids': row_tokens, 'labels': row_labels, 'word_inds': word_inds}

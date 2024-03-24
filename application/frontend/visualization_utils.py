

class PredsToHTMLProcessor:
    def __init__(self, labels_mapping: dict, colors_mapping: dict):
        self.labels_mapping = labels_mapping
        self.colors_mapping = colors_mapping

    def decode_labels(self, preds: list, word_inds: list):
        decoded_labels = ['O'] * (max(word_inds) + 1)
        for pred, word in zip(preds, word_inds):
            if decoded_labels[word] != 'O':
                continue
            decoded_labels[word] = self.labels_mapping[pred]
        return decoded_labels

    def colorize_word(self, word: str, label: str):
        cleaned_label = label.split('-')[-1]
        color = self.colors_mapping[cleaned_label]
        template = f'<span style="background-color:{color}">{word}</span>'
        return template

    def make_colorized_html(self, word_labels: list, real_words: list):
        assert len(word_labels) == len(real_words)
        for i in range(len(word_labels)):
            if word_labels[i] != 'O':
                real_words[i] = self.colorize_word(real_words[i], word_labels[i])
        html_string = ' '.join(real_words)
        return html_string

    def process_model_output(self, preds: list, real_words: list, word_inds: list):
        decoded_labels = self.decode_labels(preds, word_inds)
        colorized_html = self.make_colorized_html(decoded_labels, real_words)
        return colorized_html

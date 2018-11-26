import re
import numpy as np
from gensim.models import Word2Vec
from typing import List


class Analyzer:
    def __init__(self):
        self.model = None

    def normalization_word(self, word: str) -> str:
        return word.lower()

    def normalization(self, sentence: str) -> List:
        return list(map(lambda x: self.normalization_word(x), re.findall(r'[А-яA-z]+', sentence)))

    def predict(self, sentence, sentence_2):
        return self.model.n_similarity(
            self.normalization(sentence),
            self.normalization(sentence_2)
        )

    def load_model(self, path='word2vec.model'):
        self.model = Word2Vec.load(path)

    def train_model(self, data, size=100, iter=100, window=50, min_count=1, workers=20, **kwargs):
        self.model = Word2Vec(data, size=size, iter=iter, window=window, min_count=min_count, workers=workers, **kwargs)

    def load_data_from_txt(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            data = file.read()
        return list(map(lambda x: self.normalization(x), data.split('\n')))

    def save_model(self, path='word2vec.model'):
        self.model.save(path)

    def word_to_vec(self, word):
        return self.model.wv[self.normalization_word(word)]

    def sentence_to_vec(self, sentence) -> List[np.ndarray]:
        return sum(list(map(lambda x: self.word_to_vec(x), self.normalization(sentence))))
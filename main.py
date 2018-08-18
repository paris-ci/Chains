import collections
import random
import time
import typing
import unicodedata

import itertools
import requests
from tqdm import tqdm


class BaseCorpus:
    def __init__(self):
        pass

    @property
    def model(self) -> dict:
        # In subclasses, you'd have to do something so that we can use the model with self.model
        return None

    @model.setter
    def model(self, value):
        self._model = value

    @model.deleter
    def model(self):
        pass

    def create_markov(self, sentences: list) -> dict:
        start_time = time.time()

        model = collections.defaultdict(collections.Counter)

        for sentence in tqdm(sentences, desc="Processing corpus into the model"):
            sentence_splitted = sentence.split(" ")
            next_word = sentence_splitted[0]
            for i in range(len(sentence_splitted) - 1):
                current_word = sentence_splitted[i]
                next_word = sentence_splitted[i + 1]

                model[current_word][next_word] += 1

            model[next_word]["__END__"] += 1

        end_time = time.time()
        print(f"Processing the corpus into the model took {round(end_time-start_time, 3)}s")

        return model

    def make_sentence_with_start(self, start: str) -> str:
        current = start.split(" ")
        while current[-1] != "__END__":
            current_word = current[-1]
            possibilites_counter = self.model[current_word]

            i = random.randrange(sum(possibilites_counter.values()))

            next_word = next(itertools.islice(possibilites_counter.elements(), i, None))

            current.append(next_word)

        string = " ".join(current[:-1]).capitalize()
        return string


class DuckHuntCorpus(BaseCorpus):
    def __init__(self):
        super().__init__()
        self.url = 'http://duckhunt.api-d.com/messages.txt'
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = self.create_markov(self.process_corpus(self.download()))

        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @model.deleter
    def model(self):
        if self._model:
            self._model = None

    def update(self):
        del self.model

    def download(self) -> requests.Response:
        """
        Download the corpus with a progress bar shown to the user
        :return:
        """
        # Streaming, so we can iterate over the response.
        r = requests.get(self.url, stream=True)

        return r

    def process_corpus(self, file: requests.Response) -> list:

        start_length = 0
        start_time = time.time()

        lines_parsed = []

        for line in tqdm(file.iter_lines(), desc="Downloading and processing text corpus"):
            start_length += 1
            line = line.decode()
            message = line.lower().strip()
            try:
                message_ = unicodedata.normalize('NFKD', message)

            except:
                message_ = message

            if message_ is None:
                message_ = message

            message = message_

            message = unicodedata.normalize('NFKD', message)

            if len(message) < 2:
                continue

            if message.startswith('dh'):
                continue

            if any([x in message for x in ['nigga', 'http', 'discord.gg', 'fuck', 'hentai']]):
                continue

            for word in message.split(" "):
                if len(word) > 15:
                    break
            else:
                lines_parsed.append(message)

        lines_parsed = sorted(list(set(lines_parsed)))

        end_length = len(lines_parsed)
        end_time = time.time()

        print(f"Fixing the corpus text took {round(end_time-start_time, 3)}s, and the corpus was trimmed from {start_length} to {end_length} lines (diff: {end_length-start_length})")

        return lines_parsed


c = DuckHuntCorpus()

c.model  # Pre-load

print("I AM READY!\n\n")

try:
    while True:
        inp = input('>>> ')
        try:
            inp_ = unicodedata.normalize('NFKD', inp)

        except:
            inp_ = inp

        if inp_ is None:
            inp_ = inp

        print(c.make_sentence_with_start(inp_).capitalize())
except:
    print("bai!")
    raise

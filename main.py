import time
import typing
import unicodedata

import markovify
import requests
from tqdm import tqdm


class BaseCorpus:
    def __init__(self):
        pass

    @property
    def model(self) -> typing.Union[markovify.NewlineText, markovify.Text]:
        # In subclasses, you'd have to do something so that we can use the model with self.model
        return None

    @model.setter
    def model(self, value):
        self._model = value

    @model.deleter
    def model(self):
        pass

    def make_sentence(self, max_words: int = None):
        s = self.model.make_sentence(max_words=max_words)

        if not s:
            s = 'None'
            
        return s

    def make_short_sentence(self, chars: int = 140, more_or_less: int = 20):
        s = self.model.make_short_sentence(max_chars=chars + more_or_less, min_chars=chars - more_or_less)

        if not s:
            s = 'None'

        return s

    def make_sentence_with_start(self, start: str):
        s = self.model.make_sentence_with_start(start.lower().strip(), strict=False)

        if not s:
            s = 'None'

        return s

    def save(self, file_name):
        with open(file_name, 'w') as file:
            file.write(self.model.to_json())


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

    def process_corpus(self, file: requests.Response) -> str:

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

        print(f"Processing the corpus took {round(end_time-start_time, 3)}s, and the corpus was trimmed from {start_length} to {end_length} lines (diff: {end_length-start_length})")

        return "\n".join(lines_parsed)

    def create_markov(self, text: str) -> markovify.NewlineText:
        return markovify.NewlineText(text, state_size=4, retain_original=False)

    def load(self, file_name):
        start_time = time.time()
        with open(file_name, 'r') as file:
            model = markovify.NewlineText.from_json(file.read())

        end_time = time.time()
        print(f'Recovered model from file in {round(end_time-start_time, 3)}s')
        self.model = model


c = DuckHuntCorpus()
c.save('model.json')
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

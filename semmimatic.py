import markovify
import portalocker
import typing
import re

# i'm a sinner
class Semmimatic:
    def __init__(self, quote_path, newline=True):
        self.quote_path = quote_path
        self.newline = newline
        self.build_model(newline)
    def build_model(self, newline : typing.Optional[bool] = None):
        with portalocker.Lock(self.quote_path, "r") as text_file:
            new_newline = newline if newline is not None else self.newline
            if newline:
                self.model = markovify.NewlineText(text_file.read())
            else:
                self.model = ModelText(text_file.read())
    def add_message(self, content):
        with portalocker.Lock(self.quote_path, "a") as text_file:
            text_file.write(message.content)
            text_file.write("\r\r\r\n")

class ModelText(markovify.Text):
    def sentence_split(self, text):
        return re.split(r"\s*\n\n\n\n\s*", text)

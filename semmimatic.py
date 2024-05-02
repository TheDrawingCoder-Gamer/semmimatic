import markovify

# i'm a sinner
class Semmimatic:
    def __init__(self, user_id, quote_path, newline=True):
        self.user_id = user_id
        self.quote_path = quote_path
        self.build_model(newline)
    def build_model(self, newline=True):
        with open(self.quote_path) as text_file:
            if newline:
                self.model = markovify.NewlineText(text_file.read())
            else:
                self.model = ModelText(text_file.read())
    def add_message(self, content):
        with open(self.quote_path, "a") as text_file:
            text_file.write(message.content)
            text_file.write("\r\r\r\n")

class ModelText(markovify.Text):
    def sentence_split(self, text):
        return re.split(r"\s*\r\r\r\n\s*", text)

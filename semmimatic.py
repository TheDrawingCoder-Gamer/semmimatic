import markovify
import portalocker
import typing
import re
from collections.abc import Coroutine, Callable, Awaitable

ping_regex=re.compile('<@(.+)>')
# i'm a sinner
class Semmimatic:
    def __init__(self, quote_path, newline=True, strip_room_pings=True):
        self.quote_path = quote_path
        self.newline = newline
        self.strip_room_pings = strip_room_pings
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
    def make_sentence(self, tries: int = 100, 
                      strip_room_pings: typing.Optional[bool] = None,
                      **kwargs):
        res = self.model.make_sentence(tries=tries, **kwargs)
        if strip_room_pings is None:
            strip_room_pings = self.strip_room_pings
        if strip_room_pings:
            res = res.replace("@everyone", "PING everyone")
            res = res.replace("@here", "PING here")
        return res 
    async def make_sentence_full(self, replace_ping: Callable[[int], typing.Union[Awaitable[str], str]], **kwargs) -> str:
        res = self.make_sentence(**kwargs)
        number = ping_regex.search(res)

        if number != None:
            for group in number.groups():
                user_id = int(group)
                out = replace_ping(user_id)
                if isinstance(out, Awaitable):
                    out = await out
                res = res.replace(f"<@{group}>", f"{out}")
        return res
        
class ModelText(markovify.Text):
    def sentence_split(self, text):
        return re.split(r"\s*\n\n\n\n\s*", text)

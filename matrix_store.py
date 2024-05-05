from peewee import *


class RoomExtras(Model):
    room_id = TextField()
    ping = BooleanField(default = False)

    class Meta:
        constraints = [SQL("UNIQUE(room_id)")]

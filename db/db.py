from peewee import *

db = SqliteDatabase('integrity.db')


class MessageInfo(Model):
    h_m = BlobField()
    signature = BlobField()
    scheme = CharField()
    hash_function = CharField()
    n = IntegerField()

    class Meta:
        database = db


class BlockHashes(Model):
    h_m = BlobField()
    index = IntegerField()
    block_hash = BlobField()

    class Meta:
        database = db


def create_tables():
    db.connect()
    db.create_tables([MessageInfo, BlockHashes])
    db.close()

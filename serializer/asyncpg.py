import asyncpg

def serialize_asyncpg_record(record: asyncpg.Record) -> dict:
    return dict(record)
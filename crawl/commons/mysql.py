from sqlalchemy import create_engine, inspect
from config import mysql

def mysqlEngine():
    return create_engine(f"{mysql['sql']}://{mysql['user']}':{mysql['passwd']}'@{mysql['host']}'/{mysql['db']}")

def loadDataType(engine, schema, table):
    insp = inspect(engine)
    columns = insp.get_columns(table, schema)
    dtypes = {}
    for col in columns:
        dtypes[col['name']] = col['type']
    return dtypes
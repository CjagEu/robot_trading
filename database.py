import sqlalchemy
import pandas as pd
from herramientas import *


"""def crear_engine(nombre):
    engine = sqlalchemy.create_engine('sqlite:///' + nombre)
    return engine"""


# Crear DB general
robot_database = sqlalchemy.create_engine('sqlite:///' + 'robot_databse')


# Crear tabla para mis trades historicos
# df = obtener_mis_trades_historico_df()
# df.to_sql('HISTORICO_TRADES', robot_database)

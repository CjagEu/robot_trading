from robot_config.config import api_key, secret_key
from binance.client import Client
import pandas as pd


def get_velas(symbol, intervalo, tiempo_atras):
    df = pd.DataFrame(client.get_historical_klines(symbol, intervalo, tiempo_atras + ' ago UTC'))  # Velas diarias del año pasado
    df = df.iloc[:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='ms')
    df = df.astype(float)
    return df


def mostrarTradesEjecutados(lista_entrada, lista_salida, lista_beneficio):
    for i in range(0, len(lista_entrada)):
        print('Dia ' + str(i) + ' ' + str(lista_entrada[i]) + ' entró')
        print('Dia ' + str(i) + ' ' + str(lista_salida[i]) + ' salió       Profit: ' + str(lista_beneficio[i]) + '\n')


def getTablaTrades(lista_entrada, lista_salida, lista_beneficio):

    dft = pd.DataFrame()
    dft['Compra'] = pd.Series(lista_entrada)
    dft['Venta'] = pd.Series(lista_salida)
    dft['Beneficio'] = pd.Series(lista_beneficio)
    
    print(dft)


def mostrarResultados(n_compras, n_ventas, n_veces_no_entro, n_veces_no_salio, n_total, lista_beneficios):
    print('**************************************************************************')
    print('Numero compras: ' + str(n_compras))
    print('Numero ventas: ' + str(n_ventas))
    print('Numero de veces que no entró: ' + str(n_veces_no_entro))
    print('Numero de veces que no salió: ' + str(n_veces_no_salio))
    print('Total velas: ' + str(n_veces_no_salio+n_veces_no_entro+n_compras+1)) # para comprobar que se procesaron todas las velas (el +1 es por la primera fila que son los labels)
    print('nTOTAL: ' + str(n_total))
    print('USDT de BENEFICIO (total sin contar las comisiones): ' + str(sum(lista_beneficios)))
    print('**************************************************************************')


def mostrarBalanceResultados(balance_resultados, lista_intervalos):
    for i in range(len(balance_resultados)):
        print('Profit  ('+lista_intervalos[i]+') :   ' + '{:.2f}'.format(balance_resultados[i]))
    

def algoritmo_trading(df, balance_resultados):

    qUSDT = 100  
    n_compras = 0
    n_ventas = 0
    n_veces_no_entro = 0
    n_veces_no_salio = 0
    n_total = 0
    lista_beneficios = []
    lista_fechas_entrada = []
    lista_fechas_salida = []
    q_entrada = 0
    precio_entrada = 0
    open_position = False

    for i in range(0, len(df)):
        if not open_position:
            if df.iloc[i].FastSMA > df.iloc[i].SlowSMA:
                n_compras += 1
                n_total += 1
                # print('ENTRÓ UNA ORDEN DE COMPRA')
                q_entrada = qUSDT / df.iloc[i].Close
                precio_entrada = df.iloc[i].Close
                lista_fechas_entrada.append(df.index[i])
                open_position = True
            else:
                # print('NO ENTRÓ PORQUE LA CONDICIÓN NO SE CUMPLE')
                n_veces_no_entro += 1
                n_total += 1
        else:
            # print('NO SALIÓ PORQUE LA CONDICIÓN NO SE CUMPLE')
            n_veces_no_salio += 1
            n_total += 1
            if df.iloc[i].SlowSMA > df.iloc[i].FastSMA:
                n_ventas += 1
                n_total += 1
                # print('ENTRÓ UNA ORDEN DE VENTA')
                lista_beneficios.append((df.iloc[i].Close * q_entrada) - qUSDT)
                lista_fechas_salida.append(df.index[i])
                open_position = False
    
    balance_resultados.append(sum(lista_beneficios))
    mostrarResultados(n_compras, n_ventas, n_veces_no_entro, n_veces_no_salio, n_total, lista_beneficios)
    getTablaTrades(lista_fechas_entrada, lista_fechas_salida, lista_beneficios)


def backtesting(symbol, tiempo_atras):

    lista_intervalos = ['1d', '4h', '1h', '30m', '15m', '5m']
    balance_resultados = []

    for intervalo in lista_intervalos:
        print(str(symbol) + '   ' + intervalo)
        df = get_velas(symbol, intervalo, tiempo_atras) 
        df['FastSMA'] = df.Close.rolling(7).mean()
        df['SlowSMA'] = df.Close.rolling(25).mean()
        df = df.dropna()
        df.to_csv('tablas_backtesting_csv/velas'+intervalo+'.csv')
        algoritmo_trading(df, balance_resultados)
    
    mostrarBalanceResultados(balance_resultados, lista_intervalos)

    # intervaloAPreguntar = input('Ver trades de intervalo: (0 para ninguno)').lower()
    # if intervaloAPreguntar != 0:
    #   mostrarTradesDFT(dft)


client = Client(api_key, secret_key)

# Pedir solo un intervalo
# symbol = input('Moneda: ').upper()
# intervalo = input('Intervalo de tiempo: ')
# df = getVelasUltimoAnio(symbol, intervalo)
# faltan mas cosas

# Dar todos los intervalos
moneda = input('Moneda: ').upper()
tiempo = input('Desde cuando [x week, x month, x year]: ')
backtesting(moneda, tiempo)


"""
if not open_position:
    if lastrow.FastSMA > lastrow.SlowSMA:
        #order_buy
        print("algo")
        open_position = True
    else:
        print('no hemos entrado pero condicion no se cumple')
else:
    print('ya en posicion')
    if lastrow.SlowSMA > lastrow.FastSMA:
        #order_sell
        print('algo')
        open_position = False
"""
from robot_config.config import api_key, secret_key
from binance.client import Client
import pandas as pd
import ta


def aplicar_indicadores(df):
    #df['%K'] = ta.momentum.stoch(df.High, df.Low, df.Close, window=14, smooth_window=3)
    #df['%D'] = df['%K'].rolling(3).mean()
    #df['RSI'] = ta.momentum.rsi(df.Close, window=14)
    #df['MACD'] = ta.trend.macd_diff(df.Close)
    df['EMA18'] = ta.trend.ema_indicator(df.Close, window=18)
    df['EMA28'] = ta.trend.ema_indicator(df.Close, window=28)
    df['WMA5'] = ta.trend.wma_indicator(df.Close, window=5)
    df['WMA12'] = ta.trend.wma_indicator(df.Close, window=12)
    df['RSI'] = ta.momentum.rsi(df.Close, window=21)
    df.dropna(inplace=True)
    return df


def condicion_entrada(ema18, ema28, wma5, wma12, rsi):
    # WMA5 y WMA12 cruzan el túnel rojo hacia arriba
    media_tunel_rojo = (ema18+ema28)/2
    condicion_1 = (wma5 > media_tunel_rojo) & (wma12 > media_tunel_rojo)
    # WMA5 cruza hacia arriba a WMA12 (señal fuerte)
    condicion_2 = wma5 >= wma12
    # RSI(21) debe ser mayor que 50 (señal de confirmación)
    condicion_3 = rsi > 50
    return condicion_1 & condicion_2 & condicion_3


def condicion_salida(ema18, ema28, wma5, wma12, rsi):
    # WMA5 y WMA12 cruzan el túnel rojo hacia abajo
    media_tunel_rojo = (ema18 + ema28) / 2
    condicion_1 = (wma5 < media_tunel_rojo) & (wma12 < media_tunel_rojo)
    # WMA5 cruza hacia abajo a WMA12 (señal fuerte)
    condicion_2 = wma5 <= wma12
    # RSI(21) debe ser menor que 50 (señal de confirmación)
    condicion_3 = rsi < 50
    return condicion_1 & condicion_2 & condicion_3

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


def mostrarBalanceResultados(balance_resultados, lista_intervalos):
    for i in range(len(balance_resultados)):
        print('Profit  ('+lista_intervalos[i]+') :   ' + '{:.2f}'.format(balance_resultados[i]))
    

def algoritmo_trading(df, balance_resultados):

    qUSDT = 100
    lista_beneficios = []
    lista_fechas_entrada = []
    lista_fechas_salida = []
    q_entrada = 0
    precio_entrada = 0
    open_position = False

    for i in range(0, len(df)):
        if not open_position:
            if condicion_entrada(ema18=df.EMA18[i], ema28=df.EMA28[i], wma5=df.WMA5[i], wma12=df.WMA12[i], rsi=df.RSI[i]):
                # print('ENTRÓ UNA ORDEN DE COMPRA')
                q_entrada = qUSDT / df.iloc[i].Close
                precio_entrada = df.iloc[i].Close
                lista_fechas_entrada.append(df.index[i])
                open_position = True
            """else:
                print('NO ENTRÓ PORQUE LA CONDICIÓN NO SE CUMPLE')"""
        else:
            # print('NO SALIÓ PORQUE LA CONDICIÓN NO SE CUMPLE')
            if condicion_salida(ema18=df.EMA18[i], ema28=df.EMA28[i],wma5= df.WMA5[i],wma12=df.WMA12[i], rsi=df.RSI[i]):
                # print('ENTRÓ UNA ORDEN DE VENTA')
                lista_beneficios.append((df.iloc[i].Close * q_entrada) - qUSDT)
                lista_fechas_salida.append(df.index[i])
                open_position = False
    
    balance_resultados.append(sum(lista_beneficios))
    print('**************************************************************************')
    print('USDT de BENEFICIO (total sin contar las comisiones): ' + str(sum(lista_beneficios)))
    print('**************************************************************************')
    getTablaTrades(lista_fechas_entrada, lista_fechas_salida, lista_beneficios)


def backtesting(symbol, tiempo_atras):

    lista_intervalos = ['1d', '4h', '1h', '30m', '15m', '5m']
    balance_resultados = []

    for intervalo in lista_intervalos:
        print(str(symbol) + '   ' + intervalo)
        df = get_velas(symbol, intervalo, tiempo_atras)
        aplicar_indicadores(df)
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

from robot_config.config import api_key, secret_key
from binance.client import Client
from binance.exceptions import BinanceAPIException
from time import strftime, localtime, sleep
from bs4 import BeautifulSoup
import pandas as pd
import requests




# Conexión con Binance API
client = Client(api_key, secret_key)
# -------------------------------------------------------------------------------------------------------------------
def obtener_velas_df(symbol):
    """
        Obtiene datos sobre una moneda proveniente del exchange (valores OHLCV)

        :param symbol: requerido
        :type symbol: str

        :returns: pd.DataFrame

        :eleva: BinanceAPIException
    """
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m', '60m UTC'))
    except BinanceAPIException as e:
        print(e)
        sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m', '60m UTC'))
    df = df.iloc[:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index+3600000, unit='ms')
    df = df.astype(float)
    return df


def obtener_ordenes_abiertas_df():
    """
        Obtiene un dataframe con los datos de mis ordenes abiertas

        Si no tengo ordenes abiertas devuelve una lista vacía

        Si tengo ordenes abiertas devuelve un dataframe

        :returns: list
        :returns: pd.DataFrame
    """
    lista_monedas = obtener_mis_monedas_lista()
    if lista_monedas == []:
        return pd.DataFrame()           # Devuelvo lista vacía
    lista_ordenes_todas = pd.DataFrame(columns=['Symbol', 'Precio', 'qCripto', 'Side'])
    for moneda in lista_monedas:
        if moneda != 'USDT':
            orders = client.get_open_orders(symbol=moneda+'USDT')       # Constante USDT
            if orders == []:
                return []          # Devuelvo lista vacía
            ordenes_abiertas = pd.DataFrame(orders)
            ordenes_abiertas = ordenes_abiertas.iloc[:, [0, 4, 5, 11]]
            ordenes_abiertas.columns = ['Symbol', 'Precio', 'qCripto', 'Side']
            lista_ordenes_todas = pd.concat([lista_ordenes_todas, ordenes_abiertas])
    
    return lista_ordenes_todas


def obtener_mis_trades_monedas_billetera_df():
    """
    Obtiene un dataframe con los datos de mis trades completados de las monedas que tengo actualmente en la billetera
            Si no tengo trades completados devuelve un DataFrame vacío
            Si tengo trades completados devuelve un DataFrame con los datos

            En columnas 'Buy' y 'Sell'

            Buy=True AND Sell=True es orden de compra

            Sell=False AND Sell=False es orden de venta


        :returns: pd.DataFrame
    """
    lista_monedas = obtener_mis_monedas_lista()
    lista_trades_todos = pd.DataFrame(
        columns=['Symbol', 'Precio', 'qCripto', 'qUSDT', 'Comision', 'MonedaComision', 'Hora', 'Buy', 'Sell'])
    lista_trades_todos = lista_trades_todos.set_index('Hora')
    for moneda in lista_monedas:
        try:
            lista_trades = client.get_my_trades(symbol=moneda + 'USDT')
            if lista_trades:  # Distinto de []
                trades = pd.DataFrame(lista_trades)
                trades = trades.iloc[:, [0, 4, 5, 6, 7, 8, 9, 10, 11]]
                trades.columns = ['Symbol', 'Precio', 'qCripto', 'qUSDT', 'Comision', 'MonedaComision', 'Hora', 'Buy',
                                  'Sell']
                trades = trades.set_index('Hora')
                trades.index = pd.to_datetime(trades.index, unit='ms')
                lista_trades_todos = pd.concat([lista_trades_todos, trades])
        except BinanceAPIException:
            continue
    lista_trades_todos.sort_values(by='Hora', inplace=True)
    return lista_trades_todos


def obtener_mis_trades_historico_df():
    """
        Obtiene un dataframe con los datos de mis trades completados desde la creación de la cuenta

        Si no tengo trades completados devuelve un DataFrame vacío

        Si tengo trades completados devuelve un DataFrame con los datos

        En columnas 'Buy' y 'Sell'

        Buy=True AND Sell=True es orden de compra

        Sell=False AND Sell=False es orden de venta

        :returns: pd.DataFrame
    """
    lista_monedas = obtener_monedas_binance_lista()
    lista_trades_todos = pd.DataFrame(columns=['Symbol', 'Precio', 'qCripto', 'qUSDT', 'Comision', 'MonedaComision', 'Hora', 'Buy', 'Sell'])
    lista_trades_todos = lista_trades_todos.set_index('Hora')
    for moneda in lista_monedas:
        try:
            lista_trades = client.get_my_trades(symbol=moneda+'USDT')
            if lista_trades:        # Distinto de []
                trades = pd.DataFrame(lista_trades)
                trades = trades.iloc[:, [0, 4, 5, 6, 7, 8, 9, 10, 11]]
                trades.columns = ['Symbol', 'Precio', 'qCripto', 'qUSDT', 'Comision', 'MonedaComision', 'Hora', 'Buy', 'Sell']
                trades = trades.set_index('Hora')
                trades.index = pd.to_datetime(trades.index, unit='ms')
                lista_trades_todos = pd.concat([lista_trades_todos, trades])
        except BinanceAPIException:
            continue
    lista_trades_todos.sort_values(by='Hora', inplace=True)
    return lista_trades_todos


def obtener_mis_monedas_lista():
    """
        Obtiene una lista con las monedas que tengo actualmente en la billetera

        Se guarda el 'symbol'

        La cantidad que tengo libre

        La cantidad ocupada

        :returns: list
    """
    mis_monedas = pd.DataFrame(client.get_account().get('balances'))
    mis_monedas.columns = ['Asset', 'Libre', 'Posicionado']
    lista_mis_monedas = []
    for i in range(len(mis_monedas)):
        if float(mis_monedas.Libre[i]) != 0 or float(mis_monedas.Posicionado[i]) != 0:
            lista_mis_monedas.append(mis_monedas.Asset[i])
    return lista_mis_monedas


def obtener_monedas_binance_lista():
    """
        Obtiene una lista con las monedas que he tenido en algún momento

        (está comentado el código para obtener todas las monedas de binance, tarda mucho en ejecutar)

        Se guarda el 'symbol'

        :returns: list
    """
    # monedas = pd.DataFrame(client.get_account().get('balances'))
    # monedas.columns = ['Asset', 'Libre', 'Posicionado']
    # return monedas['Asset'].tolist()
    info = pd.DataFrame(client.get_account_snapshot(type='SPOT'))
    info = info['snapshotVos'].iloc[-1]
    info = pd.DataFrame(info['data'])
    info = pd.DataFrame(info)

    lista = []
    for fila in range(len(info)):
        lista.append((info['balances'].iloc[fila])['asset'])
    return lista


def obtener_qty_cripto(cantidad_USDT, precio):
    """
        Obtiene la cantidad de moneda comprada con USDT

        :param cantidad_USDT: requerido
        :type cantidad_USDT: float
        :param precio: requerido
        :type precio: float

        :returns: float
    """
    return float(round(cantidad_USDT / precio, 8))


def obtener_porcentaje_ganancia(numero):
    """
        Obtiene el porcentaje de ganancia 'transformado' para poder usarlo matemáticamente

        número es el porcentaje en lenguaje natural, de esta manera:

        numero = 100 --> 2      (100% ganancia)

        numero = 1   --> 1.01   (  1% ganancia)

        numero = 0.2 --> 1.002  (0.2% ganancia)

        numero > 0.1 como mínimo para superar la comisión

        :param numero: requerido
        :type numero: float

        :returns: float
    """
    if numero <= 0.1:
        raise ValueError('Porcentaje debe ser un float positivo')
    return numero/100 + 1


def consultar_ultima_posicion(symbol):
    """
        Consulta mi último trade completado y devuelve un booleano

        True  = Si fue Buy

        False = Si fue Sell

        :param symbol: requerido
        :type symbol: str

        :returns: bool
    """
    lista_trades = client.get_my_trades(symbol=symbol)
    trades = pd.DataFrame(lista_trades)
    trades = trades.iloc[:, [0, 4, 5, 6, 7, 8, 9, 10, 11]]
    trades.columns = ['Symbol', 'Precio', 'qCripto', 'qUSDT', 'Comision', 'MonedaComision', 'Hora', 'Buy', 'Sell']
    trades = trades.set_index('Hora')
    trades.index = pd.to_datetime(trades.index, unit='ms')
    if trades.Buy[-1] or (trades.Buy[-1] and trades.Sell[-1]):
        return True     # Buy   
    return False        # Sell  


def consultar_ordenes_abiertas(lista_monedas):
    """
        Consulta si tengo órdenes abiertas de alguna moneda en mi portafolio y devuelve un booleano

        True  = Si tengo

        False = No tengo

        :param lista_monedas: requerido

        :returns: bool
    """
    for moneda in lista_monedas:
        if moneda != 'USDT':
            orders = client.get_open_orders(symbol=moneda+'USDT')   # Cuidado constante USDT, no existe el par USDTUSDT
            if len(orders) > 0:
                return True
    return False


def mostrar_info_salida_mercado(symbol, ultimo_precio, buyprice, porcentaje_ganancia, qty, comision):
    """
        Muestra por pantalla información
    """
    print('Esperando para salir...  '  + '(' + symbol + ')   ' +
        'Precio Actual: '  + '{:.8f}'.format(ultimo_precio) + '  ' +
        'Precio esperado : ' + '{:.8f}'.format(buyprice * porcentaje_ganancia) + '   ' +
        'Compré a: ' + '{:.8f}'.format(buyprice) + '   ' +
        'Ganancia en USDT : [' + '{:.8f}'.format((((qty/buyprice) * ultimo_precio) - qty) - comision) + '] ' +
        '(' + calcular_margen(ultimo_precio, buyprice+comision) + ')  ' +
        'Comision(usdt): ' + str(comision) + '   ' +
        strftime("%H:%M:%S", localtime())
          )


def mostrar_info_entrada_mercado(symbol, ultimo_precio, penultimo_precio):
    """
        Muestra por pantalla información
    """
    print('Esperando para entrar... ' + '(' + symbol + ')   ' +
        'Precio Actual: '  + '{:.8f}'.format(ultimo_precio) + '  ' +
        'Cierre última vela: ' + '{:.8f}'.format(penultimo_precio) + '     ' +
         strftime("%H:%M:%S", localtime())
          )


def calcular_margen(precio_actual, buyprice):
    """
        Calcula el margen que existe entre precioActual y buyPrice.

        Es el % de ganancia o pérdida

        :param precio_actual: requerido
        :type precio_actual: float
        :param buyprice: requerido
        :type buyprice: float

        :returns: str
    """
    # Redondeo a 3 decimales
    margen = round(100 * ((precio_actual / buyprice) - 1), 3)
    if margen > 0:
        return '+' + str(margen) + '%'
    return str(margen) + '%'


def introducir_parametros():
    """
       Pide por pantalla los parámetros necesarios para la estrategia de trading

        :returns: str, float, float, bool
    """
    criptomoneda = input('MONEDA: ').upper()
    qUSDT = float(input('qUSDT: '))
    porcentaje_ganancia = float(input(" '%' Ganancia por Trade (número mayor que 0.1): "))
    symbol = criptomoneda+'USDT'
    open_position = consultar_ultima_posicion(symbol)       # True = Ultima vez compré
    return symbol, qUSDT, obtener_porcentaje_ganancia(porcentaje_ganancia), open_position



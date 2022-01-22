import sys
sys.path.append('../')
from robot_config.claves import api_key,api_secret
from binance.client import Client
from binance.exceptions import BinanceAPIException
from time import strftime, localtime, sleep
import pandas as pd


#Conexión con Binance API
client = Client(api_key,api_secret)
#-------------------------------------------------------------------------------------------------------------------
"""
    Obtiene datos sobre una moneda proveniente del exchange (valores OHLCV)

    :param symbol: requerido
    :type symbol: str

    :returns: pd.DataFrame

    :eleva: BinanceAPIException
"""
def obtener_velas(symbol):
    try:
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m','40m UTC'))
    except BinanceAPIException as e:
        print(e)
        sleep(60)
        df = pd.DataFrame(client.get_historical_klines(symbol, '1m','40m UTC'))
    df = df.iloc[:,:6]
    df.columns = ['Time','Open','High','Low','Close','Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index+3600000, unit='ms')
    df = df.astype(float)
    return df


"""
    Obtiene un dataframe con los datos de mis ordenes abiertas
        Si no tengo ordenes abiertas devuelve una lista vacía
        Si tengo ordenes abiertas devuelve un dataframe

    :returns: list
    :returns: pd.DataFrame
"""
def obtener_ordenes_abiertas_df():
    lista_monedas = obtener_mis_monedas_lista()
    if lista_monedas == []:
        return pd.DataFrame()           # Devuelvo dataframe vacío, para devolver un dataframe en cualquier caso
    lista_ordenes_todas = pd.DataFrame(columns = ['Symbol', 'Precio', 'qCripto','Side'])
    for moneda in lista_monedas:
        if moneda != 'USDT':
            orders = client.get_open_orders(symbol=moneda+'USDT')       #Constante USDT
            if orders == []:
                return []          # Devuelvo lista vacía
            ordenes_abiertas = pd.DataFrame(orders)
            ordenes_abiertas = ordenes_abiertas.iloc[:,[0,4,5,11]]
            ordenes_abiertas.columns = ['Symbol', 'Precio', 'qCripto','Side']
            lista_ordenes_todas = pd.concat([lista_ordenes_todas, ordenes_abiertas])
    
    return lista_ordenes_todas


"""
    Obtiene un dataframe con los datos de mis trades completados
        Si no tengo trades completados devuelve un DataFrame vacío
        Si tengo trades completados devuelve un DataFrame con los datos
        
        En columnas 'Buy' y 'Sell'
            Buy=True AND Sell=True es orden de compra
            Sell=False AND Sell=False es orden de venta

    :returns: pd.DataFrame
"""
def obtener_mis_trades_df():
    lista_monedas = obtener_mis_monedas_lista()
    if lista_monedas == []:
        return pd.DataFrame()           # Devuelvo dataframe vacío, para devolver un dataframe en cualquier caso
    lista_trades_todos = pd.DataFrame(columns = ['Symbol', 'Precio', 'qCripto','qUSDT','Comision','MonedaComision','Hora','Buy','Sell'])
    lista_trades_todos = lista_trades_todos.set_index('Hora')
    print(lista_trades_todos)
    for moneda in lista_monedas:
        if moneda != 'USDT':
            lista_trades = client.get_my_trades(symbol=moneda+'USDT')
            trades = pd.DataFrame(lista_trades)
            trades = trades.iloc[:,[0,4,5,6,7,8,9,10,11]]
            trades.columns = ['Symbol', 'Precio', 'qCripto','qUSDT','Comision','MonedaComision','Hora','Buy','Sell']
            trades = trades.set_index('Hora')
            trades.index = pd.to_datetime(trades.index+3600000, unit='ms')
            lista_trades_todos = pd.concat([lista_trades_todos, trades])
    lista_trades_todos.sort_values(by = 'Hora', inplace=True)
    return lista_trades_todos


"""
    Obtiene una lista con las monedas que tengo 
        Se guarda el 'symbol'
        La cantidad que tengo libre
        La cantidad ocupada
        
    :returns: list
"""
def obtener_mis_monedas_lista():
    mis_monedas = pd.DataFrame(client.get_account().get('balances'))
    mis_monedas.columns = ['Asset', 'Libre', 'Posicionado']
    lista_mis_monedas = []
    for i in range(0,len(mis_monedas)):
        if float(mis_monedas.Libre[i]) != 0 or float(mis_monedas.Posicionado[i]) != 0:
            lista_mis_monedas.append(mis_monedas.Asset[i])
    return lista_mis_monedas


"""
    Obtiene la cantidad de moneda comprada con USDT
    
    :param cantidad_USDT: requerido
    :type cantidad_USDT: float
    :param precio: requerido
    :type precio: float

    :returns: float
"""
def obtener_qty_cripto(cantidad_USDT, precio):
    # Limite
    return float(round(cantidad_USDT / precio, 8))


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
def obtener_porcentaje_ganancia(numero):
    if numero <= 0.1:
        raise ValueError('Porcentaje debe ser un float positivo')
    return (numero)/100 + 1


"""
    Consulta mi último trade completado y devuelve un booleano
        True  = Si fue Buy
        False = Si fue Sell
        
    :param symbol: requerido
    :type symbol: str

    :returns: bool
"""
def consultar_ultima_posicion(symbol):
    lista_trades = client.get_my_trades(symbol=symbol)
    trades = pd.DataFrame(lista_trades)
    trades = trades.iloc[:,[0,4,5,6,7,8,9,10,11]]
    trades.columns = ['Symbol', 'Precio', 'qCripto','qUSDT','Comision','MonedaComision','Hora','Buy','Sell']
    trades = trades.set_index('Hora')
    trades.index = pd.to_datetime(trades.index+3600000, unit='ms')
    if trades.Buy[-1] or (trades.Buy[-1] and trades.Sell[-1]):
        return True     # Buy   
    return False        # Sell  


"""
    Consulta si tengo órdenes abiertas de alguna moneda en mi portafolio y devuelve un booleano
        True  = Si tengo
        False = No tengo
        
    :param lista_monedas: requerido
    :type symbol: list

    :returns: bool
"""
def consultar_ordenes_abiertas(lista_monedas):
    for moneda in lista_monedas:
        if moneda != 'USDT':
            orders = client.get_open_orders(symbol=moneda+'USDT')   # Cuidado constante USDT, no existe el par USDTUSDT
            if(len(orders) > 0):
                return True
    return False


"""
    Muestra por pantalla información 
"""
def mostrar_info_salida_mercado(symbol, ultimo_precio, buyprice, porcentaje_ganancia, qty, comision):
            print('Esperando para salir...  '  + '(' + symbol + ')   ' + 
            'Precio Actual: '  + '{:.8f}'.format(ultimo_precio) + '  ' +
            'Precio esperado : ' + '{:.8f}'.format(buyprice * porcentaje_ganancia) + '   ' + 
            'Compré a: ' + '{:.8f}'.format(buyprice) + '   ' +
            'Ganancia en USDT : [' + '{:.8f}'.format((((qty/buyprice) * ultimo_precio) - qty) - comision) + '] ' + 
            '(' + calcular_margen(ultimo_precio, buyprice+comision) + ')  ' +
            'Comision(usdt): ' + str(comision) + '   ' + 
            strftime("%H:%M:%S", localtime())
            )  


"""
    Muestra por pantalla información 
"""
def mostrar_info_entrada_mercado(symbol, ultimo_precio, penultimo_precio):
        print('Esperando para entrar... ' + '(' + symbol + ')   ' +
         'Precio Actual: '  + '{:.8f}'.format(ultimo_precio) + '  ' + 
         'Cierre última vela: ' + '{:.8f}'.format(penultimo_precio) + '     ' +
         strftime("%H:%M:%S", localtime()) 
         )


"""
    Calcula el margen que existe entre precioActual y buyPrice
    Es el % de ganancia o pérdida 

    :param precio_actual: requerido
    :type precio_actual: float
    :param buyprice: requerido
    :type buyprice: float

    :returns: str
"""
def calcular_margen(precio_actual, buyprice):
    # Redondeo a 3 decimales
    margen = round(100 * ((precio_actual / buyprice) - 1), 3)
    if margen > 0:
        return '+' + str(margen) + '%'
    return str(margen) + '%'


"""
   Pide por pantalla los parámetros necesarios para la estrategia de trading

    :returns: str, float, float, bool
"""
def introducir_parametros():
    criptomoneda = input('MONEDA: ').upper()
    qUSDT = float(input('qUSDT: '))
    porcentaje_ganancia = float(input(" '%' Ganancia por Trade (número mayor que 0.1): "))
    symbol = criptomoneda+'USDT'
    open_position = consultar_ultima_posicion(symbol)       #True = Ultima vez compré
    return symbol, qUSDT, obtener_porcentaje_ganancia(porcentaje_ganancia), open_position

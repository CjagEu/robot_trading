from robot_config.config import api_key
from binance.client import Client
from time import strftime, localtime, sleep
import pandas as pd


def get_velas(symbol, intervalo, tiempo_atras):
    df = pd.DataFrame(client.get_historical_klines(symbol, intervalo,tiempo_atras + ' ago UTC'))  # Velas diarias del año pasado
    df = df.iloc[:,:6]
    df.columns = ['Time','Open','High','Low','Close','Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index+3600000, unit='ms')
    df = df.astype(float)
    return df



def mostrarTradesEjecutados(listaEntrada, listaSalida, listaBeneficio):
    for i in range(0, len(listaEntrada)):
        print('Dia ' + str(i) + ' ' + str(listaEntrada[i]) + ' entró')
        print('Dia ' + str(i) + ' ' + str(listaSalida[i]) + ' salió       Profit: ' + str(listaBeneficio[i]) + '\n')


def getTablaTrades(listaEntrada, listaSalida, listaBeneficio):

    dft = pd.DataFrame()
    dft['Compra'] = pd.Series(listaEntrada)
    dft['Venta'] = pd.Series(listaSalida)
    dft ['Beneficio'] = pd.Series(listaBeneficio)
    
    print(dft)

def mostrarResultados(nCompras, nVentas, nVecesNoEntro, nVecesNoSalio, nTOTAL, listaBeneficios):
    print('**************************************************************************')
    print('Numero compras: ' + str(nCompras))
    print('Numero ventas: ' + str(nVentas))
    print('Numero de veces que no entró: ' + str(nVecesNoEntro))
    print('Numero de veces que no salió: ' + str(nVecesNoSalio))
    print('Total velas: ' + str(nVecesNoSalio+nVecesNoEntro+nCompras+1)) #para comprobar que se procesaron todas las velas (el +1 es por la primera fila que son los labels)
    print('nTOTAL: ' + str(nTOTAL))
    print('USDT de BENEFICIO (total sin contar las comisiones): ' + str(sum(listaBeneficios)))
    print('**************************************************************************')


def mostrarBalanceResultados(balanceResultados, lista_intervalos):
    for i in range(0,len(balanceResultados)):
        print('Profit  ('+lista_intervalos[i]+') :   ' + '{:.2f}'.format(balanceResultados[i]))
    

def algoritmo_trading(df, balanceResultados):

    qUSDT = 100  
    nCompras = 0
    nVentas = 0
    nVecesNoEntro = 0
    nVecesNoSalio = 0
    nTOTAL = 0
    listaBeneficios = []
    listaFechasEntrada = []
    listaFechasSalida = []
    qEntrada = 0
    precioEntrada = 0
    open_position = False

    for i in range(0, len(df)):
            if not open_position:
                if df.iloc[i].FastSMA > df.iloc[i].SlowSMA:
                    nCompras += 1
                    nTOTAL += 1
                    #print('ENTRÓ UNA ORDEN DE COMPRA')
                    qEntrada = qUSDT / df.iloc[i].Close
                    precioEntrada = df.iloc[i].Close
                    listaFechasEntrada.append(df.index[i])
                    open_position = True
                else:
                    #print('NO ENTRÓ PORQUE LA CONDICIÓN NO SE CUMPLE')
                    nVecesNoEntro += 1
                    nTOTAL += 1
            else:
                #print('NO SALIÓ PORQUE LA CONDICIÓN NO SE CUMPLE')
                nVecesNoSalio += 1
                nTOTAL += 1
                if df.iloc[i].SlowSMA > df.iloc[i].FastSMA:
                    nVentas += 1
                    nTOTAL += 1
                    #print('ENTRÓ UNA ORDEN DE VENTA')
                    listaBeneficios.append((df.iloc[i].Close * qEntrada) - qUSDT)
                    listaFechasSalida.append(df.index[i])
                    open_position = False
    
    balanceResultados.append(sum(listaBeneficios))
    mostrarResultados(nCompras, nVentas, nVecesNoEntro, nVecesNoSalio, nTOTAL, listaBeneficios)
    getTablaTrades(listaFechasEntrada, listaFechasSalida, listaBeneficios)


def backtesting(symbol, tiempo_atras):

    lista_intervalos = ['1d','4h','1h','30m','15m','5m']
    balanceResultados = []

    for intervalo in lista_intervalos:
        print(str(symbol) + '   ' + intervalo)
        df = get_velas(symbol, intervalo, tiempo_atras) 
        df['FastSMA'] = df.Close.rolling(7).mean()
        df['SlowSMA'] = df.Close.rolling(25).mean()
        df = df.dropna()
        df.to_csv('tablas_backtesting_csv/velas'+intervalo+'.csv')
        algoritmo_trading(df, balanceResultados)
    
    mostrarBalanceResultados(balanceResultados, lista_intervalos)

    #intervaloAPreguntar = input('Ver trades de intervalo: (0 para ninguno)').lower()
    #if intervaloAPreguntar != 0:
        #mostrarTradesDFT(dft)


client = Client(api_key, api_secret) 

# Pedir solo un intervalo
#symbol = input('Moneda: ').upper()
#intervalo = input('Intervalo de tiempo: ')
#df = getVelasUltimoAnio(symbol, intervalo)
#faltan mas cosas

# Dar todos los intervalos
symbol = input('Moneda: ').upper()
tiempo_atras = input('Desde cuando [x week, x month, x year]: ')
backtesting(symbol, tiempo_atras)



#TODO











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
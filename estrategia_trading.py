from herramientas import *
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

"""
    Ejecuta la estrategia de trading de '4 Sistemas de trading.pdf'

    :param symbol: requerido
    :type symbol: str
    :param qty: requerido
    :type qty: float
    :param porcentaje_ganancia: requerido
    :type porcentaje_ganancia: float
    :param open_position: requerido
    :type open_position: bool
"""
def estrategia_trading(symbol, qty, porcentaje_ganancia, open_position):
    print(symbol + '    ' + str(qty) + ' USDT    ' + str(porcentaje_ganancia) + '\n')
    while True:
        df = obtener_velas_df(symbol)
        aplicar_indicadores(df)
        #mostrar_info_entrada_mercado(symbol, df.Close[-1], df.Close[-2])
        if not open_position:
            print('Condicion_1 : ' + str(((df.WMA5[-1] > (df.EMA18[-1]+df.EMA28[-1])/2) & (df.WMA12[-1] > (df.EMA18[-1]+df.EMA28[-1])/2))) +
                  '     Condicion_2 : ' + str(df.WMA5[-1] >= df.WMA12[-1]) +
                  '     Condicion_3 : ' + str(df.RSI[-1] > 50))
            print('Condiciones ENTRADA cumplidas: ' + str(condicion_entrada(df.EMA18[-1], df.EMA28[-1], df.WMA5[-1], df.WMA12[-1], df.RSI[-1])))
            if condicion_entrada(df.EMA18[-1], df.EMA28[-1], df.WMA5[-1], df.WMA12[-1], df.RSI[-1]):
                cantidad_a_comprar = obtener_qty_cripto(qty, df.Close[-1])
                # order = client.create_order(symbol=symbol,side='BUY',type='MARKET',quantity=qty)
                # order = client.order_market_buy(symbol=symbol,quoteOrderQty=qty)
                # print('\n' + order + '\n')
                open_position = True
                # buyprice = float(order['fills'][0]['price'])
                # comision = float(order['fills'][2]['commission'])          #CREO QUE SERIA ASI
                buyprice = df.Close[-1]
                print('\nCompré ' + str(cantidad_a_comprar) + ' con ' + str(qty) + ' USDT a ' + '{:.8f}'.format(df.Close[-1]) + '\n')
                break
    if open_position:
        while True:
            if obtener_ordenes_abiertas_df() == []:     # Se puede simplificar, de momento veo mejor la expresión así
                df = obtener_velas_df(symbol)
                aplicar_indicadores(df)
                #mostrar_info_salida_mercado(symbol, df.Close[-1], buyprice, porcentaje_ganancia, qty, comision)
                print('Condicion_1 : ' + str(((df.WMA5[-1] < (df.EMA18[-1] + df.EMA28[-1]) / 2) & (df.WMA12[-1] < (df.EMA18[-1] + df.EMA28[-1]) / 2))) +
                      '     Condicion_2 : ' + str(df.WMA5[-1] <= df.WMA12[-1]) +
                      '     Condicion_3 : ' + str(df.RSI[-1] < 50))
                print('Condiciones SALIDA cumplidas: ' + str(condicion_salida(df.EMA18[-1], df.EMA28[-1], df.WMA5[-1], df.WMA12[-1], df.RSI[-1])))
                if condicion_salida(df.EMA18[-1], df.EMA28[-1], df.WMA5[-1], df.WMA12[-1], df.RSI[-1]):
                    # order = client.create_order(symbol=symbol,side='SELL',type='MARKET',quantity=qty)
                    # order = client.order_market_sell(symbol=symbol, quoteOrderQty=qty)
                    # print('\n' + order + '\n')
                    # sellprice = float(order['fills'][0]['price'])
                    # print(f'profit = {(sellprice - buyprice)/buyprice}' + '\n')           # Es del tio, lo puedo poner más bonito
                    open_position = False
                    print('\nVendí <cantidad_a_vender> a <sellprice>\n')
                    break
            else:
                open_position = False   # Si cierro posición manualmente (en la web)
                break

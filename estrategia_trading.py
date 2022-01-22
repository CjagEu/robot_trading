from herramientas import *
"""
    Ejecuta la estrategia de trading:
        Cuando la ultima vela sea alcista (sin contar la actual),  comprar
        Cuando el precio suba un :porcentajeGanancia de su precio, vender

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
        df = obtener_velas(symbol)
        mostrar_info_entrada_mercado(symbol, df.Close[-1], df.Close[-2])
        if not open_position:
            if df.Close[-3] - df.Close[-2] < 0:
                cantidad_a_comprar = obtener_qty_cripto(qty, df.Close[-1])
                #order = client.create_order(symbol=symbol,side='BUY',type='MARKET',quantity=qty)
                    #order = client.order_market_buy(symbol=symbol,quoteOrderQty=qty)
                    #print('\n' + order + '\n')
                open_position = True
                    #buyprice = float(order['fills'][0]['price'])       
                    #comision = float(order['fills'][2]['commission'])          #CREO QUE SERIA ASI
                buyprice = df.Close[-1]
                print('\nCompré ' + str(cantidad_a_comprar) + ' con ' + str(qty) + ' USDT a ' + '{:.8f}'.format(df.Close[-1]) + '\n')
                break
    if open_position:
        comision = (cantidad_a_comprar * 0.00075) * buyprice                 #Solo valido si la moneda es BNB, si no tengo que consultar el precioactual de BNB expresaente en teoria en real uso la linea 71
        while True:
            df = obtener_velas(symbol)
            mostrar_info_salida_mercado(symbol, df.Close[-1], buyprice, porcentaje_ganancia, qty, comision)
            if (df.Close[-1]) >= buyprice * porcentaje_ganancia:
                #order = client.create_order(symbol=symbol,side='SELL',type='MARKET',quantity=qty)
                    #order = client.order_market_sell(symbol=symbol, quoteOrderQty=qty)
                    #print('\n' + order + '\n')
                    #sellprice = float(order['fills'][0]['price'])
                    #print(f'profit = {(sellprice - buyprice)/buyprice}' + '\n')           #Es del tio, lo puedo poner más bonito
                open_position = False
                print('\nVendí <cantidad_a_vender> a <sellprice>\n')
                break
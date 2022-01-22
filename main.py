from herramientas import *
from estrategia_trading import estrategia_trading

#Iniciación manual de parámetros
        #criptoMoneda = 'BTCUSDT'
        #qty = 20.0
        #porcentajeGanancia = 2.00



#Pedir por pantalla parámetros
criptoMoneda, qty, porcentajeGanancia, open_position = introducir_parametros()

while True:
    if consultar_ordenes_abiertas(obtener_mis_monedas_lista()):
        print('¡CUIDADO! Hay ordenes abiertas, ejecución abortada')
        break
    estrategia_trading(criptoMoneda, qty, porcentajeGanancia, open_position)

#TODO MIRAR COMO FUNCIONA create_order en la doc oficial
#TODO MIRAR COMO FUNCIONA LA VARIABLE FILLS DE ORDER (EN PRINCIPIO CONFIAR EN QUE ESTA BIEN, YA QUE LA ORDEN ES DE MERCADO)
#TODO PENSAR QUÉ QUIERES QUE PASE CUANDO SE COMPLETE UN TRADE (COMPRA Y VENTA), QUE SIGA EJECUTANDOSE CON LOS MISMOS PARÁMETROS O ALOMEJOR QUE VUELVA A PEDIR LA CANTIDAD O ALGO...
    # qty * precioMoneda = qUSDT    que me cuesta
    # qUSDT / precioMoneda = qty    que deberia poner

"""
Cojo el coste en USDT de comprar la moneda              qUSDT          
divido esa cantidad por el precio actual del BNB        qBNBoperacion = [qUSDT / df.Close[-1] (de BNB)]
multiplico esa cantidad (que esta en BNB) * 0.00075     costeComisionEnBNB = qBNBoperacion * 0.00075                        obtenemos el coste en BNB de la comision
si queremos saber cuanto USDT cuesta esa comision       costeComisionEnUSDT = costeComisionEnBNB * df.Close[-1] (de BNB)


si en la orden tengo el campo commission, solo tendria que mostrarlo

Just remeber - “quantity” is used to describe base asset (left of the symbol) and “quoteOrderQty” for the quote(right) asset
If you want to buy BTC with 6637 USDT, specify quoteOrderQty=6637 instead
    para orden de compra uso qty (quoteOrderQty=qty)
    para orden de venta uso qty  (quoteOrderQty=qty)
"""

#fees = client.get_trade_fee(symbol='BNBBTC')       lo dejo aquí para usarlo en la comison alomejors

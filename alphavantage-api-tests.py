import requests
import json
import sys
from datetime import datetime, timedelta

# Verifica si pandas está instalado e informa al usuario
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    PANDAS_INSTALLED = True
except ImportError:
    PANDAS_INSTALLED = False
    print("AVISO: pandas y/o matplotlib no están instalados.")
    print("Para visualización y análisis de datos avanzados, instálalos con:")
    print("pip install pandas matplotlib")
    print("Continuando con funcionalidad básica...\n")

# Configura tu API key de Alpha Vantage aquí
ALPHA_VANTAGE_API_KEY = ""  # Reemplaza con tu API key real

# URL base de la API
base_url = "https://www.alphavantage.co/query"

def test_conexion_api():
    """Prueba básica para verificar que podemos conectarnos a la API"""
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': 'AAPL',
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'compact'
    }
    
    response = requests.get(base_url, params=params)
    status_code = response.status_code
    
    print(f"Estado de la conexión: {status_code}")
    
    if status_code == 200:
        data = response.json()
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return False
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            print("Alpha Vantage tiene límites de 5 llamadas por minuto y 500 por día en su plan gratuito.")
            return True
        else:
            print("Conexión exitosa a la API de Alpha Vantage")
            print("Metadatos recibidos:")
            for key, value in data.get('Meta Data', {}).items():
                print(f"  {key}: {value}")
            return True
    else:
        print(f"Error al conectar: {response.text}")
        return False

def obtener_datos_diarios(simbolo, tamano_salida='compact'):
    """
    Obtiene datos de series temporales diarias
    tamano_salida: 'compact' (últimos 100 datos) o 'full' (hasta 20 años de datos históricos)
    """
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': simbolo,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': tamano_salida
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
            
        time_series_data = data.get('Time Series (Daily)', {})
        
        if PANDAS_INSTALLED:
            # Convertir a DataFrame si pandas está disponible
            df = pd.DataFrame.from_dict(time_series_data, orient='index')
            df.columns = [col.split('. ')[1] for col in df.columns]  # Limpiar nombres de columnas
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)  # Convertir valores a float
            
            print(f"\nDatos diarios para {simbolo} (tamaño: {tamano_salida}):")
            print(f"Período: {df.index.min()} a {df.index.max()}")
            print(f"Total de registros: {len(df)}")
            print(df.head())
            
            # Visualizar precios de cierre
            if not df.empty and 'close' in df.columns:
                plt.figure(figsize=(10, 5))
                plt.plot(df.index, df['close'])
                plt.title(f'Precios de cierre para {simbolo}')
                plt.xlabel('Fecha')
                plt.ylabel('Precio ($)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f"{simbolo}_precios.png")
                print(f"Gráfico guardado como {simbolo}_precios.png")
            
            return df
        else:
            # Mostrar datos sin pandas
            fechas = list(time_series_data.keys())
            print(f"\nDatos diarios para {simbolo} (tamaño: {tamano_salida}):")
            print(f"Período: {fechas[-1]} a {fechas[0]}")
            print(f"Total de registros: {len(fechas)}")
            print("\nMuestra de los datos más recientes:")
            for i, fecha in enumerate(fechas[:3]):
                print(f"Fecha: {fecha}")
                print(json.dumps(time_series_data[fecha], indent=2))
                if i < 2:  # Separador entre fechas
                    print("-" * 40)
            
            return time_series_data
    else:
        print(f"Error al obtener datos diarios: {response.text}")
        return None

def obtener_datos_intradiarios(simbolo, intervalo='5min', tamano_salida='compact'):
    """
    Obtiene datos de series temporales intradiarias
    intervalo: '1min', '5min', '15min', '30min', '60min'
    tamano_salida: 'compact' (últimos 100 datos) o 'full' (datos completos)
    """
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': simbolo,
        'interval': intervalo,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': tamano_salida
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
            
        time_series_key = f'Time Series ({intervalo})'
        time_series_data = data.get(time_series_key, {})
        
        if PANDAS_INSTALLED:
            # Convertir a DataFrame si pandas está disponible
            df = pd.DataFrame.from_dict(time_series_data, orient='index')
            df.columns = [col.split('. ')[1] for col in df.columns]  # Limpiar nombres de columnas
            df.index = pd.to_datetime(df.index)
            df = df.astype(float)  # Convertir valores a float
            
            print(f"\nDatos intradiarios para {simbolo} (intervalo: {intervalo}):")
            print(f"Período: {df.index.min()} a {df.index.max()}")
            print(f"Total de registros: {len(df)}")
            print(df.head())
            
            return df
        else:
            # Mostrar datos sin pandas
            fechas = list(time_series_data.keys())
            if not fechas:
                print(f"No se encontraron datos intradiarios para {simbolo} con intervalo {intervalo}")
                return None
                
            print(f"\nDatos intradiarios para {simbolo} (intervalo: {intervalo}):")
            print(f"Período: {fechas[-1]} a {fechas[0]}")
            print(f"Total de registros: {len(fechas)}")
            print("\nMuestra de los datos más recientes:")
            for i, fecha in enumerate(fechas[:3]):
                print(f"Fecha y hora: {fecha}")
                print(json.dumps(time_series_data[fecha], indent=2))
                if i < 2:  # Separador entre fechas
                    print("-" * 40)
            
            return time_series_data
    else:
        print(f"Error al obtener datos intradiarios: {response.text}")
        return None

def obtener_busqueda_simbolos(palabras_clave):
    """Busca símbolos de empresas basado en palabras clave"""
    params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': palabras_clave,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
            
        resultados = data.get('bestMatches', [])
        
        print(f"\nResultados de búsqueda para '{palabras_clave}':")
        print(f"Total de coincidencias: {len(resultados)}")
        
        if resultados:
            for i, match in enumerate(resultados):
                print(f"\nCoincidencia {i+1}:")
                print(f"Símbolo: {match.get('1. symbol')}")
                print(f"Nombre: {match.get('2. name')}")
                print(f"Tipo: {match.get('3. type')}")
                print(f"Región: {match.get('4. region')}")
                print(f"Zona horaria: {match.get('7. timezone')}")
                print(f"Moneda: {match.get('8. currency')}")
        
        return resultados
    else:
        print(f"Error al buscar símbolos: {response.text}")
        return None

def obtener_indicador_tecnico(simbolo, indicador='SMA', intervalo='daily', periodo=50, serie_tiempo='close'):
    """
    Obtiene un indicador técnico para un símbolo
    indicador: 'SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'MAMA', 'T3', 'MACD', 'RSI', etc.
    intervalo: 'daily', 'weekly', 'monthly'
    """
    params = {
        'function': indicador,
        'symbol': simbolo,
        'interval': intervalo,
        'time_period': periodo,
        'series_type': serie_tiempo,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
            
        # El formato de la respuesta varía según el indicador
        meta_data = data.get(f'Meta Data', {})
        indicator_key = [k for k in data.keys() if 'Meta Data' not in k]
        
        if not indicator_key:
            print("No se encontraron datos de indicador técnico")
            return None
            
        indicator_data = data.get(indicator_key[0], {})
        
        print(f"\nIndicador técnico {indicador} para {simbolo} (intervalo: {intervalo}, periodo: {periodo}):")
        print("\nMetadatos:")
        for key, value in meta_data.items():
            print(f"  {key}: {value}")
        
        fechas = list(indicator_data.keys())
        if fechas:
            print(f"\nPeríodo: {fechas[-1]} a {fechas[0]}")
            print(f"Total de registros: {len(fechas)}")
            print("\nMuestra de los datos más recientes:")
            for i, fecha in enumerate(fechas[:5]):
                print(f"{fecha}: {indicator_data[fecha]}")
        
        return {
            'meta_data': meta_data,
            'indicator_data': indicator_data
        }
    else:
        print(f"Error al obtener indicador técnico: {response.text}")
        return None

def obtener_datos_fundamentales(simbolo, funcion='OVERVIEW'):
    """
    Obtiene datos fundamentales para un símbolo
    funcion: 'OVERVIEW', 'INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW', 'EARNINGS'
    """
    params = {
        'function': funcion,
        'symbol': simbolo,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
        elif not data:
            print(f"No se encontraron datos fundamentales para {simbolo} con la función {funcion}")
            return None
            
        print(f"\nDatos fundamentales ({funcion}) para {simbolo}:")
        
        if funcion == 'OVERVIEW':
            # Para vista general, mostrar información clave seleccionada
            keys_to_show = [
                'Symbol', 'Name', 'Description', 'Exchange', 'Industry', 'Sector',
                'MarketCapitalization', 'PERatio', 'DividendYield', 'EPS',
                '52WeekHigh', '52WeekLow'
            ]
            
            for key in keys_to_show:
                if key in data:
                    print(f"{key}: {data[key]}")
                    
            print(f"\nTotal de campos disponibles: {len(data)}")
        elif funcion in ['INCOME_STATEMENT', 'BALANCE_SHEET', 'CASH_FLOW']:
            # Para estados financieros, mostrar reportes anuales
            annual_reports = data.get('annualReports', [])
            quarterly_reports = data.get('quarterlyReports', [])
            
            print(f"Reportes anuales disponibles: {len(annual_reports)}")
            print(f"Reportes trimestrales disponibles: {len(quarterly_reports)}")
            
            if annual_reports:
                print("\nÚltimo reporte anual:")
                report = annual_reports[0]
                print(f"Fecha fiscal: {report.get('fiscalDateEnding')}")
                for key, value in list(report.items())[:10]:  # Mostrar primeros 10 campos
                    print(f"  {key}: {value}")
                print("  ...")
        elif funcion == 'EARNINGS':
            # Para ganancias, mostrar sorpresas de ganancias trimestrales
            annual_earnings = data.get('annualEarnings', [])
            quarterly_earnings = data.get('quarterlyEarnings', [])
            
            print(f"Reportes anuales de ganancias: {len(annual_earnings)}")
            print(f"Reportes trimestrales de ganancias: {len(quarterly_earnings)}")
            
            if quarterly_earnings:
                print("\nÚltimos reportes trimestrales de ganancias:")
                for i, quarter in enumerate(quarterly_earnings[:4]):  # Mostrar últimos 4 trimestres
                    print(f"\nTrimestre {i+1}:")
                    print(f"  Fecha fiscal: {quarter.get('fiscalDateEnding')}")
                    print(f"  Fecha reportada: {quarter.get('reportedDate')}")
                    print(f"  EPS estimado: {quarter.get('estimatedEPS')}")
                    print(f"  EPS reportado: {quarter.get('reportedEPS')}")
                    print(f"  Sorpresa: {quarter.get('surprise')}")
                    print(f"  Sorpresa %: {quarter.get('surprisePercentage')}")
        
        return data
    else:
        print(f"Error al obtener datos fundamentales: {response.text}")
        return None

def obtener_datos_forex(desde_simbolo, hacia_simbolo, funcion='FX_DAILY', tamano_salida='compact'):
    """
    Obtiene datos de Forex
    funcion: 'FX_DAILY', 'FX_WEEKLY', 'FX_MONTHLY'
    tamano_salida: 'compact' (últimos 100 datos) o 'full' (datos completos)
    """
    params = {
        'function': funcion,
        'from_symbol': desde_simbolo,
        'to_symbol': hacia_simbolo,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': tamano_salida
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
            
        meta_data = data.get('Meta Data', {})
        
        # Determinar la clave correcta para los datos de series temporales
        time_series_key = None
        for key in data.keys():
            if 'Time Series FX' in key:
                time_series_key = key
                break
                
        if not time_series_key:
            print("No se encontraron datos de Forex")
            return None
            
        time_series_data = data.get(time_series_key, {})
        
        print(f"\nDatos Forex para {desde_simbolo}/{hacia_simbolo} ({funcion}):")
        print("\nMetadatos:")
        for key, value in meta_data.items():
            print(f"  {key}: {value}")
        
        fechas = list(time_series_data.keys())
        if fechas:
            print(f"\nPeríodo: {fechas[-1]} a {fechas[0]}")
            print(f"Total de registros: {len(fechas)}")
            print("\nMuestra de los datos más recientes:")
            for i, fecha in enumerate(fechas[:3]):
                print(f"Fecha: {fecha}")
                print(json.dumps(time_series_data[fecha], indent=2))
                if i < 2:  # Separador entre fechas
                    print("-" * 40)
        
        return {
            'meta_data': meta_data,
            'time_series_data': time_series_data
        }
    else:
        print(f"Error al obtener datos Forex: {response.text}")
        return None

def obtener_datos_crypto(simbolo, mercado, funcion='DIGITAL_CURRENCY_DAILY'):
    """
    Obtiene datos de criptomonedas
    funcion: 'DIGITAL_CURRENCY_DAILY', 'DIGITAL_CURRENCY_WEEKLY', 'DIGITAL_CURRENCY_MONTHLY'
    """
    params = {
        'function': funcion,
        'symbol': simbolo,
        'market': mercado,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
            
        meta_data = data.get('Meta Data', {})
        
        # Determinar la clave correcta para los datos de series temporales
        time_series_key = None
        for key in data.keys():
            if 'Time Series (Digital Currency' in key:
                time_series_key = key
                break
                
        if not time_series_key:
            print("No se encontraron datos de criptomonedas")
            return None
            
        time_series_data = data.get(time_series_key, {})
        
        print(f"\nDatos de {simbolo} en {mercado} ({funcion}):")
        print("\nMetadatos:")
        for key, value in meta_data.items():
            print(f"  {key}: {value}")
        
        fechas = list(time_series_data.keys())
        if fechas:
            print(f"\nPeríodo: {fechas[-1]} a {fechas[0]}")
            print(f"Total de registros: {len(fechas)}")
            print("\nMuestra de los datos más recientes:")
            for i, fecha in enumerate(fechas[:3]):
                print(f"Fecha: {fecha}")
                datos_dia = time_series_data[fecha]
                for key, value in datos_dia.items():
                    if 'USD' in key:  # Mostrar solo valores en USD para simplificar
                        print(f"  {key}: {value}")
                if i < 2:  # Separador entre fechas
                    print("-" * 40)
        
        return {
            'meta_data': meta_data,
            'time_series_data': time_series_data
        }
    else:
        print(f"Error al obtener datos de criptomonedas: {response.text}")
        return None

def obtener_indicadores_economicos(indicador, intervalo='monthly'):
    """
    Obtiene indicadores económicos
    indicador: 'REAL_GDP', 'REAL_GDP_PER_CAPITA', 'TREASURY_YIELD', 'FEDERAL_FUNDS_RATE', 'CPI', etc.
    intervalo: 'monthly', 'quarterly', 'annual'
    """
    params = {
        'function': indicador,
        'interval': intervalo,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    # Para el rendimiento del tesoro, es necesario especificar el vencimiento
    if indicador == 'TREASURY_YIELD':
        params['maturity'] = '10year'  # Valores: '3month', '2year', '5year', '7year', '10year', '30year'
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'Error Message' in data:
            print(f"Error de API: {data['Error Message']}")
            return None
        elif 'Note' in data and 'call frequency' in data['Note']:
            print(f"Aviso de limitación de llamadas: {data['Note']}")
            return None
            
        # Obtener nombre y datos
        nombre = data.get('name', 'Indicador sin nombre')
        intervalos = data.get('interval', '')
        unidad = data.get('unit', '')
        datos = data.get('data', [])
        
        print(f"\nIndicador económico: {nombre}")
        print(f"Intervalo: {intervalos}")
        print(f"Unidad: {unidad}")
        print(f"Total de registros: {len(datos)}")
        
        if datos:
            print("\nDatos más recientes:")
            for i, punto in enumerate(datos[:5]):
                date_val = punto.get('date', 'Sin fecha')
                value = punto.get('value', 'Sin valor')
                print(f"{date_val}: {value}")
        
        return data
    else:
        print(f"Error al obtener indicador económico: {response.text}")
        return None

def ejecutar_pruebas_completas():
    """Ejecuta una batería de pruebas completa para la API de Alpha Vantage"""
    print("=== INICIANDO PRUEBAS DE LA API DE ALPHA VANTAGE ===")
    print("NOTA: Alpha Vantage limita a 5 llamadas por minuto en el plan gratuito")
    print("      Las pruebas pueden pausarse entre llamadas para evitar errores")
    
    # Test de conexión básica
    if not test_conexion_api():
        print("Error en la conexión básica. Verificar API key.")
        return
        
    # Introducir pausa entre llamadas para evitar límites de frecuencia
    print("\nEsperado 15 segundos para evitar límites de frecuencia...")
    import time
    time.sleep(15)
    
    # Test de datos diarios
    obtener_datos_diarios('AAPL')
    time.sleep(15)
    
    # Test de datos intradiarios
    obtener_datos_intradiarios('MSFT', '5min')
    time.sleep(15)
    
    # Test de búsqueda de símbolos
    obtener_busqueda_simbolos('Microsoft')
    time.sleep(15)
    
    # Test de indicador técnico
    obtener_indicador_tecnico('GOOGL', 'SMA', 'daily', 50)
    time.sleep(15)
    
    # Test de datos fundamentales
    obtener_datos_fundamentales('TSLA', 'OVERVIEW')
    time.sleep(15)
    
    # Test de datos Forex
    obtener_datos_forex('EUR', 'USD', 'FX_DAILY')
    time.sleep(15)
    
    # Test de datos de criptomonedas
    obtener_datos_crypto('BTC', 'USD')
    time.sleep(15)
    
    # Test de indicadores económicos
    obtener_indicadores_economicos('REAL_GDP', 'quarterly')
    
    print("\n=== PRUEBAS COMPLETADAS ===")

# Ejecutar pruebas solo si se ejecuta como script principal
if __name__ == "__main__":
    print("Script de pruebas para la API de Alpha Vantage")
    print("=============================================")
    print(f"Pandas y Matplotlib instalados: {PANDAS_INSTALLED}")
    print("\nPara ejecutar todas las pruebas (atención a límites de llamadas):")
    print("  python3 alphavantage_test.py all")
    print("\nPara ejecutar pruebas individuales, usa:")
    print("  python3 alphavantage_test.py conexion       # Prueba de conexión básica")
    print("  python3 alphavantage_test.py diarios        # Datos diarios de AAPL")
    print("  python3 alphavantage_test.py intradiarios   # Datos intradiarios de MSFT")
    print("  python3 alphavantage_test.py busqueda       # Búsqueda de símbolos 'Microsoft'")
    print("  python3 alphavantage_test.py indicador      # Indicador técnico SMA para GOOGL")
    print("  python3 alphavantage_test.py fundamentales  # Datos fundamentales de TSLA")
    print("  python3 alphavantage_test.py forex          # Datos Forex EUR/USD")
    print("  python3 alphavantage_test.py crypto         # Datos de Bitcoin en USD")
    print("  python3 alphavantage_test.py economicos     # Indicador económico GDP")
    
    # Procesar argumentos de línea de comandos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "all":
            ejecutar_pruebas_completas()
        elif comando == "conexion":
            test_conexion_api()
        elif comando == "diarios":
            obtener_datos_diarios('AAPL')
        elif comando == "intradiarios":
            obtener_datos_intradiarios('MSFT', '5min')
        elif comando == "busqueda":
            obtener_busqueda_simbolos('Microsoft')
        elif comando == "indicador":
            obtener_indicador_tecnico('GOOGL', 'SMA', 'daily', 50)
        elif comando == "fundamentales":
            obtener_datos_fundamentales('TSLA', 'OVERVIEW')
        elif comando == "forex":
            obtener_datos_forex('EUR', 'USD', 'FX_DAILY')
        elif comando == "crypto":
            obtener_datos_crypto('BTC', 'USD')
        elif comando == "economicos":
            obtener_indicadores_economicos('REAL_GDP', 'quarterly')
        else:
            print(f"Comando no reconocido: {comando}")
    else:
        # Si no hay argumentos, mostrar instrucciones
        print("\nSin argumentos. Por favor, especifica una prueba a ejecutar.")

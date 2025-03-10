import requests
import json
import sys
from datetime import datetime, timedelta

# Comprobar si pandas está instalado e informar al usuario
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

# Configura tu token de Tiingo aquí
TIINGO_API_TOKEN = ""  # Reemplaza con tu token real

# Headers para las solicitudes
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Token {TIINGO_API_TOKEN}'
}

# URL base de la API
base_url = "https://api.tiingo.com"

def test_conexion_api():
    """Prueba básica para verificar que podemos conectarnos a la API"""
    url = f"{base_url}/tiingo/daily/AAPL/prices"
    params = {
        'startDate': '2023-01-01',
        'endDate': '2023-01-10',
        'format': 'json'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    print(f"Estado de la conexión: {response.status_code}")
    print(f"Headers de respuesta: {response.headers}")
    
    if response.status_code == 200:
        print("Conexión exitosa a la API de Tiingo")
        data = response.json()
        print(f"Muestra de datos recibidos (primeros 2 registros):")
        for i, record in enumerate(data[:2]):
            print(f"Registro {i+1}: {record}")
    else:
        print(f"Error al conectar: {response.text}")
    
    return response.status_code == 200

def obtener_datos_historicos(ticker, fecha_inicio, fecha_fin):
    """Obtiene datos históricos de precios para un ticker específico"""
    url = f"{base_url}/tiingo/daily/{ticker}/prices"
    params = {
        'startDate': fecha_inicio,
        'endDate': fecha_fin,
        'format': 'json'
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if PANDAS_INSTALLED:
            df = pd.DataFrame(data)
            print(f"\nDatos históricos para {ticker} del {fecha_inicio} al {fecha_fin}")
            print(f"Columnas disponibles: {df.columns.tolist()}")
            print(df.head())
            
            # Visualizar precios de cierre
            if not df.empty and 'close' in df.columns:
                plt.figure(figsize=(10, 5))
                plt.plot(df['date'], df['close'])
                plt.title(f'Precios de cierre para {ticker}')
                plt.xlabel('Fecha')
                plt.ylabel('Precio ($)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f"{ticker}_precios.png")
                print(f"Gráfico guardado como {ticker}_precios.png")
            
            return df
        else:
            print(f"\nDatos históricos para {ticker} del {fecha_inicio} al {fecha_fin}")
            print(f"Total de registros: {len(data)}")
            print("Primeros 3 registros:")
            for i, record in enumerate(data[:3]):
                print(f"Registro {i+1}: {json.dumps(record, indent=2)}")
            return data
    else:
        print(f"Error al obtener datos históricos: {response.text}")
        return None

def buscar_meta_datos(ticker):
    """Obtiene metadatos para un ticker específico"""
    url = f"{base_url}/tiingo/daily/{ticker}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nMetadatos para {ticker}:")
        for key, value in data.items():
            print(f"{key}: {value}")
        return data
    else:
        print(f"Error al obtener metadatos: {response.text}")
        return None

def obtener_noticias(tickers, num_noticias=5):
    """Obtiene noticias recientes relacionadas con los tickers especificados"""
    url = f"{base_url}/tiingo/news"
    params = {
        'tickers': tickers,
        'limit': num_noticias
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        noticias = response.json()
        print(f"\nÚltimas {num_noticias} noticias para {tickers}:")
        for i, noticia in enumerate(noticias):
            print(f"\nNoticia {i+1}:")
            print(f"Título: {noticia.get('title')}")
            print(f"Fecha: {noticia.get('publishedDate')}")
            print(f"Fuente: {noticia.get('source')}")
            print(f"URL: {noticia.get('url')}")
        return noticias
    else:
        print(f"Error al obtener noticias: {response.text}")
        return None

def obtener_datos_fundamentales(ticker):
    """Obtiene datos fundamentales para un ticker específico (requiere suscripción)"""
    url = f"{base_url}/fundamentals/{ticker}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nDatos fundamentales para {ticker}:")
        print(f"Información disponible: {list(data.keys())}")
        # Mostrar algunos datos financieros si están disponibles
        if 'financials' in data:
            print("\nÚltimos datos financieros:")
            for k, v in list(data['financials'].items())[:5]:  # Mostramos los primeros 5 items
                print(f"{k}: {v}")
        return data
    else:
        print(f"Error al obtener datos fundamentales: {response.text}")
        print("Nota: Los datos fundamentales pueden requerir una suscripción premium.")
        return None

def obtener_lista_tickers():
    """Obtiene una lista de todos los tickers soportados por Tiingo"""
    url = f"{base_url}/tiingo/utilities/supported/tickers"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        tickers = response.json()
        print(f"\nTotal de tickers soportados: {len(tickers)}")
        print(f"Primeros 10 tickers: {[t.get('ticker') for t in tickers[:10]]}")
        return tickers
    else:
        print(f"Error al obtener lista de tickers: {response.text}")
        return None

def obtener_datos_crypto(ticker, fecha_inicio, fecha_fin, resample='1day'):
    """Obtiene datos de criptomonedas"""
    url = f"{base_url}/tiingo/crypto/prices"
    params = {
        'tickers': ticker,
        'startDate': fecha_inicio,
        'endDate': fecha_fin,
        'resampleFreq': resample
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data and 'data' in data[0]:
            crypto_data = data[0]['data']
            
            if PANDAS_INSTALLED:
                df = pd.DataFrame(crypto_data)
                print(f"\nDatos de criptomoneda para {ticker} del {fecha_inicio} al {fecha_fin}")
                print(f"Columnas disponibles: {df.columns.tolist()}")
                print(df.head())
                return df
            else:
                print(f"\nDatos de criptomoneda para {ticker} del {fecha_inicio} al {fecha_fin}")
                print(f"Total de registros: {len(crypto_data)}")
                print("Primeros 3 registros:")
                for i, record in enumerate(crypto_data[:3]):
                    print(f"Registro {i+1}: {json.dumps(record, indent=2)}")
                return crypto_data
        else:
            print("No se encontraron datos para la criptomoneda solicitada")
            return None
    else:
        print(f"Error al obtener datos de criptomonedas: {response.text}")
        return None

def obtener_datos_forex(ticker, fecha_inicio, fecha_fin, resample='1day'):
    """Obtiene datos de Forex"""
    url = f"{base_url}/tiingo/fx/{ticker}/prices"
    params = {
        'startDate': fecha_inicio,
        'endDate': fecha_fin,
        'resampleFreq': resample
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        if PANDAS_INSTALLED:
            df = pd.DataFrame(data)
            print(f"\nDatos de Forex para {ticker} del {fecha_inicio} al {fecha_fin}")
            print(f"Columnas disponibles: {df.columns.tolist()}")
            print(df.head())
            return df
        else:
            print(f"\nDatos de Forex para {ticker} del {fecha_inicio} al {fecha_fin}")
            print(f"Total de registros: {len(data)}")
            print("Primeros 3 registros:")
            for i, record in enumerate(data[:3]):
                print(f"Registro {i+1}: {json.dumps(record, indent=2)}")
            return data
    else:
        print(f"Error al obtener datos de Forex: {response.text}")
        return None

def ejecutar_pruebas_completas():
    """Ejecuta una batería de pruebas completa para la API de Tiingo"""
    print("=== INICIANDO PRUEBAS DE LA API DE TIINGO ===")
    
    # Test de conexión básica
    if not test_conexion_api():
        print("Error en la conexión básica. Verificar token y conectividad.")
        return
    
    # Fechas para las pruebas
    hoy = datetime.now()
    fecha_fin = hoy.strftime('%Y-%m-%d')
    fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Test de datos históricos
    obtener_datos_historicos('AAPL', fecha_inicio, fecha_fin)
    
    # Test de metadatos
    buscar_meta_datos('MSFT')
    
    # Test de noticias
    obtener_noticias('AAPL,MSFT,GOOGL')
    
    # Test de datos fundamentales
    obtener_datos_fundamentales('AAPL')
    
    # Test de lista de tickers
    obtener_lista_tickers()
    
    # Test de datos de criptomonedas
    obtener_datos_crypto('btcusd', fecha_inicio, fecha_fin)
    
    # Test de datos de Forex
    obtener_datos_forex('eurusd', fecha_inicio, fecha_fin)
    
    print("\n=== PRUEBAS COMPLETADAS ===")

# Ejecutar pruebas solo si se ejecuta como script principal
if __name__ == "__main__":
    print("Script de pruebas para la API de Tiingo")
    print("=======================================")
    print(f"Pandas y Matplotlib instalados: {PANDAS_INSTALLED}")
    print("\nPara ejecutar todas las pruebas, escribe:")
    print("  python3 test.py all")
    print("\nPara ejecutar pruebas individuales, usa:")
    print("  python3 test.py conexion       # Prueba de conexión básica")
    print("  python3 test.py historicos     # Datos históricos de AAPL")
    print("  python3 test.py metadatos      # Metadatos para MSFT")
    print("  python3 test.py noticias       # Noticias de AAPL, MSFT, GOOGL")
    print("  python3 test.py fundamentales  # Datos fundamentales de AAPL")
    print("  python3 test.py tickers        # Lista de tickers soportados")
    print("  python3 test.py crypto         # Datos de criptomonedas (BTC/USD)")
    print("  python3 test.py forex          # Datos de Forex (EUR/USD)")
    
    # Fechas para las pruebas
    hoy = datetime.now()
    fecha_fin = hoy.strftime('%Y-%m-%d')
    fecha_inicio = (hoy - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Procesar argumentos de línea de comandos
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "all":
            ejecutar_pruebas_completas()
        elif comando == "conexion":
            test_conexion_api()
        elif comando == "historicos":
            obtener_datos_historicos('AAPL', fecha_inicio, fecha_fin)
        elif comando == "metadatos":
            buscar_meta_datos('MSFT')
        elif comando == "noticias":
            obtener_noticias('AAPL,MSFT,GOOGL')
        elif comando == "fundamentales":
            obtener_datos_fundamentales('AAPL')
        elif comando == "tickers":
            obtener_lista_tickers()
        elif comando == "crypto":
            obtener_datos_crypto('btcusd', fecha_inicio, fecha_fin)
        elif comando == "forex":
            obtener_datos_forex('eurusd', fecha_inicio, fecha_fin)
        else:
            print(f"Comando no reconocido: {comando}")
    else:
        # Si no hay argumentos, mostrar instrucciones
        print("\nSin argumentos. Por favor, especifica una prueba a ejecutar.")
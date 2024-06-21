import datetime
import time

# Obtener el tiempo inicial
timestamp_inicio = datetime.datetime.now()
print("Tiempo de inicio:", timestamp_inicio.strftime("%H:%M:%S"))

# Simular alguna operación o espera
time.sleep(5)  # Esperar 5 segundos, puedes cambiar esto por el tiempo que necesites

# Obtener el tiempo final
timestamp_final = datetime.datetime.now()
print("Tiempo final:", timestamp_final.strftime("%H:%M:%S"))

# Calcular la diferencia
diferencia = timestamp_final - timestamp_inicio

# Convertir la diferencia a segundos
diferencia_segundos = int(diferencia.total_seconds())

# Formatear la diferencia como HH:MM:SS
tiempo_transcurrido = str(datetime.timedelta(seconds=diferencia_segundos))
print("Tiempo transcurrido:", tiempo_transcurrido)
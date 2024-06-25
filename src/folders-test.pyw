#Manejo de folders
import datetime
import os
import shutil
import time
import psutil

def checar_espacio_disponible(ruta):
    # Obtener el uso del disco
    uso_disco = psutil.disk_usage(ruta)
    
    # Mostrar la información del uso del disco
    print(f"Ruta: {ruta}")
    print(f"Total: {uso_disco.total / (1024 ** 3):.2f} GB")
    print(f"Usado: {uso_disco.used / (1024 ** 3):.2f} GB")
    print(f"Libre: {uso_disco.free / (1024 ** 3):.2f} GB")
    print(f"Porcentaje usado: {uso_disco.percent}%")

def creacionCarpetas(ruta_base):
    # Definir la ruta base
    

    # Asegurarse de que la ruta base existe
    if not os.path.exists(ruta_base):
        os.makedirs(ruta_base)

    # Obtener la fecha actual
    fecha_actual = datetime.datetime.now()

    # Crear carpetas de la fecha actual a 14 días atrás
    for i in range(15):  # Incluye la fecha actual y los 14 días anteriores
        fecha = fecha_actual - datetime.timedelta(days=i)
        nombre_carpeta = fecha.strftime('%Y%m%d')
        ruta_carpeta = os.path.join(ruta_base, nombre_carpeta)
        
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)
            print(f'Carpeta creada: {ruta_carpeta}')
        else:
            print(f'La carpeta ya existe: {ruta_carpeta}')

def borrar_carpetas_antiguas(ruta_base):
    # Obtener la fecha actual
    fecha_actual = datetime.datetime.now()

    # Calcular la fecha límite (7 días atrás)
    fecha_limite = fecha_actual - datetime.timedelta(days=7)

    # Listar todas las carpetas en la ruta base
    carpetas = [f for f in os.listdir(ruta_base) if os.path.isdir(os.path.join(ruta_base, f))]

    for carpeta in carpetas:
        try:
            # Intentar convertir el nombre de la carpeta en una fecha
            fecha_carpeta = datetime.datetime.strptime(carpeta, '%Y%m%d')

            # Si la fecha de la carpeta es anterior a la fecha límite, borrarla
            if fecha_carpeta < fecha_limite:
                ruta_carpeta = os.path.join(ruta_base, carpeta)
                shutil.rmtree(ruta_carpeta)
                print(f'Carpeta borrada: {ruta_carpeta}')
        except ValueError:
            # Si el nombre de la carpeta no es una fecha válida, continuar
            continue

def semanas_en_mes(year, month):
    # Obtener el primer y último día del mes
    primer_dia = datetime.date(year, month, 1)
    if month == 12:
        ultimo_dia = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        ultimo_dia = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # Calcular el número de semanas
    semanas = (ultimo_dia - primer_dia).days // 7 + 1
    return semanas

def domingos_en_mes(year, month):
    # Contador de domingos
    contador_domingos = 0
    
    # Obtener el primer día del mes
    primer_dia = datetime.date(year, month, 1)
    
    # Calcular el último día del mes
    if month == 12:
        ultimo_dia = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        ultimo_dia = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # Recorrer los días del mes
    dia_actual = primer_dia
    while dia_actual <= ultimo_dia:
        if dia_actual.weekday() == 6:  # 6 corresponde a domingo
            contador_domingos += 1
        dia_actual += datetime.timedelta(days=1)
    
    return contador_domingos

def semana_del_mes(fecha):
    # Obtener el primer día del mes
    primer_dia_del_mes = fecha.replace(day=1)
    # Calcular el número de la semana ISO del primer día del mes
    semana_inicio_mes = primer_dia_del_mes.isocalendar()[1]
    
    # Calcular el número de la semana ISO de la fecha actual
    semana_actual = fecha.isocalendar()[1]
    
    # Si el primer día del mes cae en la semana anterior (es decir, semana ISO 52 o 53), ajustar el cálculo
    if primer_dia_del_mes.weekday() != 0 and semana_inicio_mes > semana_actual:
        semana_inicio_mes = 1
    
    # Calcular la semana del mes actual
    semana_del_mes_actual = semana_actual - semana_inicio_mes + 1
    return semana_del_mes_actual

if __name__ == "__main__":
    #crear folders de la fecha actual a 14 dias atras usando el formato YYYYMMDD o 20240624
    #en ruta c:/temp-pruebas/

    
    fecha_actual = datetime.datetime.now()
    year = fecha_actual.year
    month = fecha_actual.month
    ruta_base = 'c:/temp-pruebas/'

  
    backup_dir = fr'\\10.0.0.17\BACKUP_TRESS$\DIARIO\\'
    checar_espacio_disponible(backup_dir)      

    semanas = semanas_en_mes(year, month)
    domingos = domingos_en_mes(year, month)
    semana_actual = datetime.datetime.now()


    print(f"El mes actual ({year}-{month}) tiene {semanas} semanas.")
    print(f"El mes actual ({year}-{month}) tiene {domingos} domingos.")
    print(f"Estamos en la semana {semana_del_mes(fecha_actual)} del mes actual ({fecha_actual.year}-{fecha_actual.month}).")
import pyodbc
import datetime
import os

fecha_actual = datetime.datetime.now().strftime("%Y%m%d")
# Configuración para la conexión a SQL Server
server = '10.0.0.12'
username = 'SA'
password = 'Mexico2006'
backup_dir = fr'\\10.0.0.17\BACKUP_TRESS$\DIARIO\{fecha_actual}\\'  # Directorio donde se guardará el respaldo

def crear_carpeta():
    if not os.path.exists(backup_dir):
        # Crear la carpeta
        os.makedirs(backup_dir)
        print(f"La carpeta '{backup_dir}' se creó correctamente.")
    else:
        print(f"La carpeta '{backup_dir}' ya existe.")
def backup_completo():
    # Crear una conexión
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Obtener la lista de bases de datos (excluyendo las de sistema)
    cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
    databases = cursor.fetchall()

    # Iterar a través de cada base de datos
    for db in databases:
        database_name = db[0]
        
        # Excluir bases de sistema
        if database_name not in ('master', 'model', 'msdb', 'tempdb'):
            try:
                   # Obtener la marca de tiempo actual para el nombre del archivo de respaldo
                    timestamp_inicio = datetime.datetime.now()
                    print(f"Inicio de respaldo {database_name} Hora: {timestamp_inicio.strftime('%H:%M:%S')}")
                    backup_file = os.path.join(backup_dir, f"{database_name}.bak")

                    # Comando de respaldo (asegurándote de usar corchetes si el nombre de la base de datos contiene guiones)
                    backup_command = f"BACKUP DATABASE [{database_name}] TO DISK='{backup_file}' WITH COMPRESSION, MEDIADESCRIPTION='{database_name} Backup';"

                    # Ejecutar el comando de respaldo
                    cursor.execute(backup_command)
                    
                    # Consumir los mensajes de progreso del respaldo
                    while cursor.nextset():
                        pass

                    # Obtener la marca de tiempo final
                    timestamp_final = datetime.datetime.now()
                    
                    # Calcular la diferencia
                    diferencia = timestamp_final - timestamp_inicio
                    diferencia_segundos = int(diferencia.total_seconds())
                    tiempo_transcurrido = str(datetime.timedelta(seconds=diferencia_segundos))
                    
                    print(f"Respaldo completado en el servidor: {backup_file} Hora: {timestamp_final.strftime('%H:%M:%S')}")
                    print(f"Duración del respaldo: {tiempo_transcurrido}")
            except Exception as e:
            
                print(f"Error durante el respaldo: {e}")

    # Cerrar la conexión
    cursor.close()
    conn.close()

def backup_especifico(bases_a_respaldar):
    # Crear una conexión
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID={username};PWD={password}'
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Iterar a través de cada base de datos deseada
        for database_name in bases_a_respaldar:
            # Obtener la marca de tiempo actual para el nombre del archivo de respaldo
            timestamp_inicio = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"Incio de respaldo {database_name} Hora : {timestamp_inicio}")
            backup_file = os.path.join(backup_dir, f"{database_name}.bak")
            
            # Comando de respaldo
            backup_command = f"BACKUP DATABASE [{database_name}] TO DISK='{backup_file}' WITH COMPRESSION, MEDIADESCRIPTION='{database_name} Backup';"
            
            # Ejecutar el comando de respaldo
            cursor.execute(backup_command)
            
            # Consumir los mensajes de progreso del respaldo
            while cursor.nextset():
                pass
            timestamp_final = datetime.datetime.now().strftime("%H:%M:%S")
            diferencia = timestamp_final - timestamp_inicio
            diferencia_segundos = int(diferencia.total_seconds())
            print(f"Respaldo completado en el servidor: {backup_file} Hora: {timestamp_final}")
            print(f"Duracion de respaldo:{str(datetime.timedelta(seconds=diferencia_segundos))}")
    except Exception as e:
        timestamp_finalerror = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"Error durante el respaldo: {e} Hora: {timestamp_finalerror}")

    # Cerrar la conexión
    cursor.close()
    conn.close()



if __name__ == "__main__":
    crear_carpeta()
    backup_completo()
    #backup_completo()
    #bases= ["NCOMPARTE","KIOSKOTEK"]
    #backup_especifico(bases)

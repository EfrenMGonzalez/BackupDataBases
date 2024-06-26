import pyodbc
import datetime
import os
import yaml
import tkinter as tk
from tkinter import messagebox
import psutil
import schedule
import time


config = {
    'server': '',
    'username': '',
    'password': '',
    'backup_dir': '',
    'hora_respaldo':''
}

# Función para guardar la configuración en un archivo YAML
def guardar_configuracion(ip, usuario, contrasena, ubicacion,hora):
    config = {
        'server': ip,
        'username': usuario,
        'password': contrasena,
        'backup_dir': ubicacion,
        'hora_respaldo':hora
    }
    with open('configuracion.yaml', 'w') as file:
        yaml.dump(config, file)
    messagebox.showinfo("Información", "Configuración guardada correctamente")
    root.quit()

def leer_configuracion():
    global config
    with open('configuracion.yaml', 'r') as file:
        config = yaml.safe_load(file)

def crear_carpeta(backup_folder):
    if not os.path.exists(backup_folder):
        # Crear la carpeta
        os.makedirs(backup_folder)
        print(f"La carpeta '{backup_folder}' se creó correctamente.")
    else:
        print(f"La carpeta '{backup_folder}' ya existe.")

def backup_completo(backup_folder):
    crear_carpeta(backup_folder)
    # Crear una conexión
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config['server']};UID={config['username']};PWD={config['password']}'
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
                    backup_file = os.path.join(backup_folder, f"{database_name}.bak")

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
                messagebox.showerror(f"Error al respaldar{database_name}",f"Se presento un error al respaldar la base de datos.\nError:{e}")

    # Cerrar la conexión
    cursor.close()
    conn.close()
    messagebox.showinfo("Informacion", "Las bases de datos han sido respaldadas correctamente.")

def backup_especifico(bases_a_respaldar,backup_folder):
    # Crear una conexión
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config['server']};UID={config['username']};PWD={config['password']}'
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Iterar a través de cada base de datos deseada
        for database_name in bases_a_respaldar:
            # Obtener la marca de tiempo actual para el nombre del archivo de respaldo
            timestamp_inicio = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"Incio de respaldo {database_name} Hora : {timestamp_inicio}")
            backup_file = os.path.join(backup_folder, f"{database_name}.bak")
            
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

def print_server_info(backup_folder):
    print(config['server'])
    print(config['username'])
    print(config['password'])
    print(backup_folder)
    print(config['hora_respaldo'])

def checar_espacio_disponible(ruta):
    # Obtener el uso del disco
    uso_disco = psutil.disk_usage(ruta)
    
    # Mostrar la información del uso del disco
    print(f"Ruta: {ruta}")
    print(f"Total: {uso_disco.total / (1024 ** 3):.2f} GB")
    print(f"Usado: {uso_disco.used / (1024 ** 3):.2f} GB")
    print(f"Libre: {uso_disco.free / (1024 ** 3):.2f} GB")
    print(f"Porcentaje usado: {uso_disco.percent}%")
    return uso_disco

def cancelar():
    root.quit()

def respaldo_programado(folder):
    # Programa la tarea para que se ejecute todos los días a las 10:30
    hora_str = config['hora_respaldo']
    print(hora_str)
  
    schedule.every().day.at(hora_str).do(backup_completo,folder)
 
    while True:
       
        schedule.run_pending()
        time.sleep(1)
        
if __name__ == "__main__":
    if not os.path.exists('configuracion.yaml'):
        root = tk.Tk()
        root.geometry('200x450')
        root.title("Configuración del Programa")

        # Crear etiquetas y entradas para los datos del servidor
        tk.Label(root, text="IP del Servidor:").pack(pady=5)
        ip_entry = tk.Entry(root)
        ip_entry.pack(pady=5)

        tk.Label(root, text="Usuario de BD:").pack(pady=5)
        usuario_entry = tk.Entry(root)
        usuario_entry.pack(pady=5)

        tk.Label(root, text="Contraseña:").pack(pady=5)
        contrasena_entry = tk.Entry(root, show="*")
        contrasena_entry.pack(pady=5)

        tk.Label(root, text="Ubicación de Respaldo:").pack(pady=5)
        ubicacion_entry = tk.Entry(root)
        ubicacion_entry.pack(pady=5)

        tk.Label(root, text="Hora del respaldo:").pack(pady=5)
        horario_entry = tk.Entry(root)
        horario_entry.pack(pady=5)
        

        # Crear botones de Guardar y Cancelar
        tk.Button(root, text="Guardar", command=lambda: guardar_configuracion(
            ip_entry.get(), usuario_entry.get(), contrasena_entry.get(), ubicacion_entry.get(), horario_entry.get())).pack(pady=20)
        tk.Button(root, text="Cancelar", command=cancelar).pack(pady=5)

        root.mainloop()
    else:
        leer_configuracion()
        root = tk.Tk()
        root.geometry('300x450')
        root.title("Respaldos")
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")
        backup_folder = fr'{config['backup_dir']}\{fecha_actual}\\'
        disco = checar_espacio_disponible(config['backup_dir'])
        label=tk.Label(root, text=f"Servidor:{config['server']}\nEspacio disponible: {disco.total / (1024 ** 3):.2f}Gb\nEspacio Usado: {disco.used / (1024 ** 3):.2f}Gb\nEspacio Libre: {disco.free / (1024 ** 3):.2f}Gb ", anchor="w", justify="left")
        # Empacar el Label
        label.pack(side="top", anchor="w", pady=20)
        
        tk.Button(root, text="Iniciar Respaldo", command=lambda:backup_completo(backup_folder)).pack(side="left", padx=10, pady=10)
        tk.Button(root, text="Iniciar Respaldo Programado",command = lambda:respaldo_programado(backup_folder)).pack(side="left", padx=10, pady=10)
        tk.Button(root, text="Salir", command=root.quit).pack(side="left", padx=10, pady=10)


        root.mainloop()


    #crear_carpeta()
    #backup_completo()
    #backup_completo()
    #bases= ["NCOMPARTE","KIOSKOTEK"]
    #backup_especifico(bases)

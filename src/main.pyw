import pyodbc
import datetime
import os
import yaml
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, scrolledtext
import psutil
import schedule
import time
import threading
from cryptography.fernet import Fernet

config = {
    'server': '',
    'username': '',
    'password': '',
    'backup_dir': '',
    'hora_respaldo': '',
    'config_key':''
}

def getDataBases():
    password = descifrar_contrasena(config["password"], config["config_key"])
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]};UID={config["username"]};PWD={password}'
    conn = pyodbc.connect(conn_str)
    
    cursor = conn.cursor()
    query = "SELECT name FROM sys.databases WHERE name NOT IN ('master', 'model', 'msdb', 'tempdb')"
            

    cursor.execute(query)
    databases = [row.name for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return databases

def generar_clave():
    return Fernet.generate_key()
# Función para cifrar la contraseña
def cifrar_contrasena(contrasena, clave):
    fernet = Fernet(clave)
    return fernet.encrypt(contrasena.encode())
# Función para descifrar la contraseña
def descifrar_contrasena(contrasena_cifrada, clave):
    fernet = Fernet(clave)
    return fernet.decrypt(contrasena_cifrada.encode()).decode()
# Función para guardar la configuración en un archivo YAML
def guardar_configuracion(ip, usuario, contrasena, ubicacion, hora):
     # Genera una clave única para cada ejecución del programa
    clave = generar_clave()  
    # Cifra la contraseña
    contrasena_cifrada = cifrar_contrasena(contrasena, clave)
    config = {
        'server': ip,
        'username': usuario,
        'password': contrasena_cifrada.decode(),
        'backup_dir': ubicacion,
        'hora_respaldo': hora,
        'config_key':clave
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
        os.makedirs(backup_folder)
        log(f"La carpeta '{backup_folder}' se creó correctamente.")
    else:
        log(f"La carpeta '{backup_folder}' ya existe.")

def backup_completo(backup_folder):#Codigo para respaldar todas las bases de datos en el servidor.
    crear_carpeta(backup_folder)
    password = descifrar_contrasena(config["password"], config["config_key"])
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]};UID={config["username"]};PWD={password}'
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")
    databases = cursor.fetchall()

    for db in databases:
        database_name = db[0]
        if database_name not in ('master', 'model', 'msdb', 'tempdb'):
            try:
                timestamp_inicio = datetime.datetime.now()
                log(f"Inicio de respaldo {database_name} Hora: {timestamp_inicio.strftime('%H:%M:%S')}")
                backup_file = os.path.join(backup_folder, f"{database_name}.bak")
                backup_command = f"BACKUP DATABASE [{database_name}] TO DISK='{backup_file}' WITH COMPRESSION, MEDIADESCRIPTION='{database_name} Backup';"
                cursor.execute(backup_command)
                while cursor.nextset():
                    pass
                timestamp_final = datetime.datetime.now()
                diferencia = timestamp_final - timestamp_inicio
                diferencia_segundos = int(diferencia.total_seconds())
                tiempo_transcurrido = str(datetime.timedelta(seconds=diferencia_segundos))
                log(f"Respaldo completado: {backup_file} Hora: {timestamp_final.strftime('%H:%M:%S')}")
                log(f"Duración del respaldo: {tiempo_transcurrido}")
            except Exception as e:
                log(f"Error durante el respaldo de {database_name}: {e}")
                #messagebox.showerror(f"Error al respaldar {database_name}", f"Se presentó un error al respaldar la base de datos.\nError: {e}")

    cursor.close()
    conn.close()
    global disco
    log(f"Todas las bases de datos han sido respaldadas.")
    disco=checar_espacio_disponible(backup_folder)
    #messagebox.showinfo("Información", "Las bases de datos han sido respaldadas correctamente.")

def probar_conexion(ip, usuario, contrasena):
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={ip};UID={usuario};PWD={contrasena}'
        conn = pyodbc.connect(conn_str)
        conn.close()
        messagebox.showinfo("Información", "Conexión exitosa")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
        
def backup_especifico(database_name, backup_folder):#Epecificar bases de datos que se desean respaldar
    crear_carpeta(backup_folder)
    password = descifrar_contrasena(config["password"], config["config_key"])
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config["server"]};UID={config["username"]};PWD={password}'
    conn = pyodbc.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()

  
    
    try:
        timestamp_inicio = datetime.datetime.now()
        log(f"Inicio de respaldo {database_name} Hora: {timestamp_inicio.strftime('%H:%M:%S')}")
        backup_file = os.path.join(backup_folder, f"{database_name}.bak")
        backup_command = f"BACKUP DATABASE [{database_name}] TO DISK='{backup_file}' WITH COMPRESSION, MEDIADESCRIPTION='{database_name} Backup';"
        cursor.execute(backup_command)
        while cursor.nextset():
            pass
        timestamp_final = datetime.datetime.now()
        diferencia = timestamp_final - timestamp_inicio
        diferencia_segundos = int(diferencia.total_seconds())
        tiempo_transcurrido = str(datetime.timedelta(seconds=diferencia_segundos))
        log(f"Respaldo completado: {backup_file} Hora: {timestamp_final.strftime('%H:%M:%S')}")
        log(f"Duración del respaldo: {tiempo_transcurrido}")
    except Exception as e:
        log(f"Error durante el respaldo de {database_name}: {e}")
        #messagebox.showerror(f"Error al respaldar {database_name}", f"Se presentó un error al respaldar la base de datos.\nError: {e}")

    cursor.close()
    conn.close()
    global disco
    log(f"La base de datos {database_name} fue respaldada con exito!.")
    disco=checar_espacio_disponible(backup_folder)

def print_server_info(backup_folder):#Informaciondel servidor
    log(f"Servidor: {config['server']}")
    log(f"Ubicación de Respaldo: {backup_folder}")
    log(f"Hora de Respaldo: {config['hora_respaldo']}")

def checar_espacio_disponible(ruta):
    uso_disco = psutil.disk_usage(ruta)
    log(f"Ruta: {ruta}")
    log(f"Total: {uso_disco.total / (1024 ** 3):.2f} GB")
    log(f"Usado: {uso_disco.used / (1024 ** 3):.2f} GB")
    log(f"Libre: {uso_disco.free / (1024 ** 3):.2f} GB")
    log(f"Porcentaje usado: {uso_disco.percent}%")
    return uso_disco

def verificaCombo(valor,ruta):
    if(valor==""):
        log(f"No se seleciono ninguna base de datos")
        messagebox.showerror(f"Error 404", f"No se seleciono ninguna base de datos")
    else:
        backup_especifico(valor,ruta)

def cancelar():
    root.quit()

def respaldo_programado(folder):
    hora_str = config['hora_respaldo']
    log(f"Hora de respaldo programado: {hora_str}")
    schedule.every().day.at(hora_str).do(backup_completo, folder)

    while True:
        schedule.run_pending()
        time.sleep(1)

def log(message):
    global log_text
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + "\n")
    log_text.config(state=tk.DISABLED)
    log_text.yview(tk.END)

if __name__ == "__main__":
    if not os.path.exists('configuracion.yaml'):
        root = tk.Tk()
        root.geometry('200x550')
        root.title("Configuración del Programa")

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

        tk.Button(root, text="Probar Conexión", command=lambda: probar_conexion(
            ip_entry.get(), usuario_entry.get(), contrasena_entry.get())).pack(pady=5)

        tk.Button(root, text="Guardar", command=lambda: guardar_configuracion(
            ip_entry.get(), usuario_entry.get(), contrasena_entry.get(), ubicacion_entry.get(), horario_entry.get())).pack(pady=20)
        tk.Button(root, text="Cancelar", command=cancelar).pack(pady=5)

        root.mainloop()
    else:
        leer_configuracion()
        root = tk.Tk()
        root.geometry('500x500')
        root.title("Respaldos")

        # Obtener fecha actual
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")

        # Crear área de texto desplazable para el registro
        log_text = scrolledtext.ScrolledText(root, state=tk.DISABLED, height=10)
        log_text.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Ruta de la carpeta de respaldo
        backup_folder = fr'{config["backup_dir"]}\{fecha_actual}\\'

        # Espacio disponible en disco
        global disco
        disco = checar_espacio_disponible(config['backup_dir'])

        # Mostrar información del servidor y espacio libre
        label = tk.Label(root, text=f"Servidor: {config['server']}", anchor="w", justify="left")
        label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # ComboBox para seleccionar la base de datos
        DBnames = ttk.Combobox(root, values=getDataBases())
        DBnames.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Botón para respaldo específico
        btn_respaldo_especifico = tk.Button(root, text="Respaldo Especifico", command=lambda: threading.Thread(target=verificaCombo, args=(DBnames.get(), backup_folder)).start())
        btn_respaldo_especifico.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Botón para iniciar respaldo completo
        btn_backup_completo = tk.Button(root, text="Iniciar Respaldo", command=lambda: threading.Thread(target=backup_completo, args=(backup_folder,)).start())
        btn_backup_completo.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # Botón para iniciar respaldo programado
        btn_respaldo_programado = tk.Button(root, text="Iniciar Respaldo Programado", command=lambda: threading.Thread(target=respaldo_programado, args=(backup_folder,)).start())
        btn_respaldo_programado.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Botón para salir de la aplicación
        btn_salir = tk.Button(root, text="Salir", command=root.quit)
        btn_salir.grid(row=5, column=0, padx=10, pady=10, sticky="w")

        # Ajustar el tamaño y la posición de los widgets usando grid
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # Ejecutar la aplicación
        root.mainloop()

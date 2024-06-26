import yaml
from cryptography.fernet import Fernet
config = {
    'server': '',
    'username': '',
    'password': '',
    'backup_dir': '',
    'hora_respaldo': ''
}
# Genera una clave para cifrar/descifrar usando Fernet
def generar_clave():
    return Fernet.generate_key()

# Función para cifrar la contraseña
def cifrar_contrasena(contrasena, clave):
    fernet = Fernet(clave)
    return fernet.encrypt(contrasena.encode())

# Función para guardar la configuración en un archivo YAML
def guardar_configuracion(ip, usuario, contrasena, ubicacion, hora):
    # Genera una clave única para cada ejecución del programa
    clave = generar_clave()
    
    # Cifra la contraseña
    contrasena_cifrada = cifrar_contrasena(contrasena, clave)
    
    # Guarda la configuración en el diccionario
    config = {
        'server': ip,
        'username': usuario,
        'password': contrasena_cifrada.decode(),  # Guarda la contraseña cifrada como string
        'backup_dir': ubicacion,
        'hora_respaldo': hora
    }
    
    # Guarda la configuración en el archivo YAML
    with open('configuracion.yaml', 'w') as file:
        yaml.dump(config, file)
    
    # Puedes retornar la clave si deseas guardarla o manejarla de alguna forma
    return clave
def leer_configuracion():
    global config
    with open('configuracion.yaml', 'r') as file:
        config = yaml.safe_load(file)



# Ejemplo de uso
ip_servidor = 'ejemplo.com'
usuario = 'usuario'
contrasena = 'mi_contrasena_secreta'
ubicacion_backup = '/ruta/backup'
hora_respaldo = '03:00'

# Guarda la configuración y obtén la clave (opcional)
guardar_configuracion(ip_servidor, usuario, contrasena, ubicacion_backup, hora_respaldo)


# Función para cargar la configuración desde el archivo YAML
def cargar_configuracion():
    with open('configuracion.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config

# Función para descifrar la contraseña
def descifrar_contrasena(contrasena_cifrada, clave):
    fernet = Fernet(clave)
    return fernet.decrypt(contrasena_cifrada.encode()).decode()

# Ejemplo de uso para cargar y utilizar la contraseña
configuracion = cargar_configuracion()
ip = configuracion['server']
usuario = configuracion['username']
contrasena_cifrada = configuracion['password']
ubicacion = configuracion['backup_dir']
hora = configuracion['hora_respaldo']

# Descifra la contraseña
contrasena_descifrada = descifrar_contrasena(contrasena_cifrada, generar_clave())
print(contrasena_descifrada)
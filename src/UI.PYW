import os
import yaml
import tkinter as tk
from tkinter import messagebox

# Función para guardar la configuración en un archivo YAML
def guardar_configuracion(ip, usuario, contrasena, ubicacion):
    config = {
        'server': ip,
        'username': usuario,
        'password': contrasena,
        'backup_dir': ubicacion
    }
    with open('configuracion.yaml', 'w') as file:
        yaml.dump(config, file)
    messagebox.showinfo("Información", "Configuración guardada correctamente")
    root.quit()

# Función que se ejecuta al cancelar
def cancelar():
    root.quit()

# Verificar si el archivo YAML de configuración existe
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

    # Crear botones de Guardar y Cancelar
    tk.Button(root, text="Guardar", command=lambda: guardar_configuracion(
        ip_entry.get(), usuario_entry.get(), contrasena_entry.get(), ubicacion_entry.get())).pack(pady=20)
    tk.Button(root, text="Cancelar", command=cancelar).pack(pady=5)

    root.mainloop()
else:
    root = tk.Tk()
    root.geometry('200x450')
    root.title("Programa Principal")

    tk.Label(root, text="Configuración cargada correctamente").pack(pady=20)
    # Aquí puedes agregar el resto de tu lógica del programa principal

    root.mainloop()

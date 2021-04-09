# Instalación manual

Para prevenir problemas de dependencias o falta de paquetes, es recomendable
actualizar los paquetes instalados y la lista de paquetes de los repositorios.

Los nuevos en Ubuntu o Debian ejecuten: `sudo apt-get update && sudo apt-get upgrade`.

Para los de ArchLinux / Manjaro, ya saben como se hace.

***

- **Instalar programas necesarios**

  - **Debian GNU/Linux / Ubuntu**

        sudo apt-get install python3 youtube-dl ffmpeg

  - **ArchLinux / Manjaro**

        sudo pacman -S python youtube-dl ffmpeg

***

- **Modulos Python**

  - **requests:**
    - Usando PIP: `sudo pip3 install requests`

  - **lxml:**
    - Usando PIP: `sudo pip3 install lxml`

  - **pycryptodome:**
    - Usando PIP: `sudo pip3 install pycryptodome`

  - **colorama**
    - Usando PIP: `sudo pip3 install colorama`

***

- **Instalación del programa**
  - **Versiones**

      Tienes dos opciones, la rama `master` y la rama `full`, ambas ramas
      siempre están actualizadas.

    1. **master**

        Solo contiene los archivos necesarios para la instalación
        y ejecución del programa, no contiene vídeos u imágenes de muestra.

            git clone --branch=master "https://github.com/Devil64-Dev/automated-dtool"

    2. **full**

        Ademas de los archivos del programa, también contiene los vídeos e imágenes de muestra, por
        lo cual el espacio que ocupa en disco en comparación con la rama `master`
        es mucho mayor.

            git clone --branch=full "https://github.com/Devil64-Dev/automated-dtool"

  - **Instegrar el programa en el sistema**

        cd automated-dtool
        sudo ln -srf dtool.py /usr/bin/automated-dtool

    Si todo resulto bien, para ejecutar el el programa solo ejecuta `automated-dtool` en la terminal.

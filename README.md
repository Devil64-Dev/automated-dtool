# Automated Download Tool

Descarga vídeos desde tus sitios web favoritos de forma automatizada para
poder verlos sin conexión desde casi cualquier lugar.

:warning: Para actualizar a esta versión deberás borrar cualquier versión anterior
de este programa, no te preocupes las descargas pendientes no se verán afectadas.

## Tabla de contenido

- [Automated Download Tool](#automated-download-tool)
  - [Tabla de contenido](#tabla-de-contenido)
  - [Información](#información)
    - [Sitios web soportados](#sitios-web-soportados)
  - [Características y requerimientos](#características-y-requerimientos)
    - [Características](#características)
    - [Requerimientos](#requerimientos)
  - [Instalación](#instalación)
  - [Uso](#uso)

## Información

Este es un script escrito en Python para automatizar las descargas de sitios web
usando [youtube-dl](https://youtube-dl.org/)
como herramienta principal para llevar a cabo las descargas.

:information_source: Este programa no está hecho para objetivos de piratería,
si ese es su caso no lo use. Los recursos descargados deberán ser guardados
localmente solo para usted, no compartidos en Internet.

:warning: Tenga en cuenta que las descargas usando este programa pueden
considerarse ilegales, use bajo su propia responsabilidad.

### Sitios web soportados

- **platzi**

## Características y requerimientos

### Características

1. Puedes descargar **rutas de aprendizaje** o **escuelas** de manera fácil.
2. No necesitas ingresar datos como usuario y contraseña en el programa.
3. Descargas ordenadas automáticamente.
4. Compatibilidad
    - Distribuciones GNU/Linux **[Probado]**
    - macOS **[No probado]**
    - Windows 10 - Por el momento solo mediante WSL **[Probado]**
5. Selección de calidad (manual/automática)
6. Subtítulos (Solo si es soportado por la página web)
7. Selección de velocidad (manual/automática)
8. Descargas en paralelo
9. Tiempo de reposo durante cada descarga (manual/automático)
10. Información sobre descargas restantes **[Pronto]**

Algunas características se explicarán más adelante.

### Requerimientos

1. Necesitas un nivel básico de conocimiento en GNU/Linux o algún sistema
Unix-like.
2. Si eres usuario de Windows necesitas seguir instrucciones extras.

NOTA: En cuanto a nivel básico me refiero a conocer el
funcionamiento de comandos como:

- `ls` - Para listar archivos.
- `cd` - Para cambiar el directorio de trabajo.
- `mkdir` - Para crear directorios.

## Instalación

Esta sección es solo para entornos Unix-like como distribuciones GNU/Linux o
macOS etc. Si eres un usuario de Windows, antes de hacer lo
que aquí se indica primero debes tener instalado y activado Ubuntu en WSL,
para aprender como o verificar que la instalación de Ubuntu en WSL
se hizo correctamente puedes revisar [esta guía](docs/wsl.es.md)

- **Instalación automática:**

  - **Instalar**

    Para realizar la instalación basta con ejecutar el siguiente comando en la terminal

        sudo apt-get install wget

        sh -c "$(wget -O- https://raw.githubusercontent.com/Devil64-Dev/automated-dtool/master/extra/install.sh)"

    El comando anterior ejecuta un script que se encarga de instalar las
    dependencias y paquetes necesarios para el correcto funcionamiento del programa.

    **Entornos admitidos**

    1. ArchLinux
    2. Manjaro
    3. Ubuntu
    4. Debian
    5. Ubuntu en WSL (Windows Subsystem for Linux)

    Si todo se instaló correctamente, solo debes ejecutar `automated-dtool`
    en la terminal para poder correr el programa.

  - **Diferencias entre versiones**

    Existen dos versiones, la versión de la rama `master` y la rama `full`
    ambas ramas siempre están actualizadas.

    1. **master** -
      Solo contiene los archivos necesarios para la instalación
      y ejecución del programa, no contiene vídeos u imágenes de muestra.

    2. **full** -
      Además de los archivos del programa, también los vídeos e imágenes
      de muestra, por lo cual el espacio que ocupa en disco en comparación con la
      rama `master` es mucho mayor.

- **Instalación manual**

    Si tienes una distribución diferente a Ubuntu, Debian, ArchLinux y Manjaro
    u ocurre un error durante la instalación automática puedes hacer el proceso
    de instalación manualmente tal como se indica en [esta guía](docs/manual_installation.es.md)

## Uso

Para ver un ejemplo de como usar

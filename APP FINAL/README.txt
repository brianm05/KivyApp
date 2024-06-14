SI EL BUILDOZER GENERA EL APK, PERO AL INSTALARLO NO SE ABRE: PUEDE QUE HALLA UN PROBLEMA EN EL 'buildozer.spec'

Puede ser que no se especificó las extenciones de los archivos complemantrios, en la linea 16:
# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,mp3

Puede ser que no se especificó bien la version de kivy, en la linea 70:
# Kivy version to use
osx.kivy_version = 1.0.9
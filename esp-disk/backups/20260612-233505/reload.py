import sys

module_names = [
    'config',
    'app.test',
    'app.modules.display',
    'app.modules.imu_sensor',
    'app.vues.boot_vue',
    'app.controller',
    'app.services.ui',
    'config',
    'main',
]


def reload_modules():
    for name in module_names:
        if name in sys.modules:
            del sys.modules[name]
        __import__(name)


reload_modules()
print("app reloaded")

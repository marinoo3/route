import sys

module_names = [
    'config',
    'app.test',
    'app.modules.display',
    'app.controller',
    'main',
]


def reload_modules():
    for name in module_names:
        if name in sys.modules:
            del sys.modules[name]
        __import__(name)


reload_modules()
print("app reloaded")


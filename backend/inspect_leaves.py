import inspect
import importlib
m = importlib.import_module('leaves.views')
print('module file:', m.__file__)
print('---SOURCE START---')
print(inspect.getsource(m))
print('---SOURCE END---')

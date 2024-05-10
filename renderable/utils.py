from fastapi import FastAPI, Depends
from fastapi.dependencies.utils import get_dependant
from fastapi.dependencies.models import Dependant
from typing import Callable, get_type_hints
from inspect import signature

app = FastAPI()

def analyze_endpoint_dependencies(endpoint_func: Callable, path: str):
    if isinstance(endpoint_func, Depends):
        # Получаем зависимость, если это объект Depends
        dependant = get_dependant(path=path, call=endpoint_func.dependency)
        endpoint_func = endpoint_func.dependency
    else:
        dependant = get_dependant(path=path, call=endpoint_func)

    sig = signature(endpoint_func)
    hints = get_type_hints(endpoint_func)
    path_params = []
    query_params = []
    
    for name, param in sig.parameters.items():
        param_dependant = next((dep for dep in dependant.dependencies if dep.name == name), None)\
            
        if "{" + name + "}" in path:
            path_params.append((name, hints[name]))
        elif param_dependant and isinstance(param_dependant, Dependant):
            if param_dependant.use_as_query_param:
                query_params.append((name, param.annotation))
            else:
                path_params.append((name, param.annotation))
        elif isinstance(param.default, Depends):
            sub_path_params, sub_query_params = analyze_endpoint_dependencies(param.default.dependency, path)
            path_params.extend(sub_path_params)
            query_params.extend(sub_query_params)
        else:
            query_params.append((name, hints[name]))

    return path_params, query_params
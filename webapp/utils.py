from functools import wraps
import time


def benchmark(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print('[*] Время выполнения: {} секунд.'.format(end - start))
        return result
    return decorated_view

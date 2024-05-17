import time


# calcular o tempo de uma função
# https://stackoverflow.com/questions/1557571/how-do-i-get-time-of-a-python-programs-execution
def profiler(fct):
    def wrapper(*args, **kw):
        start_time = time.time()
        ret = fct(*args, **kw)
        print("{} {} {} return {} in {} seconds".format(args[0].__class__.__name__,
                                                        args[0].__class__.__module__,
                                                        fct.__name__,
                                                        ret,
                                                        time.time() - start_time))
        return ret

    return wrapper

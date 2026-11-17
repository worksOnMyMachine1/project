def log_execution(func):
    def wrapper(*args, **kwargs):
        print("Starting...")
        result = func(*args, **kwargs)
        print("Finished.")
        return result
    return wrapper


def make_uppercase(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper


@log_execution
def add(a, b):
    return a + b


@make_uppercase
def greet(name):
    return f"hello {name}"


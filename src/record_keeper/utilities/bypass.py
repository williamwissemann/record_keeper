class DecoratorBypass:
    def event(self, func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

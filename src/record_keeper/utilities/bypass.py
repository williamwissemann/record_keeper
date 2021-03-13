class DecoratorBypass:
    """Creates a empty discord.py client."""
    def event(self, func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

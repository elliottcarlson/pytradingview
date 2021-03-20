class reify:
    """
    Puts the result of the method it decorates into the instance dict after the first call, effectively replacing the
    function it decorates with an instance variable
    """
    def __init__(self, fn):
        self.fn = fn


    def __get__(self, instance, owner):
        if instance is None:
            return self

        fn = self.fn
        val = fn(instance)

        setattr(instance, fn.__name__, val)

        return val

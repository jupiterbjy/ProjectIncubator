import inspect


class ChainCall:
    def __init__(self, target):
        self.target_obj = target
        self.chained_calls = []

    def __getattr__(self, item):
        # try if it's target object's
        try:
            attribute = getattr(self.target_obj, item)
        except AttributeError:
            # it's our method then
            return getattr(super(), item)

        # check if it's non method attributes (ignoring callable here)
        if not (inspect.ismethod(attribute) or inspect.iscoroutinefunction(attribute)):
            raise TypeError(f"{type(self.target_obj).__name__}.{item} is not a method.")

        self.chained_calls.append(attribute)

        # return lambda that returns this Chainable
        return lambda: self

    async def _await_calls(self):
        """Starts calling pending calls. Also checks if returning object is identical."""
        last_return = None

        for method in self.chained_calls:
            if inspect.iscoroutinefunction(method):
                last_return = await method()
            else:
                last_return = method()

            # raise if identity is wrong
            if last_return is not self.target_obj:
                raise TypeError(
                    f"Return type of {type(self.target_obj).__name__}.{method.__name__} was not a self."
                )

        return last_return

    def __await__(self):
        return self._await_calls().__await__()


def add_chain_call(tgt_class):
    """Decorate class with chain property."""

    def chain(self) -> ChainCall:
        """Start chaining following calls."""
        return ChainCall(self)

    tgt_class.chain = property(chain)

    return tgt_class

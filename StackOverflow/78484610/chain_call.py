import inspect


class ChainCall:
    def __init__(self, target):
        self.target_obj = target
        self.chained_calls = []
        self.params = []

    def __getattr__(self, item):
        # try if it's target object's
        try:
            attribute = getattr(self.target_obj, item)

        except AttributeError as err:
            try:
                # it's our method then.
                return getattr(super(), item)

            except AttributeError:
                # we catch & reraise because it otherwise returns 'super' as object name
                # which is kinda confusing and misleading.
                raise AttributeError(
                    f"'{type(self.target_obj).__name__}' object has no attribute '{item}'",
                    name=item, obj=self.target_obj
                ) from err

        # check if it's non method attributes (ignoring callable here)
        if not (inspect.ismethod(attribute) or inspect.iscoroutinefunction(attribute)):
            raise TypeError(f"'{type(self.target_obj).__name__}.{item}' is not a method.")

        self.chained_calls.append(attribute)

        # return lambda that returns this Chainable, with param
        def wrapper(*args, **kwargs) -> "ChainCall":
            self.params.append((args, kwargs))
            return self

        return wrapper

    async def _await_calls(self):
        """Starts calling pending calls.
        Also checks if returning object is identical, excluding last call."""
        last_return = None

        for idx, (method, (arg, kwarg)) in enumerate(zip(self.chained_calls, self.params), start=1):
            if inspect.iscoroutinefunction(method):
                last_return = await method(*arg, **kwarg)
            else:
                last_return = method(*arg, **kwarg)

            # raise if identity is wrong, just in case.
            # ignored on the last call.
            if (last_return is not self.target_obj) and idx != len(self.chained_calls):
                raise TypeError(
                    f"'{type(self.target_obj).__name__}.{method.__name__}' did not return self."
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

import asyncio
import inspect


class ChainCall:
    def __init__(self, target):
        self.target_obj = target
        self.chained_calls = []

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

        # return lambda that returns this Chainable
        return lambda: self

    async def _await_calls(self):
        """Starts calling pending calls.
        Also checks if returning object is identical, excluding last call."""
        last_return = None

        for idx, method in enumerate(self.chained_calls, start=1):
            if inspect.iscoroutinefunction(method):
                last_return = await method()
            else:
                last_return = method()

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


@add_chain_call
class Character:
    def __init__(self, human):
        self.human = human

    def is_human(self) -> "Character":
        print("Checking is_human!")
        if self.human:
            return self
        raise Exception("Behold! I am no human.")

    async def has_job(self) -> "Character":
        print("Checking has_job!")
        await asyncio.sleep(1)
        return self

    async def is_knight(self) -> "Character":
        print("Checking is_knight!")
        await asyncio.sleep(1)
        return self

    async def non_self_returning(self) -> str:
        print("In non_self_returning!")
        await asyncio.sleep(1)
        return "Tho facing of a ambiguity, shall refuse the temptation to guess."


async def demo():
    chara = Character(True)

    return_self = await chara.chain.is_human().has_job().is_knight()
    assert return_self is chara
    print("That character was a formidable knight who has job and is human.")

    return_str = await chara.chain.is_knight().non_self_returning()
    print("And that knight said,", return_str)


asyncio.run(demo())

# ----------- Script by ReedRGale ----------- #
# Model object to represent a boolean that times out.
# That is, over time it swaps from true to false. #


import asyncio


class TimeoutBool:
    """Class designed to change from true to false over a timeout period."""

    def __init__(self, boolean, timeout):
        self.boolean = boolean
        self.timeout = timeout

    @staticmethod
    def start(timeout):
        """Start a TimeoutBool with the specified timeout value."""
        tb = TimeoutBool(True, timeout)
        tb.timer = asyncio.ensure_future(tb._set())
        return tb

    async def _set(self, timeout=None):
        """Set a TimeoutBool timer--that is, change its value to False."""
        self.timeout = timeout if timeout else self.timeout
        await asyncio.sleep(self.timeout)
        self.boolean = False

    def reset(self, timeout=None):
        """Reset the timer on a TimeoutBool."""
        self.timer.cancel()
        self.boolean = True
        self.timer = asyncio.ensure_future(self._set(timeout))

    def stop(self):
        """If for some reason, you just want to end the timer and return false."""
        self.timer.cancel()
        self.boolean = False
        return self.boolean

    def state(self):
        """Return the current state of the TimeoutBool"""
        return self.boolean

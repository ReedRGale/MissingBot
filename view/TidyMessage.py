import asyncio
import discord
from controller import util
from model.enums import TidyMode

class TidyMessage:
    """Class designed to handle keeping long chains of commands clean."""

    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.mode = kwargs.get("mode")
        self.message = kwargs.get("message")
        self.embed = kwargs.get("embed")

    @staticmethod
    async def build(content, **kwargs):
        """Make a new TidyMessage
            id:         Is the ID for a message that already exists
            ctx:        Is the context which this TM was being created
            content:    Is the content to be put into the embed
            mode:       Is the TidyMode to use to grab default values for the Embed"""
        # Make the TM instance.
        tm = TidyMessage(mode=kwargs.get("mode"), ctx=kwargs.get("ctx"))

        # Ascertain if we're making a TM out of an existing or new Message
        if kwargs.get("id") and tm.ctx:
            tm.message = tm.ctx.get_message(kwargs.get("id"))
            return await tm.rebuild(content)
        elif tm.ctx:
            return await tm.rebuild(content)
        else:
            return "DEBUG: Insufficient information to generate TidyMessage"

    @staticmethod
    def _convert(self, content, mode):
        """Generate an Embed based on the mode given."""
        return ""

    async def rebuild(self, content, **kwargs):
        """Modifies an existing TidyMessage
            id:         Is the ID for a message that already exists
            ctx:        Is the context which this TM was being created
            content:    Is the content to be put into the embed
            mode:       Is the TidyMode to use to grab default values for the Embed"""

        # Initialize the new TidyMessage as a copy of the current one.
        tm = TidyMessage(mode=self.mode, ctx=self.ctx, message=self.message, embed=self.embed)

        # Prepare the embed.
        if isinstance(content, discord.Embed):
            tm.embed = content
        elif isinstance(content, str):
            tm.embed = TidyMessage._convert(content, self.mode)
        else:
            return "DEBUG: Invalid 'content' provided."

        # Send or edit the message.
        if isinstance(tm.message, discord.Message):
            tm.message.edit(embed=tm.embed)
        elif tm.ctx:
            tm.ctx.channel.send(embed=tm.embed)
        else:
            return "DEBUG: Invalid 'message' or 'ctx' data."

        # Delete the user command.
        tm.ctx.message.delete()

import asyncio
import discord
import random
import shlex
from model import st
from model.enums import TidyMode


class TidyMessage:
    """Class designed to handle keeping long chains of commands clean."""

    # Static Fields #
    _t_imgs = dict()    # TidyMode mapped to array of images.
    _a_imgs = dict()    # TidyMode mapped to array of images.
    _color = dict()     # TidyMode mapped to array of hex values.
    _url = ""

    def __init__(self, **kwargs):
        # Information needed on build()
        self.ctx = kwargs.get("ctx")
        self.mode = kwargs.get("mode")
        self.escape = kwargs.get("escape")
        self.title = kwargs.get("title")
        self.dest = kwargs.get("dest")

        # Information generated in rebuild()
        self.prompt = kwargs.get("prompt")
        self.message = kwargs.get("message")
        self.embed = kwargs.get("embed")

    @staticmethod
    async def build(ctx, escape, req=True, **kwargs):
        """Make a new TidyMessage
            id:         Is the ID for a message that already exists
            ctx:        Is the context within which this TM was made
            content:    Is the content to be put into the embed
            mode:       Is the TidyMode to use to grab default values for the Embed (STANDARD by default)
            dest:       Is the endpoint where messages will be sent (ctx.channel by default)"""
        # Make the TM instance.
        tm = TidyMessage(ctx=ctx, escape=escape, prompt=ctx.message)
        tm.mode = kwargs.get("mode") if kwargs.get("mode") else TidyMode.STANDARD
        tm.title = kwargs.get("title") if kwargs.get("title") else ""
        tm.dest = kwargs.get("dest") if kwargs.get("dest") else ctx.channel

        # If an 'id' exists, edit that message instead of making a new message.
        tm.message = tm.ctx.get_message(kwargs.get("id")) if kwargs.get("id") else None

        # Generate Message, Embed, and (potentially) the prompt.
        if kwargs.get("content"):
            return await tm.rebuild(req=req, **kwargs)
        else:
            return tm

    async def rebuild(self, content, req=True, **kwargs):
        """Modifies an existing TidyMessage
            prompt:     Is the message or reaction which invoked this TM
            content:    Is the content to be put into the embed
            mode:       Is the TidyMode to use to grab default values for the Embed
            req:        Bool:  if we're doing a request or not (content is a the request message, in this case)
            repeat:     Repeat string for requests--if proper information isn't gleaned, repeats
            checks:     A set of checks for requests--allows for internal string checking for important data"""
        # Initialize the new TidyMessage as a copy of the current one.
        tm = TidyMessage(ctx=self.ctx,
                         mode=self.mode,
                         escape=self.escape,
                         title=self.title,
                         dest=self.dest,
                         prompt=self.prompt,
                         message=self.message,
                         embed=self.embed)

        # Edit fields if any changes.
        if kwargs.get("mode"):
            tm.mode = kwargs.get("mode")
        if kwargs.get("title"):
            tm.title = kwargs.get("title")

        # Prepare the embed.
        if isinstance(content, discord.Embed):
            tm.embed = content
        elif isinstance(content, str):
            tm.embed = await tm._convert(content, tm.mode)
        else:
            return await tm.rebuild(st.ERR_INVALID_TM_CONTENT, req=False, mode=TidyMode.WARNING)

        # If we hit an error, end immediately.
        if isinstance(tm.embed, TidyMessage):
            return tm.embed

        # Delete the user command.
        try:
            if not isinstance(self.dest, discord.DMChannel):
                await self.prompt.delete()
        except discord.errors.NotFound:
            pass  # If it's not there to be deleted we already did our job.

        if req:  # If a request, ask it.
            tm = await tm._req(content, tm, **kwargs)
            if tm == self.escape:
                return self.escape
        else:  # Otherwise, send the message.
            if isinstance(tm.message, discord.Message) and not isinstance(self.dest, discord.DMChannel):
                await tm.message.delete()
            tm.message = await tm.dest.send(embed=tm.embed)

        return tm

    async def _convert(self, content, mode):
        """Convert the 'content' into an Embed based on the mode given."""

        # Change mode to a hashable type.
        mode = mode.value

        # Select the images and color for the embed.
        t_url = random.choice(TidyMessage._t_imgs.get(mode)) if TidyMessage._t_imgs.get(mode) else None
        a_url = random.choice(TidyMessage._a_imgs.get(mode)) if TidyMessage._a_imgs.get(mode) else None
        color = TidyMessage._color.get(mode)

        # Check to make sure this will work.
        if not t_url or not a_url or not color:
            return await TidyMessage.rebuild(st.ERR_INVALID_TIDYMODE, req=False, mode=TidyMode.WARNING)

        # Make and return the embed.
        emb = discord.Embed(title=self.title,
                            description=content,
                            color=color)
        emb.set_thumbnail(url=t_url)
        emb.set_author(name=self.ctx.bot.user.name,
                       url=TidyMessage._url,
                       icon_url=a_url)
        return emb

    async def _req(self, content, tm, **kwargs):
        """Ask a request for the user and return that request as a list of inputs or return an escape character."""
        again, unchecked, repeat = False, True, ""

        while unchecked:
            # Ask the request.
            tm = await tm.rebuild(content if not again else repeat + " " + content, req=False)

            # Define check
            a = self.prompt.author
            c = self.prompt.channel

            def check(resp):
                return resp.author == a and resp.channel == c

            # Wait for response.
            rsp = await self.ctx.bot.wait_for("message", check=check)
            if rsp.content.lower() == self.escape:
                return self.escape

            # Set the response as the new prompt.
            tm.prompt = rsp

            # Check the information.
            req_checks = kwargs.get("checks")
            if req_checks:
                for c in req_checks:
                    c_val = c(*shlex.split(rsp.content))
                    unchecked = False
                    if isinstance(c_val, str):
                        unchecked, repeat, again = c_val, c_val, True
                        break
            else:
                unchecked = False

        return tm

    @staticmethod
    def set_t_imgs(mode, imgs):
        TidyMessage._t_imgs[mode] = imgs

    @staticmethod
    def set_a_imgs(mode, imgs):
        TidyMessage._a_imgs[mode] = imgs

    @staticmethod
    def set_color(mode, color):
        TidyMessage._color[mode] = color

    @staticmethod
    def set_url(url):
        TidyMessage._url = url

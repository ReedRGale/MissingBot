# ----------- Script by ReedRGale ----------- #
# View object to simplify sending standard embeds. #

import asyncio
import discord
import random
import shlex
import os
import time
import uuid
from asyncio import tasks
from view.TidySecretary import TidySecretary
from model import st
from model.enums import TidyMode


class TidyMessage:
    """Class designed to handle keeping long chains of commands clean, contain generalized command buttons
    and to log information for later usage.

    ::Use Cases::

    General:            tm = await TidyMessage.build(ctx, {escape character}, {error on escape},
                                                     content={content of first TM},
                                                     checks=[{checks}])

    Out-of-Channel:     tm = await TidyMessage.build(ctx, {escape character}, {error on escape},
                                                     content={content of first TM},
                                                     dest={destination channel},
                                                     checks=[{checks}])

    Change Focus:       tm = await TidyMessage.build(ctx, {escape character}, {error on escape},
                                                     content={content of first TM},
                                                     focus={user whose messages are prompts},
                                                     checks=[{checks}])"""

    # Static Fields #
    _t_imgs = dict()    # TidyMode mapped to array of images.
    _a_imgs = dict()    # TidyMode mapped to array of images.
    _color = dict()     # TidyMode mapped to array of hex values.
    _url = ""
    _pending = {}
    _req_lock = {}

    def __init__(self, **kwargs):
        # Information needed on build()
        self.ctx = kwargs.get("ctx")                    # Needed for the bot.wait_for() in req
        self.mode = kwargs.get("mode")                  # Value of the TidyMode that determines the embed created
        self.esc = kwargs.get("esc")                    # Escape string that exits req
        self.esc_m = kwargs.get("esc_m")                # What to say if escaped
        self.title = kwargs.get("title")                # Title of the embed, if given
        self.dest = kwargs.get("dest")                  # The destination of the message
        self.focus = kwargs.get("focus")                # The member who we're waiting for a response from
        self.editable = kwargs.get("editable")          # Whether the data can be edited later or not
        self.req = kwargs.get("req")                    # Whether this TidyMessage is looking for a response or not

        # Information generated in rebuild()
        self.prompt = kwargs.get("prompt")          # The message that prompted this TidyMessage
        self.message = kwargs.get("message")        # The message that contains this TidyMessage's embed
        self.embed = kwargs.get("embed")            # The embed created through this TidyMessage
        self.page = kwargs.get("page")              # The index of the TidyPage we're using
        self.path = kwargs.get("path")              # The location of the TidyPage record
        self.checks = kwargs.get("checks")          # List of functions used to check prompt legitimacy
        self.req_lock = kwargs.get("req_lock")      # If a request loop is happening already or not
        self.caller = kwargs.get("caller")          # The function calling the build or rebuild
        self.req_c = kwargs.get("req_c")            # The content for the request

    @staticmethod
    async def build(ctx, esc, esc_m, req=True, editable=False, **kwargs):
        """Make a new TidyMessage"""
        # Make the TM instance.
        tm = TidyMessage(ctx=ctx, esc=esc, esc_m=esc_m, prompt=ctx.message)
        tm.req = req
        tm.editable = editable
        tm.dest = kwargs.get("dest") if kwargs.get("dest") else ctx.channel
        tm.focus = kwargs.get("focus") if kwargs.get("focus") else ctx.message.author

        # Generate Message, Embed, and (potentially) the prompt.
        if kwargs.get("path"):      # If information already exists pull up the log.
            log = await TidySecretary.retrieve(kwargs.get("path"))
            return await tm.rebuild(req=req,
                                    content=log.get(st.FLD_CNTT),
                                    title=log.get(st.FLD_TTLE),
                                    mode=log.get(st.FLD_MODE),
                                    page=log.get(st.FLD_PAGE),
                                    editable=log.get(st.FLD_EDTBL),
                                    **kwargs)
        if kwargs.get("content"):   # If information doesn't already exist, log it.
            # Prepare data.
            g = ctx.guild.id                                                # Guild
            c = tm.dest.category_id if tm.dest.category_id else tm.dest.id  # Canon
            m = tm.focus.id                                                 # Member
            f = ctx.command.name if ctx.command else st.COMM_UNF            # JSON File
            i = 0                                                           # Name Snowflakifier
            if os.path.exists(st.CANON_P.format(g, c)):  # If the category is a canon move to canon command logs.
                while os.path.exists(st.MEM_COMMAND_C_LOG_P.format(g, c, m, f + str(i))):
                    i += 1  # Get to a unique name value in the most beautiful way I can bother to write.
                tm.path = st.MEM_COMMAND_C_LOG_P.format(g, c, m, f + str(i))
            else:  # Otherwise, move to the general command logs.
                while os.path.exists(st.MEM_COMMAND_G_LOG_P.format(g, m, f + str(i))):
                    i += 1  # Get to a unique name value in the most beautiful way I can bother to write.
                tm.path = st.MEM_COMMAND_G_LOG_P.format(g, m, f + str(i))
            return await tm.rebuild(req=req, **kwargs)
        else:
            return tm

    async def rebuild(self, content, req=True, editable=False, **kwargs):
        """Modifies an existing TidyMessage"""
        # Initialize the new TidyMessage as a copy of the current one.
        tm = self.copy()

        # Save instance of the previous destination in case it changes.
        prev_dest = tm.dest

        # Fields reset each call.
        tm.req = req
        tm.editable = editable
        tm.checks = kwargs.get("checks")    # None if nothing to replace it.
        tm.page = kwargs.get("page")        # None if nothing to replace it.
        tm.caller = kwargs.get("caller") if kwargs.get("caller") else "rebuild"
        tm.title = kwargs.get("title") if kwargs.get("title") else ""
        tm.req_c = kwargs.get("req_c") if kwargs.get("req_c") else content

        # Fields that change on request.
        tm.dest = kwargs.get("dest") if kwargs.get("dest") else tm.dest
        tm.focus = kwargs.get("focus") if kwargs.get("focus") else tm.focus

        # Cancel all other pending tasks.
        tm._cancel()

        # Store and delete prompt data.
        await tm._process_prompt()

        # Needs to be set later, because the prompt will always set the mode to 'PROMPT.'
        if kwargs.get("mode"):
            if isinstance(kwargs.get("mode"), int):
                tm.mode = kwargs.get("mode")
            else:
                tm.mode = kwargs.get("mode").value
        else:
            tm.mode = TidyMode.STANDARD.value

        # Generate and store message data.
        await tm._process_message(content, prev_dest)

        # Set all tasks in motion.
        await tm._tidy_tasks()

        # If applicable, lock until request complete.
        tm = await tm._req_loop()

        return tm

    # TidyMessage Parts #

    def copy(self):
        """Returns a copy of the given TidyMessage."""
        return TidyMessage(ctx=self.ctx,
                           mode=self.mode,
                           esc=self.esc,
                           esc_m=self.esc_m,
                           title=self.title,
                           dest=self.dest,
                           focus=self.focus,
                           editable=self.editable,
                           prompt=self.prompt,
                           message=self.message,
                           embed=self.embed,
                           page=self.page,
                           path=self.path,
                           req=self.req,
                           checks=self.checks,
                           caller=self.caller,
                           req_c=self.req_c,
                           req_lock=self.req_lock)

    def _cancel(self):
        """Cancel and remove all tasks that aren't the caller."""
        if TidyMessage._pending.get(self.ctx.author.id):
            copy = set(TidyMessage._pending.get(self.ctx.author.id))
            for t in TidyMessage._pending.get(self.ctx.author.id):
                if t._coro.__name__ + t.uid != self.caller:
                    t.cancel()
                    copy.remove(t)
            TidyMessage._pending[self.ctx.author.id] = set(copy)

    async def _process_prompt(self):
        """Method designed to collect prompt data and store it as a part of the TidyMessage chain."""
        # Prepare the embed for the prompt.
        if isinstance(self.prompt.content, str):
            self.embed = await self._convert(self.prompt.content, TidyMode.PROMPT.value)
            self.mode = TidyMode.PROMPT.value
        else:
            return await self.rebuild(st.ERR_INVALID_TM_CONTENT, req=False, mode=TidyMode.WARNING)

        # If we hit an error, end immediately.
        if isinstance(self.embed, TidyMessage):
            return self.embed

        # Hand prompt TidyMessage to TidySecretary to store.
        if not self.page:
            await TidySecretary.store(self, prompt=True)

        # Delete the user command.
        try:
            if not isinstance(self.dest, discord.DMChannel):
                await self.prompt.delete()
        except discord.errors.NotFound:
            pass  # If it's not there to be deleted we already did our job.

    async def _process_message(self, content, prev_dest):
        """Method designed to create the TidyMessage's message and store it as part of the TidyMessage chain."""
        # Prepare the embed for the message.
        if isinstance(content, discord.Embed):
            self.embed = content
        elif isinstance(content, str):
            self.embed = await self._convert(content, self.mode)
        else:
            return await self.rebuild(st.ERR_INVALID_TM_CONTENT, req=False, mode=TidyMode.WARNING)

        # If we hit an error, end immediately.
        if isinstance(self.embed, TidyMessage):
            return self.embed

        # Send the message.
        try:
            if isinstance(self.message, discord.Message) and not isinstance(prev_dest, discord.DMChannel):
                await self.message.delete()
        except discord.errors.NotFound:
            pass  # If it's not there to be deleted we already did our job.
        self.message = await self.dest.send(embed=self.embed)

        # Hand content TidyMessage to TidySecretary to store.
        if not self.page:
            await TidySecretary.store(self)

    async def _tidy_tasks(self):
        """Method to set all tasks in motion while not holding up anything."""
        # Prepare list of potential tasks.
        potential_tasks = [TidyMessage._last_g,
                           TidyMessage._req_g,
                           TidyMessage._prev_g,
                           TidyMessage._next_g,
                           TidyMessage._first_g]

        # For each potential task, check if it generates a task we need to do.
        todo, uid = list(), str(uuid.uuid4())
        for t in potential_tasks:
            task = await t(self, uid)  # Each check factory will know when it should or shouldn't run.
            if task:
                todo.append(task)

        # Make static pending tasks entry if none.
        if not TidyMessage._pending.get(self.ctx.author.id):
            TidyMessage._pending[self.ctx.author.id] = set()

        # Set all tasks in motion.
        for t in todo:
            TidyMessage._pending.get(self.ctx.author.id).add(asyncio.ensure_future(t()))
            time.sleep(0.05)

        # Add the uid to the task.
        for t in TidyMessage._pending.get(self.ctx.author.id):
            if not hasattr(t, "uid"):
                t.uid = uid

    async def _req_loop(self):
        """Method designed to loop through the req; works in tandem with other tasks that are running."""
        # Initialize the new TidyMessage as a copy of the current one.
        tm = TidyMessage.copy(self)

        # If a request, wait for a request to come out.
        while not TidyMessage._req_lock.get(tm.ctx.author.id) and tm.req:
            # Lock the loop.
            TidyMessage._req_lock[tm.ctx.author.id] = True

            # Await pending for the req task.
            done, processing = await tasks.wait(TidyMessage._pending.get(tm.ctx.author.id),
                                                return_when=asyncio.FIRST_COMPLETED)

            # Unlock by default, now that we've received tasks.
            TidyMessage._req_lock[tm.ctx.author.id] = False

            # Process results.
            for d in done:
                # Check if escaped or cancelled.
                try:
                    if d.result().prompt.content.lower() == tm.esc:
                        # Remove all the stuff because we don't care now that we escaped.
                        del(TidyMessage._pending[tm.ctx.author.id])
                        return d.result()
                except asyncio.CancelledError:
                    continue  # Move on to the next task if we're reading a cancelled one.

                # Reassign the TidyMessage.
                tm = d.result()

                # Record if the coro is the caller. If it is, this must be the req value.
                tm._child_not_caller = d._coro.__name__ + d.uid != tm.caller

                # Unlock, remove task and use information to determine exit point.
                TidyMessage._pending.get(tm.ctx.author.id).remove(d)

            if hasattr(tm, "_child_not_caller") and tm._child_not_caller:
                break
        return tm

    async def _convert(self, content, mode):
        """Convert the 'content' into an Embed based on the mode given."""

        # Select the images and color for the embed.
        t_url = TidyMessage._t_imgs.get(mode)
        a_url = TidyMessage._a_imgs.get(mode)
        color = TidyMessage._color.get(mode)

        # If the values are a constant list, pick a random one.
        if isinstance(t_url, list):
            t_url = random.choice(t_url)
        if isinstance(a_url, list):
            a_url = random.choice(a_url)
        if isinstance(color, list):
            color = random.choice(color)

        # If the values vary, ascertain their current state.
        if callable(t_url):
            t_url = t_url(self)
        if callable(a_url):
            a_url = a_url(self)
        if callable(color):
            color = color(self)

        # Check to make sure this will work.
        if not t_url or not a_url or not color:
            return await TidyMessage.rebuild(st.ERR_INVALID_TIDYMODE, req=False, mode=TidyMode.WARNING)

        # Make and return the embed.
        emb = discord.Embed(title=self.title,
                            description=content,
                            color=color)
        emb.set_thumbnail(url=t_url)
        emb.set_author(name=self.ctx.message.author,
                       url=TidyMessage._url,
                       icon_url=a_url)
        return emb

    async def remove_button(self, r):
        """Remove a reaction-button from a button generator when cancelled."""
        # Remove the button.
        bot_m = None
        for m in self.ctx.bot.get_all_members():
            if m.id == self.ctx.bot.owner_id:
                bot_m = m
                break
        try:
            await self.message.remove_reaction(r, bot_m)
        except discord.errors.NotFound:
            pass

        # Throw the error so we know this is being cancelled.
        raise asyncio.CancelledError()

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

    # Task Generators #

    @staticmethod
    async def _req_g(tm, uid):
        """A generator that checks if the TM is waiting for a response.
        If so, returns a check that waits for a user response."""
        task = None
        if tm.req:
            async def req():
                # Initialize the new TidyMessage as a copy of the current one.
                tc = tm.copy()

                # Define check
                def check(rsp):
                    return rsp.author == tc.focus and rsp.channel == tc.dest

                # Wait for response.
                tc.prompt = await tc.ctx.bot.wait_for("message", check=check)

                # Escape received, exit command.
                if tc.prompt.content.lower() == tc.esc:
                    return await tc.rebuild(tm.esc_m, page=None, title='', req=False,
                                            editable=tm.editable, caller=req.__name__ + uid)

                # Check the information.
                if tc.checks:
                    for c in tc.checks:
                        err = c(*shlex.split(tc.prompt.content))
                        if isinstance(err, str):
                            tc = await tc.rebuild(err + " " + tm.req_c, editable=tm.editable,
                                                  req=tm.req, req_c=tm.req_c, checks=tm.checks,
                                                  caller=req.__name__ + uid)
                            break
                return tc
            task = req
        return task

    @staticmethod
    async def _prev_g(tm, uid):
        """A generator that checks if the TM has a previous log instance to go back to.
        If so, adds the :arrow_backward: reaction and checks whether it's pressed or not."""
        task = None

        # Get and analyze log.
        if tm.page:
            prev_page = int(tm.page) - 1
        else:
            curr_page = await TidySecretary.retrieve(tm.path)
            prev_page = int(curr_page.get(st.FLD_PAGE)) - 1

        if prev_page >= 0:
            async def prev():
                # Initialize the new TidyMessage as a copy of the current one.
                tc = tm.copy()

                # Add the button.
                await tc.message.add_reaction('◀')

                # Define check
                def check(r, u):
                    return u == tc.focus and r.emoji == '◀'

                # Wait for a response.
                try:
                    await tc.ctx.bot.wait_for('reaction_add', check=check)
                except asyncio.CancelledError:
                    await tc.remove_button('◀')

                # Once this is the reaction we're looking for, rebuild the page.
                history = await TidySecretary.retrieve(tm.path, whole=True)
                page = history[str(int(tm.page) - 1)] if tm.page else history[str(prev_page)]
                tc = await tc.rebuild(page.get(st.FLD_CNTT), title=page.get(st.FLD_TTLE),
                                      mode=page.get(st.FLD_MODE), page=page.get(st.FLD_PAGE),
                                      path=page.get(st.FLD_PATH), editable=page.get(st.FLD_EDTBL),
                                      req=tm.req, req_c=tm.req_c, checks=tm.checks,
                                      caller=prev.__name__ + uid)
                return tc
            task = prev
        return task

    @staticmethod
    async def _next_g(tm, uid):
        """A generator that checks if the TM has a later log instance to go forward to.
        If so, adds the :arrow_forward: reaction and checks whether it's pressed or not."""
        task = None

        # Get and analyze log.
        next_page = None
        if tm.page:
            next_page = int(tm.page) + 1
        top_page = int((await TidySecretary.retrieve(tm.path)).get(st.FLD_PAGE))

        if next_page and next_page <= top_page:
            async def next():
                # Initialize the new TidyMessage as a copy of the current one.
                tc = tm.copy()

                # Add the button.
                await tc.message.add_reaction('▶')

                # Define check
                def check(r, u):
                    return u == tc.focus and r.emoji == '▶'

                # Wait for a response.
                try:
                    await tc.ctx.bot.wait_for('reaction_add', check=check)
                except asyncio.CancelledError:
                    await tc.remove_button('◀')

                # Once this is the reaction we're looking for, rebuild the page.
                history = await TidySecretary.retrieve(tm.path, whole=True)
                page = history[str(next_page)]
                tc = await tc.rebuild(page.get(st.FLD_CNTT), title=page.get(st.FLD_TTLE),
                                      mode=page.get(st.FLD_MODE), page=page.get(st.FLD_PAGE),
                                      path=page.get(st.FLD_PATH), editable=page.get(st.FLD_EDTBL),
                                      req=tm.req, req_c=tm.req_c, checks=tm.checks,
                                      caller=next.__name__ + uid)
                return tc
            task = next
        return task

    @staticmethod
    async def _first_g(tm, uid):
        """A generator that checks if the TM has a later log instance to go forward to.
        If so, adds the :track_next: reaction and checks whether it's pressed or not.
        If so, take the user to the most recent page."""
        task = None

        # Get and analyze log.
        next_page = None
        if tm.page:
            next_page = int(tm.page) + 1
        top_page = int((await TidySecretary.retrieve(tm.path)).get(st.FLD_PAGE))

        if next_page and next_page <= top_page:
            async def first():
                # Initialize the new TidyMessage as a copy of the current one.
                tc = tm.copy()

                # Add the button.
                await tc.message.add_reaction('⏭')

                # Define check
                def check(r, u):
                    return u == tc.focus and r.emoji == '⏭'

                # Wait for a response.
                try:
                    await tc.ctx.bot.wait_for('reaction_add', check=check)
                except asyncio.CancelledError:
                    await tc.remove_button('⏭')

                # Once this is the reaction we're looking for, rebuild the page.
                page = await TidySecretary.retrieve(tm.path)
                tc = await tc.rebuild(page.get(st.FLD_CNTT), title=page.get(st.FLD_TTLE),
                                      mode=page.get(st.FLD_MODE), page=page.get(st.FLD_PAGE),
                                      path=page.get(st.FLD_PATH), editable=page.get(st.FLD_EDTBL),
                                      req=tm.req, req_c=tm.req_c, checks=tm.checks,
                                      caller=first.__name__ + uid)
                return tc
            task = first
        return task

    @staticmethod
    async def _last_g(tm, uid):
        """A generator that checks if the TM has a previous log instance to go back to.
        If so, adds the ⏮ reaction and checks whether it's pressed or not. If so, takes
        the user to the first page."""
        task = None

        # Get and analyze log.
        if tm.page:
            prev_page = int(tm.page) - 1
        else:
            curr_page = await TidySecretary.retrieve(tm.path)
            prev_page = int(curr_page.get(st.FLD_PAGE)) - 1

        if prev_page >= 0:
            async def last():
                # Initialize the new TidyMessage as a copy of the current one.
                tc = tm.copy()

                # Add the button.
                await tc.message.add_reaction('⏮')

                # Define check
                def check(r, u):
                    return u == tc.focus and r.emoji == '⏮'

                # Wait for a response.
                try:
                    await tc.ctx.bot.wait_for('reaction_add', check=check)
                except asyncio.CancelledError:
                    await tc.remove_button('⏮')

                # Once this is the reaction we're looking for, rebuild the page.
                history = await TidySecretary.retrieve(tm.path, whole=True)
                page = history['0']
                tc = await tc.rebuild(page.get(st.FLD_CNTT), title=page.get(st.FLD_TTLE),
                                      mode=page.get(st.FLD_MODE), page=page.get(st.FLD_PAGE),
                                      path=page.get(st.FLD_PATH), editable=page.get(st.FLD_EDTBL),
                                      req=tm.req, req_c=tm.req_c, checks=tm.checks,
                                      caller=last.__name__ + uid)
                return tc
            task = last
        return task

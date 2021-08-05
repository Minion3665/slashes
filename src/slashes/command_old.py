import enum

import aiohttp

import discord
from discord.ext import commands

argument_types = {
    str: 3,
    int: 4,
    bool: 5,
    discord.User: 6,
    discord.abc.GuildChannel: 7,
    discord.role: 8,
}


class Command(commands.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guild_id = kwargs.get('guild_id')
        self.description = kwargs.get('description', 'No description set')
        self.auto_ack = kwargs.get('auto_ack', True)

    @staticmethod
    async def ack(ctx, swallow=False):
        # noinspection PyProtectedMember
        token = ctx._reply_token
        # noinspection PyProtectedMember
        interaction_id = ctx._interaction_id
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://discord.com/api/v8/interactions/{interaction_id}/{token}/callback",
                                    json={'type': 2 if swallow else 5}) as resp:
                pass

    async def invoke(self, ctx):
        if self.auto_ack:
            await self.ack(ctx)
        return await super().invoke(ctx)

    # noinspection PyProtectedMember
    async def transform(self, ctx, param):
        required = param.default is param.empty
        converter = self._get_converter(param)
        try:
            param_value = ctx._args[param.name]['value']
        except KeyError:
            if not required:
                return param.default
            else:
                raise commands.MissingRequiredArgument(param)
        if converter == discord.User:
            return ctx.bot.get_user(param_value) or await ctx.bot.fetch_user(param_value)
        elif converter == discord.abc.GuildChannel:
            return ctx.bot.get_channel(param_value)
        elif converter == discord.Role and ctx.guild:
            return ctx.guild.get_role(converter)
        elif converter in [bool, int, str]:
            return param_value
        elif issubclass(converter, enum.Enum):
            # noinspection PyArgumentList
            return converter(param_value)
        elif type(converter) is commands.Greedy:
            raise TypeError("Slash commands do not support greedy converters")
        else:
            return await self.do_conversion(ctx, converter, param_value, param)

    def get_params(self):
        iterator = iter(self.params.items())

        if self.cog is not None:
            # we have 'self' as the first parameter so just advance
            # the iterator and resume parsing
            try:
                next(iterator)
            except StopIteration:
                fmt = 'Callback for {0.name} command is missing "self" parameter.'
                raise discord.ClientException(fmt.format(self))

        # next we have the 'ctx' as the next parameter
        try:
            next(iterator)
        except StopIteration:
            fmt = 'Callback for {0.name} command is missing "ctx" parameter.'
            raise discord.ClientException(fmt.format(self))

        return iterator

    async def _parse_arguments(self, ctx):
        ctx.args = [ctx] if self.cog is None else [self.cog, ctx]
        ctx.kwargs = {}
        args = ctx.args
        kwargs = ctx.kwargs

        view = ctx.view

        iterator = self.get_params()

        for name, param in iterator:
            if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.POSITIONAL_ONLY:
                transformed = await self.transform(ctx, param)
                args.append(transformed)
            else:
                raise TypeError(f"Programmer error in {self.name}: Keyword only parameters or starred arg parameters "
                                f"are invalid in slash commands")

        if not self.ignore_extra and not view.eof:
            raise commands.TooManyArguments('Programmer error: too many arguments passed to slash command '
                                            + self.qualified_name)

import enum
import json
import typing
import zlib

import aiohttp

from discord.ext import commands
from . import context
from . import errors
from . import command as slash_command


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_slash_commands = {}
        self._connection.parsers['INTERACTION_CREATE'] = self.parse_interaction_create

    def run(self, *args, **kwargs):
        self.loop.create_task(self.register_commands())
        return super().run(*args, **kwargs)

    def get_context(self, message, *, cls=context.Context):
        return super().get_context(message, cls=cls)

    def parse_interaction_create(self, data):
        self.dispatch('raw_interaction_create', data)

    async def on_raw_interaction_create(self, data):
        ctx = context.Context.from_slash(self, data)
        await self.invoke(ctx)

    def add_slash_command(self, command):
        if not isinstance(command, commands.Command):
            raise TypeError('The command passed must be a subclass of Command')

        if isinstance(self, commands.Command):
            command.parent = self

        if command.name in self.all_slash_commands:
            raise errors.SlashCommandRegistrationError(command.name)

        self.all_slash_commands[command.name] = command
        for alias in command.aliases:
            if alias in self.all_slash_commands:
                self.remove_command(command.name)
                raise errors.SlashCommandRegistrationError(alias, alias_conflict=True)
            self.all_slash_commands[alias] = command

    def slash_command(self, *args, **kwargs):
        """
        A decorator that adds a slash command to the bot
        """

        def decorator(func):
            kwargs.setdefault('parent', self)

            result = commands.command(cls=slash_command.Command, *args, **kwargs)(func)
            self.add_slash_command(result)
            return result

        return decorator

    async def register_commands(self):
        await self.wait_until_ready()
        slash_commands = {}

        for command in self.all_slash_commands.values():
            slash_commands[command.guild_id] = slash_commands.get(command.guild_id, {})
            if slash_commands[command.guild_id].get(command.name):
                raise commands.CommandRegistrationError(command.name)

            args = []
            for name, param in command.get_params():
                if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.POSITIONAL_ONLY:
                    required = param.default is param.empty
                    # noinspection PyProtectedMember
                    converter = command._get_converter(param)
                    param_type = slash_command.argument_types.get(converter, 3)  # The default converter is a string
                    # converter. In particular, enums will be converted with string converters *even if they are int
                    # enums*

                    arg = {
                        "name": name,
                        "description": 'No description set',
                        "type": param_type,
                        "required": required,
                    }

                    if issubclass(converter, enum.Enum):
                        arg["choices"] = [
                            {
                                "name": choice.name,
                                "value": choice.value,
                            } for choice in converter
                        ]

                    args.append(arg)
                else:
                    raise TypeError(
                        f"Programmer error in {command.name}: Keyword only parameters or starred arg parameters "
                        f"are invalid in slash commands")

            slash_commands[command.guild_id][command.name] = {
                'name': command.name,
                'description': command.description,
                'options': args
            }

        async with aiohttp.ClientSession() as session:
            for guild_id, command_list in slash_commands.items():
                async with session.put(f"https://discord.com/api/v8/applications/{self.user.id}"
                                       f"{f'/guilds/{guild_id}' if guild_id else ''}/commands",
                                       json=list(command_list.values()),
                                       headers={'Authorization': f'Bot {self._connection.http.token}'}) as resp:
                    print(f"{resp.status} when registering {guild_id or 'global'} commands"
                          f"{(f': ' + await resp.text()) if resp.status != 200 else ''}")


class AutoShardedBot(Bot, commands.AutoShardedBot):
    pass

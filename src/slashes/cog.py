from discord.ext import commands
from . import command_context


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # noinspection PyProtectedMember
        # Accesses the parsers, hooking into discord.py's gateway
        self.bot._connection.parsers['INTERACTION_CREATE'] = self.parse_interaction_create

    def parse_interaction_create(self, data):
        self.bot.dispatch('raw_interaction_create', data)
        if data['type'] == 2:  # Slash command
            self.parse_slash_command(data)

    def parse_slash_command(self, data):
        context = command_context.CommandContext(self.bot, data)
        self.bot.dispatch('slash_command_execute', context)

    @commands.Cog.listener()
    async def on_raw_interaction_create(self, data):
        pass

    async def on_slash_command_execute(self, data):
        pass

    async def on_button_press(self, data):
        pass

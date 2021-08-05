import discord
from discord.ext import commands
from discord.ext.commands.view import StringView


class Message(discord.Message):
    @classmethod
    def from_slash(cls, bot, slash_data):
        # Messages are initialised with a data dictionary, let's create one now
        # noinspection PyDictCreation
        message_data = {}
        # Let's add attributes that we *know for sure* to be constant across slash commands
        message_data['tts'] = False  # Slash commands *cannot* have TTS
        message_data['embeds'] = []  # Slash commands can't have embeds
        message_data['type'] = 'default'  # In this lib, slash commands are always default commands
        message_data['id'] = -1  # In this lib, *there are no IDs given with slash command messages, only with the
        # context*. This is important as despite slash commands technically having IDs they are not message IDs and
        # cannot be treated as such (for example in getting messages). Instead, each slash command message will have an
        # ID of None. We've set an ID of -1 here because we need it to initialise the message, we will later replace it
        message_data['attachments'] = []  # Commands cannot have attachments
        message_data['edited_timestamp'] = None  # Commands cannot be edited
        message_data['pinned'] = False  # Commands cannot be pinned
        message_data['mention_everyone'] = False  # Commands cannot mention *anyone*
        message_data['mentions'] = []
        message_data['mention_roles'] = []
        message_data['call'] = None
        message_data['flags'] = 0

        channel = bot.get_channel(int(slash_data['channel_id']))  # Channels are *always* cached, so we don't need to
        # fetch a channel here

        # noinspection PyProtectedMember
        state = bot._connection  # The state is the bot's connection state

        # Alright, now for the hard bit...
        name = slash_data["data"]["name"]
        args = ' '.join(f"{opt['name']}:{opt['value']}" for opt in slash_data['data']['options'])
        message_data['content'] = f'/{name} {args}'

        message_data['author'] = slash_data.get('member', {}).get('user') or slash_data.get('user')

        return cls(state=state, channel=channel, data=message_data)


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def from_slash(cls, bot, slash_data):
        message = Message.from_slash(bot, slash_data)

        view = StringView(message.content)
        ctx = cls(prefix=None, view=view, bot=bot, message=message)

        # noinspection PyProtectedMember
        if bot._skip_check(message.author.id, bot.user.id):
            return ctx

        prefix = '/'
        invoked_prefix = prefix

        view.skip_string(prefix)

        if bot.strip_after_prefix:
            view.skip_ws()

        invoker = view.get_word()
        ctx.invoked_with = invoker
        ctx.prefix = invoked_prefix
        ctx.command = bot.all_slash_commands.get(invoker)

        ctx._args = {arg['name']: arg for arg in slash_data['data']['options']}
        ctx._reply_token = slash_data['token']
        ctx._interaction_id = slash_data['id']
        return ctx

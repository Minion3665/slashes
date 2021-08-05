from discord.mixins import Hashable
import discord.abc
from abc import ABC
from . import command


class CommandContext(discord.abc.Messageable, ABC, Hashable):
    def __init__(self, bot, data):
        self.bot = bot

        self.version = data['version']

        self.token = data['token']

        self.id = data['id']

        self.channel = bot.get_channel(int(data['channel_id']))
        self.guild = self.channel.guild if self.channel is not None else bot.get_guild(int(data.get('guild_id', -1)))

        if member := data.get('member', None):
            # noinspection PyProtectedMember
            # gets the member from the data sent from the gateway,
            # uses private member bot._connection as the member state
            self.author = discord.Member(data=member, guild=self.guild, state=bot._connection)
        else:
            # noinspection PyProtectedMember
            # if there wasn't a member, we must have a user instead
            # also uses private member bot._connection as the member state
            self.author = discord.User(state=bot._connection, data=data['user'])

        self.command = command.Command.from_gateway_data(data['data'])
        self.options = command.Command.convert_gateway_parameters(data['data']['options'])

    async def _get_channel(self):
        return self.channel


# {'application_id': '863733834121216011',
#  'channel_id': '760907664573202483',
#  'data': {'id': '872571634240860211',
#           'name': 'deliver',
#           'options': [{'name': 'animal', 'type': 3, 'value': 'animal_dog'},
#                       {'name': 'number', 'type': 4, 'value': 3}],
#           'type': 1},
#  'guild_id': '684492926528651336',
#  'id': '872580528421879808',
#  'member': {'avatar': None,
#             'deaf': False,
#             'is_pending': False,
#             'joined_at': '2020-10-09T20:02:03.304000+00:00',
#             'mute': False,
#             'nick': '[LDR] Minion3665',
#             'pending': False,
#             'permissions': '274877906943',
#             'premium_since': None,
#             'roles': ['856129494845751298',
#                       '760896658862243911',
#                       '760901551496626187',
#                       '697412626812108850',
#                       '760896837866749972'],
#             'user': {'avatar': '6f9f41d057107bea29dcffa0eb542d08',
#                      'discriminator': '6456',
#                      'id': '317731855317336067',
#                      'public_flags': 131328,
#                      'username': 'Minion3665'}},
#  'token': '<redacted for privacy>',
#  'type': 2,
#  'version': 1}
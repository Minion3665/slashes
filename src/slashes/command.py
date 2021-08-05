import discord
import enum


class CommandType(enum.Enum):
    COMMAND = 1
    GROUP = 2


class ParameterType(enum.Enum):
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


parameter_types = {
    str: ParameterType.STRING,
    int: ParameterType.INTEGER,
    bool: ParameterType.BOOLEAN,
    discord.User: ParameterType.USER,
    discord.abc.GuildChannel: ParameterType.CHANNEL,
    discord.role: ParameterType.ROLE,
}


class Parameter:
    def __init__(self, parameter_type: ParameterType, value=None):
        self.type = parameter_type
        self.value = value


class Command:
    def __init__(self, name, **parameters):
        self.type = 1
        self.name = name
        self.parameters = parameters
        self.id = None

    @staticmethod
    def convert_gateway_parameters(data):
        parameters = {option['name']: Parameter(ParameterType(option['type']), option['value'])
                      for option in data}
        return parameters

    @classmethod
    def from_gateway_data(cls, data):
        parameters = cls.convert_gateway_parameters(data['options'])
        new = cls(data['name'], **parameters)
        new.id = data['id']
        return new

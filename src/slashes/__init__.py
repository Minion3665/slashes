from . import context_old
from . import cog

Context = context_old.Context
Message = context_old.Message


def setup(bot):
    bot.add_cog(cog.Cog(bot))


__all__ = (
    setup,
    Context,
    Message,
)

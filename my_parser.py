from Commands import Command
from collections import namedtuple


CommandAttributeSingle = namedtuple('CommandAttribute', [])
CommandAttributeShortened = namedtuple('CommandAttribute', ["lesson"])
CommandAttributeStandard = namedtuple('CommandAttribute', ["lesson", "date"])
CommandAttributeExpanded = namedtuple('CommandAttribute', ["lesson", "date", "task"])
CommandAttributeExtraExpanded = namedtuple('CommandAttribute', ["lesson", "mon", "tue", "wed", 'thu', 'fri'])


class MessageParts:
    def __init__(self, comm, command_args):
        self.command = comm
        self.command_args = command_args

    @staticmethod
    def define_command(stock_message):
        splitted = stock_message.lower().split('*')
        return Command(splitted[0])

    @classmethod
    def parse_message(cls, stock_message):
        try:
            command = cls.define_command(stock_message)
        except ValueError:
            return cls(Command.UNKNOWN, CommandAttributeSingle())
        if command == Command.GET or command == Command.ACCESS:
            parts_list = stock_message.lower().split('*', maxsplit=3)
            command_args = CommandAttributeStandard(parts_list[1], parts_list[2])
            return cls(command, command_args)
        elif command == Command.WRITE or command == Command.CHANGE or command == Command.CHANGE_SCH:
            parts_list = stock_message.lower().split('*', maxsplit=4)
            command_args = CommandAttributeExpanded(parts_list[1], parts_list[2], parts_list[3])
            return cls(command, command_args)
        elif command == Command.GET_SCH:
            parts_list = stock_message.lower().split('*', maxsplit=2)
            command_args = CommandAttributeShortened(parts_list[1])
            return cls(command, command_args)
        elif command == Command.WRITE_SCH:
            parts_list = stock_message.lower().split('*', maxsplit=7)
            command_args = CommandAttributeExtraExpanded(parts_list[1], parts_list[2], parts_list[3], parts_list[4],
                                                         parts_list[5], parts_list[6])
            return cls(command, command_args)
        else:
            command_args = CommandAttributeSingle()
            return cls(command, command_args)


def parse_message(message):
    return MessageParts.parse_message(message)

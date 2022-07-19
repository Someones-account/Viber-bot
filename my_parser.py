from Commands import Command
from collections import namedtuple


CommandAttributeSingle = namedtuple('CommandAttribute', [])
CommandAttributeExtraShortened = namedtuple('CommandAttribute', ["lesson"])
CommandAttributeShortened = namedtuple('CommandAttribute', ["lesson", "datetype"])
CommandAttributeStandard = namedtuple('CommandAttribute', ["lesson", "datetype", "date"])
CommandAttributeExpanded = namedtuple('CommandAttribute', ["lesson", "datetype", "date", "task"])
CommandAttributeExtraExpanded = namedtuple('CommandAttribute', ["lesson", "mon", "tue", "wed", 'thu', 'fri'])


class MessageParts:
    def __init__(self, comm, command_args, full_message):
        self.command = comm
        self.command_args = command_args
        self.full_message = full_message

    @staticmethod
    def define_command(stock_message):
        splitted = stock_message.lower().split('*')
        return Command(splitted[0])

    @classmethod
    def parse_message(cls, stock_message):
        try:
            command = cls.define_command(stock_message)
        except ValueError:
            return cls(Command.UNKNOWN, CommandAttributeSingle(), stock_message)
        if command == Command.HELP or command == Command.START:
            command_args = CommandAttributeSingle()
            return cls(command, command_args, stock_message)
        if command == Command.GET:
            parts = stock_message.lower().split('*', maxsplit=4)
            if len(parts) == 1:
                command_args = CommandAttributeSingle()
                return cls(Command.GETTER_LESSON, command_args, stock_message)
            elif len(parts) == 2:
                command_args = CommandAttributeExtraShortened(parts[1])
                return cls(Command.GETTER_DATE_TYPE, command_args, stock_message)
            elif len(parts) == 3:
                command_args = CommandAttributeShortened(parts[1], parts[2])
                return cls(Command.GETTER_DATE, command_args, stock_message)
            else:
                command_args = CommandAttributeStandard(parts[1], parts[2], parts[3])
                return cls(command, command_args, stock_message)
        elif command == Command.WRITE:
            parts = stock_message.lower().split('*', maxsplit=5)
            if len(parts) == 1:
                command_args = CommandAttributeSingle()
                return cls(Command.WRITER_LESSON, command_args, stock_message)
            elif len(parts) == 2:
                command_args = CommandAttributeExtraShortened(parts[1])
                return cls(Command.WRITER_DATE_TYPE, command_args, stock_message)
            elif len(parts) == 3:
                command_args = CommandAttributeShortened(parts[1], parts[2])
                return cls(Command.WRITER_DATE, command_args, stock_message)
            elif len(parts) == 4:
                command_args = CommandAttributeStandard(parts[1], parts[2], parts[3])
                return cls(Command.WRITER_CONTENT, command_args, stock_message)
            else:
                command_args = CommandAttributeExpanded(parts[1], parts[2], parts[3], parts[4])
                return cls(command, command_args, stock_message)
        elif command == Command.CHANGE:
            parts = stock_message.lower().split('*', maxsplit=5)
            if len(parts) == 1:
                command_args = CommandAttributeSingle()
                return cls(Command.MODIFIER_LESSON, command_args, stock_message)
            elif len(parts) == 2:
                command_args = CommandAttributeExtraShortened(parts[1])
                return cls(Command.MODIFIER_DATE, command_args, stock_message)
            elif len(parts) == 3:
                command_args = CommandAttributeShortened(parts[1], parts[2])
                return cls(Command.MODIFIER_CONTENT, command_args, stock_message)
            else:
                command_args = CommandAttributeStandard(parts[1], parts[2], parts[3])
                return cls(command, command_args, stock_message)


def parse_message(message):
    return MessageParts.parse_message(message)

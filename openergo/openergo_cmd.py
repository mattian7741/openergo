import cmd
from typing import IO, Callable, List, Optional, cast

from openergo.openergo_cli import OpenergoCli


class OpenergoCmd(cmd.Cmd):
    # Class variable to store the introduction message for the CLI.
    intro: str = ""
    prompt: str = ""  # Class variable to store the prompt for the CLI.

    def __init__(
        self,
        # The constructor takes a 'OpenergoCli' object as 'cli'.
        cli: "OpenergoCli",
        completekey: str = "tab",
        stdin: Optional[IO[str]] = None,
        stdout: Optional[IO[str]] = None,
    ) -> None:
        # Call the constructor of the superclass 'cmd.Cmd'.
        super().__init__(completekey, stdin, stdout)
        self._cli = cli  # Store the 'cli' object as an instance variable.
        # Update the class variable 'intro' with the 'cli.intro'.
        OpenergoCmd.intro = self._cli.intro
        # Update the class variable 'prompt' with the 'cli.prompt'.
        OpenergoCmd.prompt = self._cli.prompt

    def onecmd(self, line: str) -> bool:
        # Split the input 'line' into a list of words (commands and arguments).
        splitline: List[str] = line.split()
        # Extract the first word, which is the command.
        command: str = splitline[0]

        # Check if the 'cmd.Cmd' superclass has a method named 'do_<command>',
        # or if the 'cli' object has an attribute named 'command'.
        if hasattr(self, f"do_{command}") or not hasattr(self._cli, command):
            # If either condition is true, it means the entered command is valid according to the superclass's
            # built-in command handling mechanism. Therefore, call the superclass's 'onecmd' method to process it,
            # which will automatically execute the corresponding 'do_<command>'
            # method or handle the unknown command.
            return super().onecmd(line)

        # If the command is not recognized, extract the remaining words as
        # arguments.
        args: List[str] = splitline[1:]

        # If the command is recognized but not a method of the superclass 'cmd.Cmd',
        # get the attribute from the 'cli' object with the name 'command'.
        # The attribute is assumed to be a callable (function or method). Cast it to 'callable'
        # and then call the callable with args as arguments.
        return cast(Callable[..., bool], getattr(self._cli, command))(*args)

    def do_exit(self, line: str) -> bool:
        # This method handles the 'exit' command. It always returns 'True',
        # indicating that the application should continue running and prompt
        # for the next command.
        return True


# get hash of lastest commit    git log -n 1 release3.3.0 --pretty=format:"%h" | tail -n 1
# get short hash                git rev-parse --short --verify my_branch

# list additions and deletions  git diff master origin/master
from shutil import which
from subprocess import CalledProcessError, TimeoutExpired, run

from os import linesep
from typing import Dict

# constants
LINE_SEPARATOR: str = linesep
CODEC_SETTINGS: Dict[str, str] = {"encoding": "utf-8", "errors": "strict"}

class Command:
    # TODO doc
    @staticmethod
    def is_available(command: str):
        """Checks at first that the specified command is syntaxically correct, then tells if the specified command is available.

        Args:
            command (str): the command line to be verified.

        Raises:
            TypeError: if the command is not a string.
            ValueError: if the command is an empty string.
        
        Returns:
            bool: True if the command is available, False otherwise.
        """
        if not isinstance(command, str):
            raise TypeError("The specified command must be a string.")

        if not command.strip():
            raise ValueError("The specified command must be a non-empty string.")

        return which(command)

    @staticmethod
    def get_version(command: str) -> tuple:
        """Returns the version of the specified command.
        May not work for all commands as the version is not always shared with --version option.

        Args:
            command (str): the specified command.

        Returns:
            tuple: the version of the specified command as a tuple.
        """
        matches = Command.execute(f'{command} --version | grep -Eo "([0-9]+\.[0-9\.]+)"')
        version = matches.strip().split("\n", maxsplit=1)[0]

        return tuple(map(int, (version.split("."))))

    @staticmethod
    def execute(command: str) -> str:
        """Executes the command and returns the output.

        Args:
            command (str): the command line to be executed.

        Raises:
            ValueError: if the command fails (in case the return code is not 0).

        Returns:
            str: the command stdout, otherwise raises an error.
        """
        try:
            process = run(command, shell=True, check=True, capture_output=True)  # nosec
            if process.stderr:
                raise CalledProcessError(process.returncode, command, process.stdout, stderr=process.stderr)
            return str(process.stdout, encoding=CODEC_SETTINGS["encoding"])
        except (CalledProcessError, TimeoutExpired) as error:
            if isinstance(error.stderr, (bytes, str)):
                error.stderr = error.stderr.decode(**CODEC_SETTINGS).replace(LINE_SEPARATOR, "")
            raise ValueError(error.stderr) from error


if __name__ == "__main__":
    
    # get azure resolved workitem
    # get last commit from rep 
    # get deployed image
    
    # 
    # helm dependency update demo-chart/

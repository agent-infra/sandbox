#!/usr/bin/env python3
"""AIO Sandbox CLI - Command line tool for AI agent sandbox environments"""

import sys
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commands.root import root
from commands.shell import exec, shell, sessions
from commands.file import cat, download, upload, ls
from commands.browser import screenshot, browser_info
from commands.jupyter import run_python, jupyter_info
from commands.nodejs import run_node, node_info


def main():

    # Register all commands
    root.add_command(exec)
    root.add_command(shell)
    root.add_command(sessions)
    root.add_command(cat)
    root.add_command(download)
    root.add_command(upload)
    root.add_command(ls)
    root.add_command(screenshot)
    root.add_command(browser_info)
    root.add_command(run_python)
    root.add_command(jupyter_info)
    root.add_command(run_node)
    root.add_command(node_info)

    root()


if __name__ == '__main__':
    main()

# AIO Sandbox CLI

Command-line interface for [AIO Sandbox](https://github.com/agent-infra/sandbox) - the all-in-one agent sandbox environment.

## Installation

```bash
# Install dependencies
pip install agent-sandbox

# Run CLI directly
python main.py --help

# Or install as a package
pip install -e .
sandbox --help
```

## Quick Start

```bash
# Set up a sandbox instance
docker run --security-opt seccomp=unconfined --rm -it -p 8080:8080 ghcr.io/agent-infra/sandbox:latest

# Execute commands
sandbox exec "echo hello"
sandbox exec "ls -la /home/user"
```

## Usage

### Shell Commands

```bash
# Execute a shell command
sandbox exec "ls -la"

# List active sessions
sandbox sessions

# Open interactive shell (use VNC or web terminal)
sandbox shell
```

### File Operations

```bash
# Read a file
sandbox cat /home/user/.bashrc

# List directory
sandbox ls /home/user

# Upload file to sandbox
sandbox upload local.txt /home/user/remote.txt

# Download file from sandbox
sandbox download /home/user/remote.txt ./local.txt
```

### Browser

```bash
# Take screenshot (base64 output)
sandbox screenshot

# Save screenshot to file
sandbox screenshot screenshot.png

# Get browser info
sandbox browser-info
```

### Code Execution

```bash
# Run Python code
sandbox run-python "print('Hello, World!')"

# Get Jupyter info
sandbox jupyter-info

# Run Node.js code
sandbox run-node "console.log('Hello, World!')"
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--base-url` | Sandbox API base URL | `http://localhost:8080` |
| `-o, --output` | Output format (`table`, `json`, `yaml`) | `table` |

## License

Apache License 2.0

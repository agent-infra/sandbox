import click
import json
from .root import root, get_client


@root.command()
@click.argument('command')
@click.option('--session-id', '-s', help='Shell session ID')
@click.option('--exec-dir', help='Working directory (absolute path)')
@click.option('--timeout', type=float, help='Timeout in seconds')
@click.option('--async', 'async_mode', is_flag=True, help='Run in async mode')
@click.pass_context
def exec(ctx, command, session_id, exec_dir, timeout, async_mode):
    """Execute a shell command"""
    client = get_client(ctx)
    result = client.shell.exec_command(
        command=command,
        id=session_id,
        exec_dir=exec_dir,
        timeout=timeout,
        async_mode=async_mode
    )

    if ctx.obj['output'] == 'json':
        click.echo(json.dumps({
            'id': result.id,
            'status': result.status,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'exit_code': result.exit_code
        }, indent=2))
    else:
        click.echo(result.stdout, nl=not result.stdout.endswith('\n'))
        if result.stderr:
            click.echo(result.stderr, err=True, nl=not result.stderr.endswith('\n'))


@root.command()
@click.pass_context
def shell(ctx):
    """Open an interactive shell session"""
    client = get_client(ctx)
    click.echo("Creating interactive shell session...")
    click.echo("WebSocket terminal available at: " + client.shell.get_terminal_url().data)
    click.echo("(Use VNC or web terminal to interact)")


@root.command()
@click.pass_context
def sessions(ctx):
    """List all active shell sessions"""
    client = get_client(ctx)
    result = client.shell.list_sessions()

    if ctx.obj['output'] == 'json':
        click.echo(json.dumps([{
            'id': s.id,
            'status': s.status,
            'command': s.command
        } for s in result.data.sessions], indent=2))
    else:
        if not result.data.sessions:
            click.echo("No active sessions")
        else:
            click.echo(f"{'ID':<40} {'STATUS':<10} {'COMMAND'}")
            click.echo("-" * 80)
            for s in result.data.sessions:
                cmd = s.command[:40] if s.command else ''
                click.echo(f"{s.id:<40} {s.status:<10} {cmd}")

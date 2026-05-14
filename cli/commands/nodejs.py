import click
from .root import root, get_client


@root.command()
@click.argument('code')
@click.option('--session-id', '-s', help='Node.js session ID')
@click.pass_context
def run_node(ctx, code, session_id):
    """Execute Node.js code"""
    client = get_client(ctx)
    result = client.nodejs.execute_code(code=code, session_id=session_id)

    for output in result.outputs:
        if hasattr(output, 'text') and output.text:
            click.echo(output.text)


@root.command()
@click.pass_context
def node_info(ctx):
    """Get Node.js runtime info"""
    client = get_client(ctx)
    info = client.nodejs.get_info()
    click.echo(f"Node.js Version: {info.version}")
    click.echo(f"V8 Version: {info.v8_version}")

import click
import json
from .root import root, get_client


@root.command()
@click.argument('code')
@click.option('--session-id', '-s', help='Jupyter session ID')
@click.pass_context
def run_python(ctx, code, session_id):
    """Execute Python code in Jupyter"""
    client = get_client(ctx)
    result = client.jupyter.execute_code(code=code, session_id=session_id)

    for output in result.outputs:
        if hasattr(output, 'text') and output.text:
            click.echo(output.text)
        elif hasattr(output, 'error') and output.error:
            click.echo(output.error, err=True)


@root.command()
@click.pass_context
def jupyter_info(ctx):
    """Get Jupyter runtime info"""
    client = get_client(ctx)
    info = client.jupyter.get_info()
    click.echo(f"Python Version: {info.python_version}")
    click.echo(f"Working Directory: {info.working_directory}")

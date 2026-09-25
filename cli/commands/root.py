import click
from agent_sandbox import Sandbox


@click.group()
@click.option('--base-url', default='http://localhost:8080', help='Sandbox API base URL')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
@click.pass_context
def root(ctx, base_url, output):
    """AIO Sandbox CLI - Command line tool for AI agent sandbox environments"""
    ctx.ensure_object(dict)
    ctx.obj['base_url'] = base_url
    ctx.obj['output'] = output
    ctx.obj['client'] = Sandbox(base_url=base_url)


def get_client(ctx):
    return ctx.obj.get('client') or Sandbox(base_url=ctx.obj['base_url'])

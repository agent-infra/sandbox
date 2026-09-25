import click
import json
from .root import root, get_client


@root.command()
@click.argument('path')
@click.pass_context
def cat(ctx, path):
    """Read a file"""
    client = get_client(ctx)
    result = client.file.read_file(file=path)
    click.echo(result.data.content)


@root.command()
@click.argument('remote_path')
@click.argument('local_path')
@click.pass_context
def download(ctx, remote_path, local_path):
    """Download a file from sandbox"""
    client = get_client(ctx)
    result = client.file.read_file(file=remote_path)
    with open(local_path, 'w') as f:
        f.write(result.data.content)
    click.echo(f"Downloaded to {local_path}")


@root.command()
@click.argument('local_path')
@click.argument('remote_path')
@click.pass_context
def upload(ctx, local_path, remote_path):
    """Upload a file to sandbox"""
    client = get_client(ctx)
    with open(local_path, 'r') as f:
        content = f.read()
    client.file.write_file(file=remote_path, content=content)
    click.echo(f"Uploaded to {remote_path}")


@root.command()
@click.argument('path')
@click.option('--pattern', '-p', help='Search pattern')
@click.pass_context
def ls(ctx, path, pattern):
    """List files in a directory"""
    client = get_client(ctx)
    if pattern:
        result = client.file.search_in_file(path=path, pattern=pattern)
        if ctx.obj['output'] == 'json':
            click.echo(json.dumps([{'path': m.path, 'line': m.line, 'content': m.content} for m in result.data.matches], indent=2))
        else:
            for m in result.data.matches:
                click.echo(f"{m.path}:{m.line}: {m.content}")
    else:
        result = client.file.list_path(path=path)
        if ctx.obj['output'] == 'json':
            click.echo(json.dumps([{'path': f.path, 'is_dir': f.is_dir, 'size': f.size} for f in result.data.files], indent=2))
        else:
            for f in result.data.files:
                prefix = 'd' if f.is_dir else '-'
                size = f.size or 0
                click.echo(f"{prefix} {size:>10}  {f.path}")

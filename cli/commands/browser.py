import click
import base64
from .root import root, get_client


@root.command()
@click.argument('output_path', required=False)
@click.pass_context
def screenshot(ctx, output_path):
    """Take a screenshot"""
    client = get_client(ctx)
    img_data = b''.join(client.browser.screenshot())

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(img_data)
        click.echo(f"Screenshot saved to {output_path}")
    else:
        # Output as base64 to stdout
        click.echo(base64.b64encode(img_data).decode())


@root.command()
@click.pass_context
def browser_info(ctx):
    """Get browser information"""
    client = get_client(ctx)
    info = client.browser.get_info()
    click.echo(f"CDP URL: {info.cdp_url}")
    click.echo(f"Display: {info.display}")
    click.echo(f"Viewport: {info.viewport.width}x{info.viewport.height}")

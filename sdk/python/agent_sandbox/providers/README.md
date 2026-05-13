# Cloud Providers

This module contains cloud provider implementations for sandbox management.

## Volcengine

The Volcengine provider integrates with Volcengine VEFAAS APIs to manage sandbox instances.

```python
from agent_sandbox.providers import VolcengineProvider

provider = VolcengineProvider(
    access_key="your-access-key",
    secret_key="your-secret-key",
    region="cn-beijing",
)

sandbox_id = provider.create_sandbox("function-id", timeout=30)
sandbox = provider.get_sandbox("function-id", sandbox_id)
sandboxes = provider.list_sandboxes("function-id")
provider.set_sandbox_timeout("function-id", sandbox_id, 120)
provider.delete_sandbox("function-id", sandbox_id)
```

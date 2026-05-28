# Security

By default, a local AIO Sandbox is intended for trusted local development. When exposing it to a network or another service, add authentication and limit access.

## JWT Authentication

Set `JWT_PUBLIC_KEY` to enable Bearer token verification. Your application signs tokens with the private key, and the sandbox verifies them with the public key.

Generate a key pair:

```bash
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem
```

Start the sandbox with the public key:

```bash
docker run --security-opt seccomp=unconfined --rm -it \
  -p 8080:8080 \
  -e JWT_PUBLIC_KEY="$(base64 -w 0 public_key.pem)" \
  ghcr.io/agent-infra/sandbox:latest
```

Call APIs with a Bearer token:

```bash
curl "http://localhost:8080/v1/sandbox" \
  -H "Authorization: Bearer $SANDBOX_TOKEN"
```

## Short-Lived Tickets

For browser access or temporary handoff flows, prefer short-lived tickets when supported by your deployment. Tickets should expire quickly and be scoped to the minimum required access.

## Network Boundaries

- Bind the sandbox to localhost unless remote access is required.
- Put a reverse proxy with TLS in front of the sandbox for shared environments.
- Restrict inbound access by IP, network, or service identity.
- Do not expose unauthenticated sandbox APIs on the public internet.

## Secret Handling

- Pass secrets through runtime environment variables or a secret manager.
- Do not bake secrets into custom images.
- Do not write long-lived secrets to Skills, hooks, notebooks, or generated files.
- Prefer short-lived credentials for task-specific access.


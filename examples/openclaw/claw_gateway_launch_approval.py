from agent_sandbox import Sandbox
import re, os, json, shlex

class OpenClawManager:
    def __init__(
        self,
        client: Sandbox,
        openai_api_key: str,
        home: str = "/tmp/openclaw-home",
        port: int = 18789,
        model: str = "openai/gpt-5.1-codex",
        allowed_origins: list[str] | None = None,
    ):
        self.client = client
        self.openai_api_key = openai_api_key
        self.home = home
        self.port = port
        self.model = model
        self.allowed_origins = allowed_origins or [f"http://localhost:{port}"]

    import shlex

    def sh(self, command: str) -> str:
      full_command = (
          f"export OPENAI_API_KEY={shlex.quote(self.openai_api_key)}; "
          f"{command}"
      )
      result = self.client.shell.exec_command(
          command=f"bash -lc {shlex.quote(full_command)}"
      )
      output = result.data.output
      exit_code = result.data.exit_code
      if exit_code != 0:
          raise RuntimeError(f"Command failed ({exit_code}):\n{output}")
      return output   

    def install(self) -> str:
        return self.sh("command -v openclaw >/dev/null 2>&1 || npm install -g openclaw@latest")

    def setup(self) -> str:
        return self.sh(
            f'export OPENCLAW_HOME={self.home}; '
            f'[ -d "$OPENCLAW_HOME/.openclaw" ] || openclaw setup'
        )

    def config_set_json(self, path: str, value) -> str:
      value_json = json.dumps(value)
      return self.sh(
        f"export OPENCLAW_HOME={shlex.quote(self.home)}; "
        f"openclaw config set {shlex.quote(path)} {shlex.quote(value_json)} --json"
      )

    def configure(self) -> None:
        self.config_set_json("agents.defaults.model.primary", self.model)
        self.config_set_json("gateway.mode", "local")
        self.config_set_json("gateway.bind", "lan")
        self.config_set_json("gateway.port", self.port)
        self.config_set_json("gateway.controlUi.allowedOrigins", self.allowed_origins)
        self.config_set_json(
            "gateway.auth.rateLimit",
            {
                "maxAttempts": 10,
                "windowMs": 60000,
                "lockoutMs": 300000,
            },
        )

    def issue_token(self) -> str:
        out = self.sh(
            'TOKEN="$(openssl rand -hex 16)"; '
            'echo "$TOKEN" >/tmp/openclaw-token; '
            'chmod 600 /tmp/openclaw-token; '
            'echo "$TOKEN"'
        )
        return out.strip().splitlines()[-1]

    def get_token(self) -> str:
        out = self.sh("cat /tmp/openclaw-token")
        return out.strip().splitlines()[-1]

    def start_gateway(self) -> str:
        return self.sh(
            f'export OPENCLAW_HOME={self.home}; '
            f'TOKEN="$(cat /tmp/openclaw-token)"; '
            f'nohup openclaw gateway --port {self.port} --bind lan '
            f'--auth token --token "$TOKEN" --force '
            f'>/tmp/openclaw-gateway.out 2>/tmp/openclaw-gateway.err < /dev/null &'
        )

    def wait_ready(self) -> str:
        return self.sh(
            f'TOKEN="$(cat /tmp/openclaw-token)"; '
            f'until openclaw gateway status --url ws://127.0.0.1:{self.port} --token "$TOKEN" >/dev/null 2>&1; '
            f'do sleep 1; done; '
            f'echo READY'
        )

    def launch(self) -> str:
        self.install()
        self.setup()
        self.configure()
        self.issue_token()
        self.start_gateway()
        self.wait_ready()
        return self.dashboard_url()

    def dashboard_url(self) -> str:
        token = self.get_token()
        return f"http://localhost:{self.port}/#token={token}"

    def list_devices(self) -> str:
      token = self.get_token()
      return self.sh(
        f'export OPENCLAW_HOME={self.home}; '
        f'openclaw devices list --url ws://127.0.0.1:{self.port} --token "{token}"'
      )

    def gateway_status(self) -> str:
      token = self.get_token()
      return self.sh(
        f'export OPENCLAW_HOME={self.home}; '
        f'openclaw gateway status --url ws://127.0.0.1:{self.port} --token "{token}"'
      )

    def get_pending_device_request_id(self) -> str | None:
        output = self.list_devices()
        return self._extract_first_pending_request_id(output)

    def approve_device(self, request_id: str) -> str:
        token = self.get_token()
        return self.sh(
            f'openclaw devices approve {request_id} '
            f'--url ws://127.0.0.1:{self.port} --token "{token}"'
        )
    
    def approve_pending_device(self) -> str:
      output = self.list_devices()

      if "Paired (" in output and "Pending (" not in output:
        return "ALREADY_PAIRED"

      request_id = self.get_pending_device_request_id()
      if not request_id:
        return "NO_PENDING_DEVICE"

      approve_output = self.approve_device(request_id)
      return f"DEVICE_APPROVED:{request_id}\n{approve_output}"

    @staticmethod
    def _extract_first_pending_request_id(text: str) -> str | None:
        pending_match = re.search(r"Pending.*?(?=Paired|\Z)", text, flags=re.DOTALL)
        if not pending_match:
            return None
        pending_text = pending_match.group(0)
        match = re.search(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
            pending_text,
        )
        return match.group(0) if match else None

    @staticmethod
    def _escape_shell(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    
def main() -> None:
    client = Sandbox(base_url="http://localhost:8080")
    openai_api_key = os.environ["OPENAI_API_KEY"]

    manager = OpenClawManager(
        client=client,
        openai_api_key=openai_api_key,
        home="/tmp/openclaw-home",
        port=18789,
        model="openai/gpt-5.1-codex",
        allowed_origins=["http://localhost:18789"],
    )

    url = manager.launch()
    print("OpenClaw launched.")
    print(url)

    input("Open the dashboard URL, then press Enter to approve the device...")

    print(manager.list_devices())
    print(manager.approve_pending_device())
    print(manager.gateway_status())


if __name__ == "__main__":
    main()
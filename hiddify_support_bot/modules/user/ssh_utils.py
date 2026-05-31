from io import StringIO
import re
import asyncssh


def get_public_key():
    with open(SSH_PUB_PATH) as f:
        return f.readline().strip()


SSH_PK_PATH = "./hiddify_support.key"
SSH_PUB_PATH = SSH_PK_PATH+".pub"
SSH_PUB_STR = get_public_key()



ansi_escape_pattern = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")


def _text(stream: bytes | str | None) -> str:
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode(errors="replace")
    return str(stream)


def _format_result(result: asyncssh.SSHCompletedProcess) -> str:
    return f"{_text(result.stdout)}  {_text(result.stderr)}".strip()


async def test_ssh(host: str,port: int,username: str, key_path: str) -> str:
    async with asyncssh.connect(host,port=port,username=username,client_keys=[key_path],known_hosts=None,connect_timeout=10,encoding="utf-8") as conn:
        result = await conn.run("cat /opt/hiddify-manager/VERSION", check=False)
        out = _format_result(result)
        print(f"VERSION (exit {result.exit_status}):\n{out}\n")

        try:
            status = await conn.run("/opt/hiddify-manager/status.sh", check=False)
            cleaned = ansi_escape_pattern.sub("", _text(status.stdout))
            cleaned = cleaned.replace("                      ", " ")
            cleaned = cleaned.replace("-----------------------------------", " ")
            out += f"\n```bash\n{cleaned}\n{_text(status.stderr)}```"
            print(f"status.sh (exit {status.exit_status}):\n{cleaned}\n")
        except Exception as e:
            out += f"\nError running status.sh: {e}"
            print(f"status.sh failed: {e}")

        return out

async def test_ssh_connection(ssh_info):
    if not ssh_info:
        return False
    try:
        return await test_ssh(ssh_info["host"], ssh_info["port"], ssh_info["user"], SSH_PK_PATH)
    except Exception as e:
        print(f"Error: {e}")
    return False


def get_ssh_info(txt, searchAll=False):
    import re

    pattern = r"(?:ssh\s+)(?:(?P<user>\w+)@(?P<host>[^\s@]+))?(?:\s+-p\s+(?P<port>\d+))?\s*"
    if searchAll:
        pattern = f"(.*){pattern}.*"
    else:
        pattern = f"^{pattern}$"

    match = re.match(pattern, txt.replace("\n", " "))
    if not match:
        return None

    groups = match.groupdict()
    try:
        port = int(groups.get("port", "22"))
    except:
        port = 22
    return {"user": groups["user"], "host": groups["host"], "port": port}


async def close_permission(ssh_info):
    try:
        async with asyncssh.connect(
            ssh_info["host"], port=ssh_info["port"], username=ssh_info["user"], client_keys=[SSH_PK_PATH], known_hosts=None, connect_timeout=2
        ) as conn:
            # result = await conn.run("pip3 freeze | grep hiddifypanel | awk -F ' == ' '{ print $2 }'")
            result = await conn.run("sed -i '/hiddify@assistant/d' ~/.ssh/authorized_keys")
            out = f"{result.stdout}  {result.stderr}".strip()
            return f'"{out}"'
        return "WTF?"
    except Exception as e:
        print(f"Error: {e}")

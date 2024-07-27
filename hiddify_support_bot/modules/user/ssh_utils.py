from io import StringIO
import re
import asyncssh


def get_public_key():
    with open(SSH_PUB_PATH) as f:
        return f.readline()


SSH_PK_PATH = "./hiddify_support.key"
SSH_PUB_PATH = SSH_PK_PATH+".pub"
SSH_PUB_STR = get_public_key()

ansi_escape_pattern = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

# Remove ANSI escape sequences


async def test_ssh_connection(ssh_info):
    if not ssh_info:
        return False
    print("TEST")
    try:
        async with asyncssh.connect(
            ssh_info["host"], port=ssh_info["port"], username=ssh_info["user"], client_keys=[SSH_PK_PATH], known_hosts=None, connect_timeout=2
        ) as conn:
            # result = await conn.run("pip3 freeze | grep hiddifypanel | awk -F ' == ' '{ print $2 }'")
            result = await conn.run("cat /opt/hiddify-manager/VERSION")
            out = f"{result.stdout}  {result.stderr}".strip()
            try:
                status = await conn.run("/opt/hiddify-manager/status.sh")
                out += f"```bash\n{ansi_escape_pattern.sub('', status.stdout)}\n{status.stderr}```"
            except Exception as e:
                out += (f"Error: {e}")
            print("SUCCESS")
            return f'"{out}"'
        return "WTF?"
    except Exception as e:
        print(f"Error: {e}")
    return False


def get_ssh_info(txt, searchAll=False):
    import re

    pattern = r"^(?:ssh\s+)?(?:(?P<user>\w+)@(?P<host>[^\s@]+))?(?:\s+-p\s+(?P<port>\d+))?\s*$"
    match = re.match(pattern, txt)

    if match:
        groups = match.groupdict()
        try:
            port = int(groups.get("port", "22"))
        except:
            port = 22
        return {"user": groups["user"], "host": groups["host"], "port": port}
    return None


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

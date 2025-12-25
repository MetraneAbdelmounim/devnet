import os
import asyncio
import yaml
from jinja2 import Environment, FileSystemLoader
from scrapli.driver.core import AsyncIOSXEDriver
from inv import DEVICES

username = os.environ['XE_VAR_USER']
password = os.environ['XE_VAR_PASS']


def generate_config(device):
    """
    Load yaml from host vars for each device in list.
    Render config via Jinja2
    """
    hostname = device["hostname"]
    config_data = yaml.safe_load(open(f"host_vars/{hostname}.yaml"))
    env = Environment(
        loader=FileSystemLoader("./templates"), trim_blocks=True, lstrip_blocks=True
    )
    template = env.get_template("bgp.j2")
    configuration = template.render(config_data)
    return configuration


async def deploy_config(device):
    """
    Coroutine to open connection and push config
    """
    async with AsyncIOSXEDriver(
        host=device["host"],
        auth_username=username,
        auth_password=password,
        auth_strict_key=False,
        transport="asyncssh",
    ) as conn:
        prompt_result = await conn.get_prompt()
        cfg = generate_config(device).splitlines()
        configs_result = await conn.send_configs(configs=cfg)
    return prompt_result, configs_result


async def main():
    """
    Main coroutine
    """
    coroutines = [deploy_config(device) for device in DEVICES]
    results = await asyncio.gather(*coroutines)
    for result in results:
        print(f"{result[0]}")
        print(f"{result[1].result}\n\n")


asyncio.run(main())

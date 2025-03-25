import asyncio

from fiber.chain import chain_utils, interface, weights
from fiber.chain.fetch_nodes import get_nodes_for_netuid
from fiber.logging_utils import get_logger
import argparse
import time

logger = get_logger(__name__)


async def set_weights(netuid: int, wallet_name: str, hotkey_name: str):
    substrate = interface.get_substrate()
    nodes = get_nodes_for_netuid(substrate=substrate, netuid=netuid)
    keypair = chain_utils.load_hotkey_keypair(
        wallet_name=wallet_name, hotkey_name=hotkey_name
    )
    validator_node_id = substrate.query(
        "SubtensorModule", "Uids", [netuid, keypair.ss58_address]
    ).value
    version_key = substrate.query(
        "SubtensorModule", "WeightsVersionKey", [netuid]
    ).value
    node_weights = [0 for node in nodes]
    node_weights[4] = 1
    weights.set_node_weights(
        substrate=substrate,
        keypair=keypair,
        node_ids=[node.node_id for node in nodes],
        node_weights=node_weights,
        netuid=netuid,
        validator_node_id=validator_node_id,
        version_key=version_key,
        wait_for_inclusion=True,
        wait_for_finalization=True,
    )


async def main():
    # await metagraph_example()
    parser = argparse.ArgumentParser()
    parser.add_argument("--netuid", type=int, default=26)
    parser.add_argument("--wallet-name", type=str, default="default")
    parser.add_argument("--hotkey-name", type=str, default="default")
    args = parser.parse_args()

    while True:
        await set_weights(args.netuid, args.wallet_name, args.hotkey_name)
        print("Waiting 10 minutes...")
        time.sleep(10 * 60)  # set weights every 10 minutes


if __name__ == "__main__":
    asyncio.run(main())

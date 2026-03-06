from src.udp.udp_client import UDPClient
import numpy as np

def run_udp_client(host="127.0.0.1", port=9000, packaging_type="json"):

    client = UDPClient(packaging_type)

    client.connect(host, port)

    step = 0

    while True:

        client.step()

        print("[Client] Sent action")

        step += 1


if __name__ == "__main__":

    run_udp_client(
        host="127.0.0.1",
        port=9000,
        packaging_type="json"
    )
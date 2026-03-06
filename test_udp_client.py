from src.udp.udp_client import UDPClient
import numpy as np

def run_udp_client(host="127.0.0.1", port=9000, packaging_type="json"):

    client = UDPClient(packaging_type)
    client.connect(host, port)

    try:
        while True:
            finished = client.step()
            if finished:
                break
    except KeyboardInterrupt:
        print("\nClient stopped by user")

    finally:
        client.close()
        print("[INFO] Client exited.")


if __name__ == "__main__":

    run_udp_client(
        host="127.0.0.1",
        port=9000,
        packaging_type="pickle"
    )
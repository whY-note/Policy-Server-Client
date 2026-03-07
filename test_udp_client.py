from src.udp.udp_client import UDPClient

def run_udp_client(host="127.0.0.1", port=9000, packaging_type="json"):

    client = UDPClient(packaging_type)

    try:
        client.connect(host, port)

        client._send_msg({"type": "user_name", "user_name": "unknown_user"})

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
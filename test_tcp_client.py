from src.tcp.tcp_client import TCPClient


if __name__ =="__main__":
    PACKAGING_TYPE = "pickle"

    client = TCPClient(packaging_type = PACKAGING_TYPE)

    # host = "localhost"
    # port = 8000

    # host = "192.168.6.49"
    # port = 8000

    # host = "120.48.23.252"
    # port  = 9000

    host = "localhost"
    port = 9000

    try:
        client.connect(host, port)
        print("[INFO] Connected.")
        while True:
            client.step()

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        print("[INFO] Closing connection.")
        client.close()
        print("[INFO] Client exited.")
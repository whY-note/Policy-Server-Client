from src.web.web_client import WebClient

if __name__ == "__main__":
    PACKAGING_TYPE = "json"

    host = "localhost"
    port = 9000
    client = WebClient(packaging_type=PACKAGING_TYPE)
    try:
        client.connect(host, port, max_size = None)
        while True:
            client.step()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        client.close()
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print("[INFO] Closing connection.")
        client.close()
        print("[INFO] Client exited.")
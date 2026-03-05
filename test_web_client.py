from src.web.web_client import WebClient

if __name__ == "__main__":
    PACKAGING_TYPE = "json"
    # server_url = "ws://localhost:9000"
    # server_url = "ws://192.168.6.49:8000"
    # server_url = "ws://120.48.23.252:22"
    server_url = "ws://localhost:9000"
    client = WebClient(server_url, packaging_type=PACKAGING_TYPE)
    try:
        while True:
            client.step()
    except KeyboardInterrupt:
        client.close()
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client.close()
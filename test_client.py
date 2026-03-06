from src.base.base_client import BaseClient
from src.tcp.tcp_client import TCPClient
from src.web.web_client import WebClient
from src.utils.utils import load_yaml, jpeg_to_img

from websockets.exceptions import ConnectionClosedOK
from websockets.exceptions import ConnectionClosedError

def create_client(protocol, packaging_type) -> BaseClient:
    if protocol == "tcp":
        return TCPClient(packaging_type=packaging_type)
    elif protocol == "web":
        return WebClient(packaging_type=packaging_type)
    else:
        raise ValueError(f"Unsupported protocol: {protocol}")

def main(protocol, host, port, packaging_type):
    client = create_client(protocol, packaging_type)

    try:
        client.connect(host, port)
        print("[INFO] Connected.")
        while True:
            client.step()
    except KeyboardInterrupt:
        print("[INFO] Interrupted by user.")
        client.close()
    except ConnectionError:
        print("[INFO] Server exited.")
    except ConnectionClosedOK:
        print("[INFO] Connection closed by server.")
    except ConnectionClosedError:
        print(f"[ERROR] Connection closed with error: {e}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        print("[INFO] Closing connection.")
        client.close()
        print("[INFO] Client exited.")

if __name__ == "__main__":
    config_path = "./config/config.yml"
    config = load_yaml(config_path)

    protocol = config["protocol"]
    packaging_type = config["packaging_type"]
    host = config["client"]["host"]
    port = config["client"]["port"]

    print("Config: ")
    print("Protocol: ", protocol)
    print("Packaging type: ", packaging_type)
    print("Host: ", host)
    print("Port: ", port)

    main(protocol, host, port, packaging_type)


    


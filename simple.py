"""
A simple MQTT client for MicroPython (CORREGIDO)
Compatible con Mosquitto y Raspberry Pi
"""

import usocket as socket
import ustruct as struct
import utime as time


class MQTTException(Exception):
    pass


class MQTTClient:
    def __init__(self, client_id, server, port=1883, user=None, password=None,
                 keepalive=30, ssl=False, ssl_params={}):
        self.client_id = client_id if isinstance(client_id, bytes) else client_id.encode()
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.keepalive = keepalive
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.sock = None
        self.last_ping = 0

    def _send_str(self, s):
        self.sock.write(struct.pack("!H", len(s)))
        self.sock.write(s)

    def connect(self, clean_session=True):
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock = socket.socket()

        # SSL si aplica
        if self.ssl:
            import ussl
            self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)

        self.sock.connect(addr)

        # --------------------------------------------
        # MQTT CONNECT PACKET (CORRECTO)
        # --------------------------------------------
        packet = bytearray()

        # Fixed header
        packet.append(0x10)  # CONNECT

        # Variable header
        var_header = bytearray()
        var_header.extend(b"\x00\x04MQTT")  # Protocol name
        var_header.append(4)                # Protocol level
        var_header.append(2 if clean_session else 0)  # Flags
        var_header.extend(struct.pack("!H", self.keepalive))

        # Payload
        payload = bytearray()
        payload.extend(struct.pack("!H", len(self.client_id)))
        payload.extend(self.client_id)

        # Remaining Length
        remaining = len(var_header) + len(payload)
        while True:
            digit = remaining & 0x7F
            remaining >>= 7
            if remaining > 0:
                digit |= 0x80
            packet.append(digit)
            if remaining == 0:
                break

        # Final packet
        packet.extend(var_header)
        packet.extend(payload)

        # Send packet
        self.sock.write(packet)

        # Read CONNACK
        resp = self.sock.read(4)
        if resp != b"\x20\x02\x00\x00":
            raise MQTTException("Failed to connect, got: %s" % resp)

    def disconnect(self):
        try:
            self.sock.write(b"\xE0\x00")
        except:
            pass
        try:
            self.sock.close()
        except:
            pass

    def ping(self):
        self.sock.write(b"\xC0\x00")

    def publish(self, topic, msg, retain=False, qos=0):
        packet = bytearray()
        header = 0x30 | (qos << 1) | retain
        packet.append(header)

        # Variable length
        remaining = 2 + len(topic) + len(msg)
        while True:
            digit = remaining & 0x7F
            remaining >>= 7
            if remaining > 0:
                digit |= 0x80
            packet.append(digit)
            if remaining == 0:
                break

        # Topic
        packet.extend(struct.pack("!H", len(topic)))
        packet.extend(topic)

        # Message
        packet.extend(msg)

        self.sock.write(packet)

    def subscribe(self, topic, qos=0):
        packet = bytearray(b"\x82")
        remaining = 2 + 2 + len(topic) + 1

        # Remaining length
        while True:
            digit = remaining & 0x7F
            remaining >>= 7
            if remaining > 0:
                digit |= 0x80
            packet.append(digit)
            if remaining == 0:
                break

        packet.extend(struct.pack("!H", 1))  # Message ID
        packet.extend(struct.pack("!H", len(topic)))
        packet.extend(topic)
        packet.append(qos)

        self.sock.write(packet)

    def wait_msg(self):
        return self.sock.read(1)

    def check_msg(self):
        return None



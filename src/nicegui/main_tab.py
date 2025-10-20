import subprocess
import json
import asyncio

from nicegui import app, ui
from typing import Optional, List, Tuple

from src.dataclasses import AppConfig

class MainTab(ui.element):
    def __init__(self, config: AppConfig):
        super().__init__()
        self.main_color = config.main_color
        self.secondary_color = config.secondary_color
        self.main_page_grid = ui.grid(columns = 2).classes("gap-4")
        self.refresh_timer = ui.timer(interval = 60.0, callback = lambda: self.get_tailscale_status())
        self.refresh_button = ui.button("Refresh Stats", color = self.main_color, on_click = lambda: self.get_tailscale_status()).style("color: white;")

        self.valid_digits = [str(i) for i in range(0, 10)] # for line checking with stdout

        # dictionary of additional ports based on dns
        self.additional_ports = config.additional_ports

        self.http_ports = config.http_ports
        self.https_ports = config.https_ports

        # init last dictionary of ip: ports
        # idea is if its the same, don't clear and spend precious cpu making new cards
        self.last_memory = {}

        self.cached_peers_data = app.storage.user.get("cached_peers_data", None)
        if self.cached_peers_data:
            self._refresh_grid(self.cached_peers_data)

        ui.timer(0.1, self.load_stats, once = True)

    # helper to return a list of ports
    def _strip_port_stdout(self, stdout: str) -> List[int]:
        will_parse = False
        ports = []

        for line in stdout.split("\n"):
            if len(line) > 0:
                if will_parse and line[0] in self.valid_digits:
                    
                    # parse port line: "22/tcp   open  ssh"
                    parts = line.split()
                    port_num = parts[0].split("/")[0]
                    service = parts[2] if len(parts) > 2 else "unknown"

                    if parts[1] == "open":
                        ports.append({
                            "port": port_num,
                            "service": service,
                            "protocol": parts[1] if len(parts) > 1 else "tcp"
                        })

            if line.startswith("PORT"):
                will_parse = True

        return ports

    # helper for checking if state has changed
    def _create_state_key(self, ip: str, online: bool, ports: List[int]) -> Tuple[str, bool, List[int]]:

        # needs to be sorted for easy comparison: x == y
        sorted_ports = tuple(sorted([p["port"] for p in ports]))

        return (ip, online, sorted_ports)

    # helper to get whether protocol is either http/https
    # for http, will check if its either in http_ports or if "http" is in service
    def _get_protocol_for_port(self, port: str, service: str) -> Optional[str]:
        if int(port) in self.https_ports:

            return "https"
            
        elif int(port) in self.http_ports or "http" in service.lower():

            return "http"
        
        else:

            return None

    # helper to refresh the main grid
    def _refresh_grid(self, peers_data: List[dict]) -> None:
        self.main_page_grid.clear()
            
        with self.main_page_grid:
            for peer in peers_data:
                with ui.card().classes("w-full"):
                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.column().classes("gap-1"):
                            ui.label(peer["hostname"]).classes("text-xl font-bold")
                            ui.label(peer["dns_name"]).classes("text-sm text-gray-500")
                            ui.label(peer["ip"]).classes("text-xs text-gray-400")
                        
                        if peer["online"]:
                            ui.badge("Online", color = self.main_color)
                        else:
                            ui.badge("Offline", color = self.secondary_color)
                    
                    # only show ports if online
                    if peer["online"]:
                        ui.separator()

                        with ui.column().classes("w-full"):
                            ui.label("Open Ports:").classes("font-semibold")
                            
                            if peer["ports"]:
                                with ui.row().classes("gap-2 flex-wrap"):
                                    infos = []
                                    for port_info in peer["ports"]:
                                        port = port_info["port"]
                                        service = port_info["service"]
                                        protocol = self._get_protocol_for_port(port, service)

                                        infos += [(port, service, protocol)]

                                    infos.sort(key = lambda x: (x[2] not in ["http", "https"], x[0]))
                                    for port, service, protocol in infos:
                                        if protocol:
                                            url = f"{protocol}://{peer['ip']}:{port}"

                                            ui.link(
                                                f"{port} ({service})",
                                                url,
                                                new_tab = True
                                            ).classes("text-blue-600 hover:text-blue-800 underline")

                                        else:
                                            ui.label(f"{port} ({service})").classes("bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded text-sm")

        return None

    # scan a single port on ip (dns_name)
    # port is returned as a list with either 0/1 integers
    def scan_port(self, dns_name: str, port: str) -> List[int]:
        command = f"nmap -p {port} {dns_name}"
        res = subprocess.run(
            command.split(" "),
            capture_output = True,
            text = True
        )

        port = self._strip_port_stdout(res.stdout)

        return port

    # scan ports on ip (dns_name)
    def scan_ports(self, dns_name: str) -> List[int]:
        command = f"nmap {dns_name}"
        res = subprocess.run(
            command.split(" "),
            capture_output = True,
            text = True
        )

        ports = self._strip_port_stdout(res.stdout)

        return ports

    # wrapper to call load_stats (async)
    def get_tailscale_status(self) -> None:
        ui.timer(0.1, self.load_stats, once = True)

        return None

    # checks if state has changed
    # if state has changed, we should refresh the grid
    async def load_stats(self) -> None:

        # get tailscale device info
        command = "tailscale status --json"
        res = subprocess.run(
            command.split(" "),
            capture_output = True,
            text = True
        )

        # dict
        d = json.loads(res.stdout)

        # get relevant info for each "peer" (defined as connected and discoverable device in tailscale)
        peers_data = [] # list of dicts
        for peer_id, peer_data in d.get("Peer", {}).items():
            hostname = peer_data.get("HostName", "Unknown")
            dns_name = peer_data.get("DNSName", "")[:-1]
            online = peer_data.get("Online", False)
            ip = peer_data.get("TailscaleIPs", [""])[0]

            peers_data.append({
                "hostname": hostname,
                "dns_name": dns_name,
                "online": online,
                "ip": ip,
                "peer_data": peer_data
            })

        # dont forget about self
        self_data = d.get("Self", {})
        hostname = self_data.get("HostName", "Unknown")
        dns_name = self_data.get("DNSName", "")[:-1]
        online = self_data.get("Online", False)
        ip = self_data.get("TailscaleIPs", [""])[0]

        peers_data.append({
            "hostname": hostname,
            "dns_name": dns_name,
            "online": online,
            "ip": ip,
            "peer_data": self_data
        })

        # sort by whether peer is "online", then ip
        peers_data.sort(key = lambda x: (not x["online"], x["ip"]))

        # scan all peers and build new state
        new_memory = {}
        for peer in peers_data:
            if peer["online"]:
                loop = asyncio.get_event_loop()
                ports = await loop.run_in_executor(None, self.scan_ports, peer["dns_name"])

                # add additional ports based on config
                # some ports are not discoverable by `nmap`
                if peer["dns_name"] in self.additional_ports:
                    for port in self.additional_ports[peer["dns_name"]]:
                        additional = await loop.run_in_executor(None, self.scan_port, peer["dns_name"], port)
                        ports += additional

                peer["ports"] = ports
                new_memory[peer["ip"]] = self._create_state_key(peer["ip"], peer["online"], ports)

            else:
                peer["ports"] = []
                new_memory[peer["ip"]] = self._create_state_key(peer["ip"], peer["online"], [])

        # clear and rebuild if state changed
        if new_memory != self.last_memory:
            self._refresh_grid(peers_data)
            self.last_memory = new_memory

            app.storage.user["cached_peers_data"] = peers_data

        return None
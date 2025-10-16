# A tailscale hub/directory

I decided to make a tailscale hub to direct me to open ports on my tailscale systems, so I didn't have to try remembering which services were active. I also didn't want to log into the tailscale website and check the services.

This project uses NiceGUI and requires Python >= 3.10.

## Setup

1. Create a virtual environment, and install the requirements:
```
python3 -m venv .venv
pip install -r requirements.txt
```

2. Install `nmap` through your package distributor (`yay -S nmap` for arch)

3. Start the app (optionally append a custom port):
```
python main.py [PORT]
```

## Configurations
Configurations are stored in the `config.toml` file, and all the variables should be self explanatory along with the comments provided.

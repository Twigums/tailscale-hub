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

## Setup (NixOS)

1. Move/copy `.nix` files in `./nix` to `/etc/nixos/`. Please make sure to change the variable name, `path_to_folder` in `./nix/tailscale-hub.nix`. This variable should be set to the folder where this `README.md` exists.

2. Add these files as imports to your configuration file, `/etc/nixos/configuration.nix`.

3. Change permissions if needed:

```
sudo chmod +x /home/{user}
sudo chmod +x /home/{user}/git
```

4. App should run on port `80/8080` with `nginx` after running:

```
sudo nixos-rebuild switch
```

## Configurations
Configurations are stored in the `config.toml` file, and all the variables should be self explanatory along with the comments provided.

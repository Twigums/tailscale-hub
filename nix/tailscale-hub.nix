{ config, pkgs, ... }:

let

  # path to this folder
  # dont forget to set this before running on nix
  path_to_folder = "";
in
{
  systemd.services.nicegui-app = {
    description = "NiceGUI - Tailscale Hub";
    after = [ "network.target" ];
    wantedBy = [ "multi-user.target" ];

    path = with pkgs; [
      tailscale
      nmap
    ];
    
    serviceConfig = {
      ExecStart = "${pkgs.python3.withPackages (ps: [ ps.nicegui ])}/bin/python ${path_to_folder}/main.py";
      WorkingDirectory = "${path_to_folder}";
      Restart = "always";
      User = "nicegui";
      Group = "nicegui";
      NoNewPrivileges = true;
      PrivateTmp = true;
    };
    
    environment = {
      NICEGUI_PORT = "8080";
    };
  };
  
  # tailscale hub requires nmap for port checking
  environment.systemPackages = with pkgs; [ nmap ];

  users.users.nicegui = {
    isSystemUser = true;
    group = "nicegui";
  };

  users.groups.nicegui = {};

}

# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running ‘nixos-help’).

{ config, pkgs, ... }:

{
  system.nixos.label = "-";

  services.xserver.enable = true;
  services.power-profiles-daemon.enable = true;
  services.displayManager.ly.enable = true;
  services.gvfs.enable = true;
  services.udisks2.enable = true;


  hardware.nvidia.package = config.boot.kernelPackages.nvidiaPackages.stable;
  hardware.graphics.enable = true;

  services.xserver.videoDrivers = ["nvidia"];

  hardware.nvidia = {
    modesetting.enable = true;
    powerManagement.enable = false;
    open = false;
    nvidiaSettings = true;
  };

  boot.extraModulePackages = with config.boot.kernelPackages; [
    v4l2loopback
  ];
  boot.kernelModules = [ "v4l2loopback" ];
  boot.extraModprobeConfig = ''
    options v4l2loopback exclusive_caps=1 card_label="DroidCam"
  '';

  programs.adb.enable = true;

  environment.sessionVariables = {
    WLR_NO_HARDWARE_CURSORS = "1";
    NIXOS_OZONE_WL = "1";
  };

  hardware.bluetooth.enable = true;
  services.blueman.enable = true;

  services.flatpak.enable = true;

  services.pipewire = {
    enable = true;
    pulse.enable = true; # For PulseAudio compatibility
    alsa.enable = true;
    jack.enable = true;
  };

  services.logind.settings.Login.HandleLidSwitch = "suspend";
  services.logind.settings.Login.HandleLidSwitchExternalPower = "suspend";

  services.displayManager.defaultSession = "hyprland";

  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  programs.hyprland.enable = true;

  environment.etc."inputrc".text = ''
      set bell-style none
  '';

  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.systemd-boot.configurationLimit = 2;

  #Kernel Parameters
  boot.kernelParams = [ 	
  	"mem_sleep_default=deep" 
	"quiet" 
    	"splash" 
    	"boot.shell_on_fail" 
    	"loglevel=3" 
    	"rd.systemd.show_status=false" 
    	"rd.udev.log_level=3" 
    	"udev.log_priority=3"
  ];

  #silencing the console (grub)
  boot.consoleLogLevel = 0;

  #hiding the stages of Nix OS
  boot.initrd.verbose = false;

  networking.hostName = "nixos"; # Define your hostname.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Enable networking
  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "Asia/Ulaanbaatar";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  i18n.extraLocaleSettings = {
    LC_ADDRESS = "mn_MN";
    LC_IDENTIFICATION = "mn_MN";
    LC_MEASUREMENT = "mn_MN";
    LC_MONETARY = "mn_MN";
    LC_NAME = "mn_MN";
    LC_NUMERIC = "mn_MN";
    LC_PAPER = "mn_MN";
    LC_TELEPHONE = "mn_MN";
    LC_TIME = "en_US.UTF-8";
  };

  # Configure keymap in X11
  services.xserver.xkb = {
    layout = "us";
    variant = "";
  };

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.me = {
    isNormalUser = true;
    description = "Me";
    extraGroups = [ "networkmanager" "wheel" "adbusers" ];
    packages = with pkgs; [];
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  services.xserver.excludePackages = [ pkgs.xterm ];

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
     #hyprland essentials
     waybar 
     hyprpaper 
     hyprlock
     hyprshot
     usbutils
     nautilus  
     kitty
     pamixer
     brightnessctl
     pavucontrol

     #apps
     firefox
     dropbox
     tmux
     onlyoffice-desktopeditors
     ranger
     kdePackages.okular
     image-roll
     obsidian
     spotify
     vscode

     #appearance/usability
     cava
     rofi
     rofimoji
     nwg-look
     papirus-icon-theme
     droidcam
     phinger-cursors
     cowsay
     catppuccin-gtk
     fortune
     tree-sitter
     python3
     lua
     lua52Packages.luarocks
     
     #clipboard
     cliphist
     wl-clipboard

     #notifications
     swaynotificationcenter
     notify-desktop

     #other essentials (for me)
     git
     gcc
     ani-cli
     bc
     openjdk21
     btop
     playerctl
     entr
  #  vim # Do not forget to add an editor to edit configuration.nix! The Nano editor is also installed by default.
  #  wget
  ];
	
  fonts = {
     enableDefaultPackages = true;
     packages = with pkgs; [
	noto-fonts
	noto-fonts-cjk-sans
	noto-fonts-color-emoji
	liberation_ttf
	fira-code
	fira-code-symbols
	nerd-fonts.fira-code
	nerd-fonts.jetbrains-mono
     ];
  };

  fonts.fontconfig.useEmbeddedBitmaps = true;
	
  programs.neovim = {
	  enable = true;
  };

# Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # List services that you want to enable:

  # Enable the OpenSSH daemon.
  # services.openssh.enable = true;

  # Open ports in the firewall.
   networking.firewall.allowedTCPPorts = [ 22 80 443 17500 4747 ];
   networking.firewall.allowedUDPPorts = [ 53 17500 4747 ];
  # Or disable the firewall altogether.
   networking.firewall.enable = true;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "25.11"; # Did you read the comment?

}

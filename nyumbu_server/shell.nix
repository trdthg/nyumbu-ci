let
  pkgs = import
    (fetchTarball "https://nixos.org/channels/nixos-unstable/nixexprs.tar.xz")
    { };
in pkgs.mkShell {
  nativeBuildInputs = with pkgs; [
    ### dev tool
    # python311Packages.tinydb
    # python311Packages.flask
    pdm
    socat
    minicom
    file

    ### build(lib)
    # libudev-sys: find libudev
    pkg-config
    # libudev-sys: contains libudev
    systemd.dev
    # openssl-sys: ssh2
    openssl.dev
    # libvirt api
    libvirt
    virt-manager
    virt-viewer
  ];
  buildInputs = with pkgs; [ ];
  shellHook = ''
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${
      pkgs.lib.makeLibraryPath [

      ]
    }"
  '';
}

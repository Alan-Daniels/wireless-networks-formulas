{
  description = "Generate question & answer sheets for Wireless and Mobile Networks";

  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-unstable;
    utils.url = github:numtide/flake-utils;
  };

  # This is for running on X86-64 Linux (the norm), Intel and M1 Macs.
  outputs = { self, nixpkgs, ... }@inputs: inputs.utils.lib.eachSystem [
    "x86_64-linux"
    "x86_64-darwin"
    "aarch64-darwin"
  ]
    (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pylatex = with pkgs.python311Packages;
          buildPythonPackage rec {
            pname = "pylatex";
            version = "1.4.2";
            src = fetchPypi {
              inherit pname version;
              sha256 = ""; # TODO
            };
            buildInputs = inputs;
          };
        inputs = with pkgs;
          [
            python311
            python311Packages.pylatex # added above
            texliveFull
          ];
      in
      {
        devShells.default =
          pkgs.mkShell rec {
            buildInputs = inputs;
          };
        packages.default =
          with pkgs.python311Packages;
          buildPythonPackage rec {
            pname = "wireless-networks-formulas";
            version = "0.1";
            src = ./.;
            buildInputs = inputs;
            propagatedBuildInputs = inputs;
            preBuild = ''
              cat > requirements.txt << EOF
              pylatex
              EOF
              cat > setup.py << EOF
              from setuptools import setup

              with open('requirements.txt') as f:
                install_requires = f.read().splitlines()

              setup(
                name='${pname}',
                version='${version}',
                scripts=['main.py'],
                install_requires=install_requires,
              )
              EOF
            '';
            postInstall = "mv -v $out/bin/main.py $out/bin/wireless-networks-formulas";
          };
      }
    );
}

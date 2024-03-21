Generate question & answer sheets for Wireless and Mobile Networks

## Dependancy Management
If you'd like to run this project, you will need to [install nix](https://nixos.org/download/) and [enable flakes](https://nixos.wiki/wiki/Flakes).

## Running

```sh
cd <where-you-would-like-pdfs>
nix run github:Alan-Daniels/wireless-networks-formulas
```

the outputs will be in `./build`.

## Developing

```sh
git clone https://github.com/Alan-Daniels/wireless-networks-formulas.git
cd wireless-networks-formulas
nix develop
```

which will give you a shell with all the dependancies available.

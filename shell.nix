# shell.nix
{ pkgs ? import <nixpkgs> {} }:
let
  my-python-packages = ps: with ps; [
    z3
    pysmt
    numpy
    pandas
  ];
  my-python = pkgs.python310.withPackages my-python-packages;
in my-python.env

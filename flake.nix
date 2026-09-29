{
  description = "Reproducible environment for the NeuroPET workshop and finished notebook";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  outputs = { self, nixpkgs }:
    let
      systems = [ "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python313.withPackages (ps: with ps; [
            numpy scipy matplotlib nibabel scikit-image templateflow
            nbformat nbclient ipykernel ipywidgets pytest jupyterlab
          ]);
        in {
          default = pkgs.mkShell {
            packages = [ python ];
          };
        });
    };
}

{
  description = "fastmcp-template - Cookiecutter template for FastMCP servers";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
        };

        fhsEnv = pkgs.buildFHSEnv {
          name = "fastmcp-template-dev-env";

          targetPkgs = pkgs':
            with pkgs'; [
              # Python and uv
              python312
              uv

              # Template generation
              cookiecutter

              # System libraries
              zlib
              stdenv.cc.cc.lib

              # Shells
              zsh
              bash

              # Development tools
              git
              git-lfs
              curl
              wget
              jq
              tree
            ];

          profile = ''
            echo "🍪 fastmcp-template Development Environment"
            echo "==========================================="
            echo ""
            echo "This is the template repository development environment."
            echo "Use 'cookiecutter' to test template generation."
            echo ""
            echo "✅ Python:       $(python --version)"
            echo "✅ uv:           $(uv --version)"
            echo "✅ cookiecutter: $(cookiecutter --version | head -n1)"
            echo ""
          '';

          runScript = ''
            # Set shell for the environment
            SHELL=''${pkgs.zsh}/bin/zsh

            echo "🍪 Template Development Quick Reference:"
            echo ""
            echo "🧪 Test Template Generation:"
            echo "  cookiecutter . --no-input                      - Generate with defaults"
            echo "  cookiecutter . --output-dir /tmp/test-gen      - Generate to specific dir"
            echo "  cookiecutter .                                 - Interactive mode"
            echo ""
            echo "🔍 Verify Generated Project:"
            echo "  cd <generated-project>"
            echo "  uv sync                                        - Install dependencies"
            echo "  uv run pytest                                  - Run tests"
            echo "  uv run ruff check .                            - Lint code"
            echo ""
            echo "📝 Template Files:"
            echo "  cookiecutter.json                              - Template variables"
            echo "  hooks/post_gen_project.py                      - Post-generation automation"
            echo "  {{cookiecutter.project_slug}}/                 - Template directory"
            echo ""
            echo "🚀 Ready to develop templates!"
            echo ""

            # Start zsh shell
            exec ''${pkgs.zsh}/bin/zsh
          '';
        };
      in {
        devShells.default = pkgs.mkShell {
          shellHook = ''
            exec ''${fhsEnv}/bin/fastmcp-template-dev-env
          '';
        };

        packages.default = pkgs.python312;
      }
    );
}

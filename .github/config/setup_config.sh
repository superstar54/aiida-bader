verdi computer setup -n --config localhost-setup.yaml
verdi computer configure core.local localhost -n --config localhost-config.yaml
verdi code create core.code.installed -n --config code-bader.yaml --filepath-executable $(which bader.x)

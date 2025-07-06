param (
    [string]$Command
)

# Execute the command in Ubuntu WSL
wsl -d Ubuntu-22.04 -- bash -c "$Command"

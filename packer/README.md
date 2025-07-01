# PDF Chat Appliance OVA Build

## Prerequisites

- VMware Workstation/Player or VMware Fusion
- Packer installed (v1.8.0+)
- Internet connection for ISO download

## Build Instructions

1. **Update ISO checksum:**
   ```bash
   cd packer
   # Download Ubuntu 24.04 ISO and get checksum
   curl -O https://releases.ubuntu.com/24.04/ubuntu-24.04.3-live-server-amd64.iso
   sha256sum ubuntu-24.04.3-live-server-amd64.iso
   # Update the checksum in ubuntu-template.pkr.hcl
   ```

2. **Build the OVA:**
   ```bash
   packer init ubuntu-template.pkr.hcl
   packer build ubuntu-template.pkr.hcl
   ```

3. **Output:**
   - OVA file: `output-vmware-iso/pdf-chat-appliance.ova`
   - Import into VMware/Proxmox

## Manual Testing

1. **Import OVA** into VMware Workstation/Player
2. **Start VM** and wait for boot
3. **Access WebUI** at `http://<VM_IP>`
4. **Test CLI:**
   ```bash
   ssh ubuntu@<VM_IP>
   pdfchat version
   pdfchat config show
   ```

## Troubleshooting

- **Boot issues:** Check VMware network settings
- **Service not starting:** Check logs with `sudo journalctl -u pdfchat`
- **WebUI not accessible:** Verify nginx is running

## Customization

- Modify `vmx_data` for different network configurations
- Update `preseed.cfg` for different installation options
- Adjust VM specs in the template 
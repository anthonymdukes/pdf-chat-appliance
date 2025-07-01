packer {
  required_plugins {
    vmware = {
      version = "~> 1.0"
      source  = "github.com/hashicorp/vmware"
    }
  }
}

variable "vm_name" {
  type    = string
  default = "pdf-chat-appliance"
}

variable "iso_url" {
  type    = string
  default = "https://releases.ubuntu.com/24.04/ubuntu-24.04.3-live-server-amd64.iso"
}

variable "iso_checksum" {
  type    = string
  default = "sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}

source "vmware-iso" "ubuntu" {
  iso_url          = var.iso_url
  iso_checksum     = var.iso_checksum
  output_directory = "output-vmware-iso"
  vm_name          = var.vm_name
  
  guest_os_type = "ubuntu-64"
  
  cpus   = 2
  memory = 4096
  
  disk_size         = 25600
  disk_type_id      = 0
  disk_adapter_type = "lsisas1068"
  
  network_name = "VM Network"
  network_adapter_type = "e1000"
  
  http_directory = "http"
  http_port_min  = 8000
  http_port_max  = 8000
  
  ssh_username = "ubuntu"
  ssh_password = "ubuntu"
  ssh_timeout  = "30m"
  
  boot_wait = "10s"
  
  boot_command = [
    "<esc><wait>",
    "<esc><wait>",
    "<enter><wait>",
    "/install/vmlinuz",
    " auto=true",
    " url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/preseed.cfg",
    " debian-installer=en_US locale=en_US keymap=us",
    " hostname=pdfchat-appliance",
    " fb=false",
    " debconf/frontend=noninteractive",
    " keyboard-configuration/modelcode=SKIP keyboard-configuration/layout=USA",
    " keyboard-configuration/variant=USA console-setup/ask_detect=false",
    " initrd=/install/initrd.gz",
    " quiet",
    " ---",
    "<enter>"
  ]
  
  shutdown_command = "echo 'ubuntu' | sudo -S shutdown -P now"
  
  vmx_data = {
    "ethernet0.present" = "TRUE"
    "ethernet0.connectionType" = "bridged"
    "ethernet0.virtualDev" = "e1000"
    "ethernet0.wakeOnPcktRcv" = "FALSE"
    "ethernet0.addressType" = "generated"
    "ethernet0.linkStatePropagation.enable" = "TRUE"
    "ethernet0.bsdName" = "en0"
    "ethernet0.displayName" = "Ethernet"
    "ethernet0.uptCompatibility" = "TRUE"
    "ethernet0.uptv2.enable" = "TRUE"
  }
  
  vmx_data_post = {
    "ethernet0.pciSlotNumber" = "32"
    "ethernet0.generatedAddress" = "00:0c:29:00:00:00"
    "ethernet0.generatedAddressOffset" = "0"
  }
}

build {
  sources = ["source.vmware-iso.ubuntu"]
  
  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get install -y python3 python3-pip python3-venv nginx",
      "sudo systemctl enable nginx",
      "sudo systemctl start nginx"
    ]
  }
  
  provisioner "file" {
    source = "../"
    destination = "/tmp/pdf-chat-appliance"
  }
  
  provisioner "shell" {
    inline = [
      "sudo mv /tmp/pdf-chat-appliance /opt/",
      "sudo chown -R ubuntu:ubuntu /opt/pdf-chat-appliance",
      "cd /opt/pdf-chat-appliance",
      "python3 -m venv venv",
      "source venv/bin/activate",
      "pip install -r requirements.txt"
    ]
  }
  
  provisioner "shell" {
    script = "../scripts/setup.sh"
  }
} 
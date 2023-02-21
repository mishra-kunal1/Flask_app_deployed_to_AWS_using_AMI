variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "source_ami" {
  type    = string
  default = "ami-08c40ec9ead489470" # Ubuntu 22.04 LTS
}

variable "ssh_username" {
  type    = string  
  default = "ubuntu"
}

variable "subnet_id" {
  type    = string
  default = "subnet-0c571b419f5726fd8"
  
}

variable "ami_user"{
  type    = string
  default = "031887029695"
}
# https://www.packer.io/plugins/builders/amazon/ebs
source "amazon-ebs" "my-ami" {
  region     = "${var.aws_region}"
  ami_name        = "custom_ami_${formatdate("YYYY_MM_DD_hh_mm_ss", timestamp())}"
  ami_description = "AMI for Demo"
  ami_users= ["${var.ami_user}"]
  ami_regions = [
    "us-east-1",
  ]
  

  aws_polling {
    delay_seconds = 15
    max_attempts  = 60
  }


  instance_type = "t2.micro"
  source_ami    = "${var.source_ami}"
  ssh_username  = "${var.ssh_username}"
  subnet_id     = "${var.subnet_id}"

  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/sda1"
    volume_size           = 8
    volume_type           = "gp2"
  }
}


build {
  sources = ["source.amazon-ebs.my-ami"]

  provisioner "file" {
    
    source      = "webapp.zip"
    
    destination = "/home/ubuntu/webapp.zip"
  }

  provisioner "file" {
    source      = "nginx_config"
    destination ="/tmp/nginx_config"
    #destination = "/etc/nginx/sites-available/default"
  }
   provisioner "file" {
    source      = "service_file.service"
    destination ="/tmp/service_file.service"
    #destination = "/etc/systemd/system/service_file.service"
  }

  provisioner "shell" {
    script ="app.sh"
 }
 post-processor "manifest" {
    output = "manifest.json"
    strip_path = true
 }
}

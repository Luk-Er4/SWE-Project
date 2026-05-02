### Main VPC
resource "aws_vpc" "main" {
  cidr_block = "10.1.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  
  tags = {
    Name = "vpc-health-sys-ec2"
  }
}

### Security Group for EC2
resource "aws_security_group" "ec2_api" {
  name        = "security-group-ec2-health-sys-api"
  description = "sg for ec2 api"
  vpc_id      = aws_vpc.main.id
}

# Inbound Rule 1 (FastAPI) - EC2
resource "aws_vpc_security_group_ingress_rule" "ec2_api_fastapi" {
  security_group_id = aws_security_group.ec2_api.id

  ip_protocol = "tcp"
  from_port   = 8000
  to_port     = 8000

  cidr_ipv4 = "0.0.0.0/0"
}

# Inbound Rule 2 (SSH) - EC2
resource "aws_vpc_security_group_ingress_rule" "ec2_api_ssh" {
  security_group_id = aws_security_group.ec2_api.id

  ip_protocol = "tcp"
  from_port   = 22
  to_port     = 22

  cidr_ipv4 = "0.0.0.0/0"
}

# Outbound Rule 1 - EC2
resource "aws_vpc_security_group_egress_rule" "ec2_api_out" {
  security_group_id = aws_security_group.ec2_api.id

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"
}

### Security Group for RDS
resource "aws_security_group" "sg_rds" {
  name        = "security-group-rds-health-sys"
  description = "sg for rds"
  vpc_id      = aws_vpc.main.id
}

# Inbound Rule 1 (MySQL/Aurora 3306) - RDS
resource "aws_vpc_security_group_ingress_rule" "rds_in" {
  security_group_id = aws_security_group.sg_rds.id

  ip_protocol = "tcp"
  from_port   = 3306
  to_port     = 3306

  cidr_ipv4 = "0.0.0.0/0"
}

# Outbound Rule 1 - RDS
resource "aws_vpc_security_group_egress_rule" "rds_out" {
  security_group_id = aws_security_group.sg_rds.id

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"
}

### Subnets 
# Public Subnets
resource "aws_subnet" "pub_1_health" { 
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.1.1.0/24"
    availability_zone = "us-east-1a"
    map_public_ip_on_launch = true
    tags = {
        Name = "subnet-pub-health-sys-1"
    }
}

resource "aws_subnet" "pub_2_health" { 
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.1.2.0/24"
    availability_zone = "us-east-1b"
    map_public_ip_on_launch = true
    tags = {
        Name = "subnet-pub-health-sys-2"
    }
}

# Private Subnets
resource "aws_subnet" "prv_1_health" { 
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.1.11.0/24"
    availability_zone = "us-east-1a"
    tags = {
        Name = "subnet-prv-health-sys-1"
    }
}

resource "aws_subnet" "prv_2_health" { 
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.1.12.0/24"
    availability_zone = "us-east-1b"
    tags = {
        Name = "subnet-prv-health-sys-2"
    }
}

### Internet Gateway
resource "aws_internet_gateway" "igw_health" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "igw-health-sys"
    }
}

### Route Tables and Associations
# Route Table(Public) <- Internet Gateway
resource "aws_route_table" "pub_health" {
    vpc_id = aws_vpc.main.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw_health.id
    }

    tags = {
        "Name" = "health-sys-rtb-public" 
    }
}

# Route Table (Private) <- X
#resource "aws_route_table" "prv_health" {
#    vpc_id = aws_vpc.main.id
#}

# Subnet(Public 1) <- Route Table 
resource "aws_route_table_association" "pub_1_health" {
    subnet_id      = aws_subnet.pub_1_health.id
    route_table_id = aws_route_table.pub_health.id
}

# Subnet(Public 2) <- Route Table 
resource "aws_route_table_association" "pub_2_health" {
    subnet_id      = aws_subnet.pub_2_health.id
    route_table_id = aws_route_table.pub_health.id
}

### DB Subent Group
resource "aws_db_subnet_group" "main" {
    description             = "subnet for rds user"
    name                    = "rds-subnet-sql-health-sys"
    name_prefix             = null
    subnet_ids              = [
        aws_subnet.pub_1_health.id,
        aws_subnet.pub_2_health.id,
    ]
}

### RDS Instance
resource "aws_db_instance" "health_db" {
    allocated_storage                     = 20
    availability_zone                     = "us-east-1a"
    backup_retention_period               = 1
    backup_target                         = "region"
    backup_window                         = "03:54-04:24"
    ca_cert_identifier                    = "rds-ca-rsa2048-g1"
    character_set_name                    = null
    copy_tags_to_snapshot                 = true
    custom_iam_instance_profile           = null
    customer_owned_ip_enabled             = false
    database_insights_mode                = "standard"
    db_name                               = null
    db_subnet_group_name                  = aws_db_subnet_group.main.name
    dedicated_log_volume                  = false
    delete_automated_backups              = true
    deletion_protection                   = false
    domain                                = null
    domain_auth_secret_arn                = null
    domain_fqdn                           = null
    domain_iam_role_name                  = null
    domain_ou                             = null
    enabled_cloudwatch_logs_exports       = []
    engine                                = "mysql"
    engine_lifecycle_support              = "open-source-rds-extended-support-disabled"
    engine_version                        = "8.4.8"
    iam_database_authentication_enabled   = false
    identifier                            = "db-rds-health-sys"
    identifier_prefix                     = null
    instance_class                        = "db.t4g.micro"
    iops                                  = 0
    kms_key_id                            = "arn:aws:kms:us-east-1:077369590118:key/38c093fe-6c39-48e9-82a5-1431b3f41472"
    license_model                         = "general-public-license"
    maintenance_window                    = "tue:08:19-tue:08:49"
    max_allocated_storage                 = 1000
    monitoring_interval                   = 0
    monitoring_role_arn                   = null
    multi_az                              = false
    nchar_character_set_name              = null
    network_type                          = "IPV4"
    option_group_name                     = "default:mysql-8-4"
    parameter_group_name                  = "default.mysql8.4"
    password                              = var.db_password
    performance_insights_enabled          = false
    performance_insights_kms_key_id       = null
    performance_insights_retention_period = 0
    port                                  = 3306
    publicly_accessible                   = true
    replica_mode                          = null
    replicate_source_db                   = null
    skip_final_snapshot                   = true
    storage_encrypted                     = true
    storage_throughput                    = 0
    storage_type                          = "gp2"
    timezone                              = null
    username                              = "admin"
    vpc_security_group_ids                = [
        aws_security_group.sg_rds.id,
    ]
    depends_on = [
    aws_db_subnet_group.main
  ]
}

### EC2 Instance
resource "aws_instance" "ec2_api" {
  ami                         = "ami-098e39bafa7e7303d"
  hibernation                 = false
  instance_type               = "t3.nano"
  key_name                    = "key-pair-ec2-health-sys-api"
  user_data_replace_on_change = false
  iam_instance_profile        = "instanceRole"
  subnet_id = aws_subnet.pub_1_health.id

  vpc_security_group_ids = [
    aws_security_group.ec2_api.id
  ]

  user_data = templatefile("${path.module}/deploy.sh", {
    aws_region   = "us-east-1"
    ecr_image_uri = var.ecr_image_uri
    db_host      = aws_db_instance.health_db.address
    db_name      = var.db_name
    db_user      = var.db_user
    db_password  = var.db_password
  })

  credit_specification {
    cpu_credits = "unlimited"
  }

  tags = {
    Name = "ec2-vm-health-sys-api"
  }

  lifecycle {
    ignore_changes = [
      user_data,
      user_data_base64,
    ]
  }
}


### Main VPC
resource "aws_vpc" "main" {
  cidr_block = "10.1.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  
  tags = {
    Name = "vpc-health-sys-ec2"
  }
}

### sg for sys-api
resource "aws_security_group" "ec2_sys_api" {
  name        = "security-group-ec2-health-sys-api"
  description = "sg for ec2 sys-api"
  vpc_id      = aws_vpc.main.id
}

# Inbound Rule 1 (FastAPI) - EC2
resource "aws_vpc_security_group_ingress_rule" "ec2_sys_api_in_fastapi" {
  security_group_id = aws_security_group.ec2_sys_api.id

  ip_protocol = "tcp"
  from_port   = var.port_sys_api
  to_port     = var.port_sys_api

  referenced_security_group_id = aws_security_group.sg_react_to_api.id # from alb sg
}

# Inbound Rule 2 (SSH) - EC2
resource "aws_vpc_security_group_ingress_rule" "ec2_sys_api_in_ssh" {
  security_group_id = aws_security_group.ec2_sys_api.id

  ip_protocol = "tcp"
  from_port   = 22
  to_port     = 22

  cidr_ipv4 = "0.0.0.0/0"
}

# Outbound Rule 1 - EC2
resource "aws_vpc_security_group_egress_rule" "ec2_sys_api_out_all" {
  security_group_id = aws_security_group.ec2_sys_api.id

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"
}

### sg for data-api
resource "aws_security_group" "ec2_data_api" {
  name        = "security-group-ec2-health-data-api"
  description = "sg for ec2 data-api"
  vpc_id      = aws_vpc.main.id
}

# Inbound Rule 1 (FastAPI) - EC2
resource "aws_vpc_security_group_ingress_rule" "ec2_data_api_in_fastapi" {
  security_group_id = aws_security_group.ec2_data_api.id

  ip_protocol = "tcp"
  from_port   = var.port_data_api
  to_port     = var.port_data_api

  referenced_security_group_id = aws_security_group.sg_react_to_api.id # from alb sg
}

# Inbound Rule 2 (SSH) - EC2
resource "aws_vpc_security_group_ingress_rule" "ec2_data_api_in_ssh" {
  security_group_id = aws_security_group.ec2_data_api.id

  ip_protocol = "tcp"
  from_port   = 22
  to_port     = 22

  cidr_ipv4 = "0.0.0.0/0"
}

# Outbound Rule 1 - EC2
resource "aws_vpc_security_group_egress_rule" "ec2_data_api_out_all" {
  security_group_id = aws_security_group.ec2_data_api.id

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"
}


### Security Group for RDS (Shared for sys & data)
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
    name                    = "rds-subnet-sql-health-sys" # shared with rds-data
    name_prefix             = null
    subnet_ids              = [
        aws_subnet.pub_1_health.id,
        aws_subnet.pub_2_health.id,
    ]
}

### RDS Instance (sys-db)
resource "aws_db_instance" "health_sys_db" {
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

### RDS Instance (data-db)
resource "aws_db_instance" "health_data_db" {
    allocated_storage                     = 20
    availability_zone                     = "us-east-1a"
    backup_retention_period               = 1
    backup_target                         = "region"
    backup_window                         = "05:56-06:26"
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
    identifier                            = "db-rds-health-data"
    identifier_prefix                     = null
    instance_class                        = "db.t4g.micro"
    iops                                  = 0
    kms_key_id                            = "arn:aws:kms:us-east-1:077369590118:key/38c093fe-6c39-48e9-82a5-1431b3f41472"
    license_model                         = "general-public-license"
    maintenance_window                    = "mon:09:35-mon:10:05"
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

### EC2 (sys-api)
resource "aws_instance" "ec2_vm_sys_api" {
  ami                         = "ami-098e39bafa7e7303d"
  hibernation                 = false
  instance_type               = "t3.nano"
  key_name                    = "key-pair-ec2-health-sys-api" # shared with data-api
  user_data_replace_on_change = false
  iam_instance_profile        = "instanceRole"
  subnet_id = aws_subnet.pub_1_health.id

  vpc_security_group_ids = [
    aws_security_group.ec2_sys_api.id
  ]

  user_data = templatefile("${path.module}/deploy.sh", {
    aws_region   = "us-east-1"
    ecr_image_uri = var.ecr_image_uri_sys_api
    db_host      = aws_db_instance.health_sys_db.address
    db_name      = var.db_name_sys
    db_user      = var.db_user
    db_password  = var.db_password
    ec2_port_num = var.port_sys_api
    ec2_container_name = var.container_name_sys_api
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

### EC2 (data-api)
resource "aws_instance" "ec2_vm_data_api" {
  ami                         = "ami-098e39bafa7e7303d"
  hibernation                 = false
  instance_type               = "t3.nano"
  key_name                    = "key-pair-ec2-health-sys-api" # shared with sys-api
  user_data_replace_on_change = false
  iam_instance_profile        = "instanceRole"
  subnet_id = aws_subnet.pub_1_health.id

  vpc_security_group_ids = [
    aws_security_group.ec2_data_api.id
  ]

  user_data = templatefile("${path.module}/deploy.sh", {
    aws_region   = "us-east-1"
    ecr_image_uri = var.ecr_image_uri_data_api
    db_host      = aws_db_instance.health_data_db.address
    db_name      = var.db_name_data
    db_user      = var.db_user
    db_password  = var.db_password
    ec2_port_num = var.port_data_api
    ec2_container_name = var.container_name_data_api
  })

  credit_specification {
    cpu_credits = "unlimited"
  }

  tags = {
    Name = "ec2-vm-health-data-api"
  }

  lifecycle {
    ignore_changes = [
      user_data,
      user_data_base64,
    ]
  }
}

### Resources for Application Load Balancer
# sg for alb
resource "aws_security_group" "sg_react_to_api" {
  name        = "security-group-alb-health-react"
  description = "sg for react to amplify"
  vpc_id      = aws_vpc.main.id
}

# Inbound Rule 1 (HTTPS 443) - ALB
resource "aws_vpc_security_group_ingress_rule" "health_alb_in" {
  security_group_id = aws_security_group.sg_react_to_api.id

  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443

  cidr_ipv4 = "0.0.0.0/0"
}

# Outbound Rule 1 - ALB
resource "aws_vpc_security_group_egress_rule" "health_alb_out" {
  security_group_id = aws_security_group.sg_react_to_api.id

  ip_protocol = "-1"

  cidr_ipv4 = "0.0.0.0/0"
}

# Main ALB
resource "aws_lb" "main" {
    name               = "alb-health-sys-react"
    load_balancer_type = "application"
    subnets            = [
        "${aws_subnet.pub_1_health.id}", # us-east-1a public
        "${aws_subnet.pub_2_health.id}"  # us-east-1b public
    ]
    security_groups    = [aws_security_group.sg_react_to_api.id]
}

### ALB Target Groups
# ALB tg (sys-api)
resource "aws_lb_target_group" "health_ec2_sys_api" {
    name        = "tg-health-sys-api"
    port        = 8000
    protocol    = "HTTP"
    vpc_id      = aws_vpc.main.id
    target_type = "instance"

    health_check {
        healthy_threshold   = 5
        interval            = 30
        matcher             = "200"
        path                = "/health"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
    }
}

# ALB tg (data-api)
resource "aws_lb_target_group" "health_ec2_data_api" {
    name        = "tg-health-data-api"
    port        = 8001
    protocol    = "HTTP"
    vpc_id      = aws_vpc.main.id
    target_type = "instance"

    health_check {
        healthy_threshold   = 5
        interval            = 30
        matcher             = "200"
        path                = "/health"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
    }
}

### ALB Listeners
# Default Listener
resource "aws_lb_listener" "https_health_apis" {
    load_balancer_arn = aws_lb.main.arn
    port              = 443
    protocol          = "HTTPS"
    certificate_arn   = var.https_certificate

    default_action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.health_ec2_sys_api.arn
    }
}

# sys-api Listener
resource "aws_lb_listener_rule" "listener_sys_api" {
  listener_arn = aws_lb_listener.https_health_apis.arn
  priority     = 1

  condition {
    host_header {
      values = ["sys-api.health-scoring-system.com"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.health_ec2_sys_api.arn
  }
}

# data-api Listener
resource "aws_lb_listener_rule" "listener_data_api" {
  listener_arn = aws_lb_listener.https_health_apis.arn
  priority     = 2

  condition {
    host_header {
      values = ["data-api.health-scoring-system.com"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.health_ec2_data_api.arn
  }
}

# Attach sys-api as target
resource "aws_lb_target_group_attachment" "sys_api" {
  target_group_arn = aws_lb_target_group.health_ec2_sys_api.arn
  target_id        = aws_instance.ec2_vm_sys_api.id
  port             = 8000
}

# Attach data-api as target
resource "aws_lb_target_group_attachment" "data_api" {
  target_group_arn = aws_lb_target_group.health_ec2_data_api.arn
  target_id        = aws_instance.ec2_vm_data_api.id
  port             = 8001
}

# Route 53 Sub DNS name
resource "aws_route53_record" "sys_api" {
  zone_id = var.zone_id
  name    = "sys-api.health-scoring-system.com"
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "data_api" {
  zone_id = var.zone_id
  name    = "data-api.health-scoring-system.com"
  type    = "A"

  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}
# ECS Cluster
resource "aws_ecs_cluster" "main" {
   name = "ecr-cluster-${var.project_name}"

    configuration {
        execute_command_configuration {
        logging = "DEFAULT"
        }
    }
}

resource "aws_ecs_service" "app" {
    name                          = "${var.task_definition_name}-${var.project_name}-service-run-damn-task"
    cluster                       = aws_ecs_cluster.main.id
    desired_count                 = 1
    task_definition               = aws_ecs_task_definition.app.arn
    launch_type                   = "FARGATE"
    enable_ecs_managed_tags       = true
    availability_zone_rebalancing = "ENABLED"

    deployment_circuit_breaker {
        enable   = true
        rollback = true
    }

    load_balancer {
        target_group_arn = aws_lb_target_group.health_fargate_api.arn
        container_name   = "container-${var.project_name}"
        container_port   = 8000
    }

    network_configuration {
        subnets          = [aws_subnet.pub_1_health.id, aws_subnet.pub_2_health.id]
        security_groups  = [aws_security_group.sg_fargate_health.id]
        assign_public_ip = true
    }

    depends_on = [aws_lb_listener.http_health]
}

# Task Definition (in ECS Cluster)
resource "aws_ecs_task_definition" "app" {
    family                = "${var.task_definition_name}-${var.project_name}"
    cpu                   = "512"
    memory                = "1024"
    network_mode          = "awsvpc"
    execution_role_arn    = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/ecsTaskExecutionRole"
    task_role_arn         = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/ecsTaskExecutionRole"
    requires_compatibilities = [
        "FARGATE",
    ]
    runtime_platform { 
        cpu_architecture        = "X86_64"   
        operating_system_family = "LINUX"   
    }
  container_definitions = jsonencode([
        {
            "name" = "container-${var.project_name}",
            "image" = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_name}/api:v3",
            "portMappings": [
                {
                    "containerPort" = 8000,
                    "hostPort" = 8000,
                    "protocol" = "tcp",
                    "name" = "container-${var.project_name}-8000-tcp",
                    "appProtocol" = "http"
                }
            ],
            "essential" = true,
            "environment" = [],
            "environmentFiles" = [],
            "mountPoints" = [],
            "volumesFrom" = [],
            "ulimits" = [],
            "logConfiguration" = {
                "logDriver" = "awslogs",
                "options" = {
                    "awslogs-group" = "/ecs/${var.task_definition_name}-${var.project_name}",
                    "awslogs-create-group" = "true",
                    "awslogs-region" = "${var.aws_region}",
                    "awslogs-stream-prefix" = "ecs"
                },
                "secretOptions" = []
            },
            "systemControls" = []
        }
    ])
}

# ALB
resource "aws_lb" "main" {
    name               = "alb-health-sys"
    load_balancer_type = "application"
    subnets            = [
        "${aws_subnet.pub_1_health.id}", # us-east-1b public
        "${aws_subnet.pub_2_health.id}"  # us-east-1a public
    ]
    security_groups    = [aws_security_group.sg_alb_health.id]
}

# ALB Target groups
resource "aws_lb_target_group" "health_fargate_api" {
    name        = "tg-health-sys"
    port        = 8000
    protocol    = "HTTP"
    vpc_id      = aws_vpc.main.id
    target_type = "ip"

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

# ALB Listener
resource "aws_lb_listener" "http_health" {
    load_balancer_arn = aws_lb.main.arn
    port              = 80
    protocol          = "HTTP"

    default_action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.health_fargate_api.arn
    }
}

# Security Groups (1. alb sg)
resource "aws_security_group" "sg_alb_health" {
    name        = "security-group-alb-health-sys"
    description = "sg for alb"
    vpc_id      = aws_vpc.main.id

    ingress { 
        cidr_blocks      = [
            "0.0.0.0/0",
        ]
        from_port        = 80
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "tcp"
        security_groups  = []
        self             = false
        to_port          = 80
    }

    egress {
        cidr_blocks      = [
            "0.0.0.0/0",
        ]
        from_port        = 0
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "-1"
        security_groups  = []
        self             = false
        to_port          = 0
    }
}

# Security Groups (2. rds sg)
resource "aws_security_group" "sg_rds_health" {
    name        = "security-group-rds-health-sys"
    description = "sg for rds"
    vpc_id      = aws_vpc.main.id

    ingress {
        cidr_blocks      = []
        from_port        = 3306
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "tcp"
        security_groups  = [aws_security_group.sg_fargate_health.id]
        self             = false
        to_port          = 3306
    }

    egress {
        cidr_blocks      = [
            "0.0.0.0/0",
        ]
        from_port        = 0
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "-1"
        security_groups  = []
        self             = false
        to_port          = 0
    }
}

# Security Groups (3. fargate sg)
resource "aws_security_group" "sg_fargate_health" { 
    name        = "security-group-fargate-health-sys"
    description = "sg for fargate"
    vpc_id      = aws_vpc.main.id

    ingress {
        cidr_blocks      = []
        from_port        = 8000
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "tcp"
        security_groups  = [
            aws_security_group.sg_alb_health.id,
        ]
        self             = false
        to_port          = 8000
    }

    egress {
        cidr_blocks      = [
            "0.0.0.0/0",
        ]
        from_port        = 0
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "-1"
        security_groups  = []
        self             = false
        to_port          = 0
    }
}

# VPC MAIN
resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
    tags       = {
        "Name" = "vpc-health-sys"
    }
}

# Internet Gateways
resource "aws_internet_gateway" "igw_health" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "igw-health-sys"
    }
}

# Subnets (1. public-1)
resource "aws_subnet" "pub_1_health" { 
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.1.0/24"
    availability_zone = "us-east-1a"
    map_public_ip_on_launch     = true
    tags = {
        Name = "subnet-pub-health-sys-1"
    }
}

# Subnets (2. public-2)
resource "aws_subnet" "pub_2_health" {
    vpc_id            = aws_vpc.main.id
    cidr_block        = "10.0.2.0/24"
    availability_zone = "us-east-1b"
    map_public_ip_on_launch     = true
    tags = {
        Name = "subnet-pub-health-sys-2"
    }
}

# Subnets (3. private-1)
resource "aws_subnet" "prv_1_health" {
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.11.0/24"
    availability_zone       = "us-east-1a"
    map_public_ip_on_launch = false
    tags = {
        Name = "subnet-prv-health-sys-1"
    }
}

# Subnets (4. private-2)
resource "aws_subnet" "prv_2_health" {
    vpc_id                  = aws_vpc.main.id
    cidr_block              = "10.0.12.0/24"
    availability_zone       = "us-east-1b"
    map_public_ip_on_launch = false
    tags = {
        Name = "subnet-prv-health-sys-2"
    }
}

# Route Table(Public) <- Internet Gateway
resource "aws_route_table" "pub_health" {
    vpc_id = aws_vpc.main.id

    route {
        cidr_block = "0.0.0.0/0"
        gateway_id = aws_internet_gateway.igw_health.id
    }

    tags = {
        "Name" = "rtb-health-sys" 
    }
}

# Route Table (Private) <- X
resource "aws_route_table" "prv_health" {
    vpc_id = aws_vpc.main.id
}

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

# Subnet(Private 1) <- Route Table 
#resource "aws_route_table_association" "prv_1_health" {
#  subnet_id      = aws_subnet.prv_1_health.id
#  route_table_id = aws_route_table.prv_health.id
#}

# Subnet(Private 2) <- Route Table 
#resource "aws_route_table_association" "prv_2_health" {
#  subnet_id      = aws_subnet.prv_2_health.id
#  route_table_id = aws_route_table.prv_health.id
#}

resource "aws_db_instance" "health_db" {
    allocated_storage                     = 20
    availability_zone                     = "us-east-1a"
    backup_retention_period               = 1
    backup_target                         = "region"
    backup_window                         = "05:39-06:09"
    ca_cert_identifier                    = "rds-ca-rsa2048-g1"
    character_set_name                    = null
    copy_tags_to_snapshot                 = true
    custom_iam_instance_profile           = null
    customer_owned_ip_enabled             = false
    database_insights_mode                = "standard"
    db_name                               = null
    db_subnet_group_name                  = "rds-subnet-sql-health-sys"
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
    engine_version                        = "8.4.7"
    iam_database_authentication_enabled   = false
    identifier                            = "db-rds-health-sys"
    identifier_prefix                     = null
    instance_class                        = "db.t4g.micro"
    iops                                  = 0
    kms_key_id                            = "arn:aws:kms:us-east-1:077369590118:key/38c093fe-6c39-48e9-82a5-1431b3f41472"
    license_model                         = "general-public-license"
    maintenance_window                    = "sat:08:11-sat:08:41"
    max_allocated_storage                 = 1000
    monitoring_interval                   = 0
    monitoring_role_arn                   = null
    multi_az                              = false
    nchar_character_set_name              = null
    network_type                          = "IPV4"
    option_group_name                     = "default:mysql-8-4"
    parameter_group_name                  = "default.mysql8.4"
    password                              = "!7w6orN1JqS"
    performance_insights_enabled          = false
    performance_insights_kms_key_id       = null
    performance_insights_retention_period = 0
    port                                  = 3306
    publicly_accessible                   = false
    replica_mode                          = null
    replicate_source_db                   = null
    skip_final_snapshot                   = true
    storage_encrypted                     = true
    storage_throughput                    = 0
    storage_type                          = "gp2"
    tags                                  = {}
    tags_all                              = {}
    timezone                              = null
    username                              = "admin"
    vpc_security_group_ids                = [
        aws_security_group.sg_rds_health.id,
    ]
}

resource "aws_db_subnet_group" "health_db_subnet" {
    description             = "sg for health sys db"
    name                    = "rds-subnet-sql-health-sys"
    name_prefix             = null
    subnet_ids              = [
        aws_subnet.prv_1_health.id,
        aws_subnet.prv_2_health.id,
    ]
}
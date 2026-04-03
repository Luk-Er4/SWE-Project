# ECS Cluster
resource "aws_ecs_cluster" "main" {
   name = "ecr-cluster-${var.project_name}"

    configuration {
        execute_command_configuration {
        logging = "DEFAULT"
        }
    }
}

# ECS Service (in ECS Cluster)
resource "aws_ecs_service" "app" {
    name                         = "${var.task_definition_name}-${var.project_name}-service-fwgacusd"
    cluster                      = aws_ecs_cluster.main.id
    desired_count                = 1
    task_definition              = "${var.task_definition_name}-${var.project_name}:5"
    enable_ecs_managed_tags      = true
    availability_zone_rebalancing = "ENABLED"

    deployment_circuit_breaker {
        enable   = true
        rollback = true
    }

    load_balancer {
        target_group_arn = "arn:aws:elasticloadbalancing:${var.aws_region}:${data.aws_caller_identity.current.account_id}:targetgroup/tg-${var.project_name}/11933881c0746628"
        container_name   = "container-${var.project_name}"
        container_port   = 8000
    }

    network_configuration {
        subnets          = ["subnet-0469cd3e609806a31", "subnet-0513d4e6e574b9b70"]
        security_groups  = ["sg-0ef29a6809f2a0880"]
        assign_public_ip = true
    }
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
            "image" = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_name}/api@sha256:21317844acc7e7261fb616cb14cd1ef4e8fceec53ac37ef7fe049c062ffc31d9",
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
        "subnet-0469cd3e609806a31", # us-east-1b public
        "subnet-0513d4e6e574b9b70"  # us-east-1a public
    ]
}

# ALB Target groups
resource "aws_lb_target_group" "health_fargate_api" {
    name        = "tg-health-sys"
    port        = 8000
    protocol    = "HTTP"
    vpc_id      = var.vpc_id
    target_type = "ip"

    health_check {
        healthy_threshold   = 5
        interval            = 30
        matcher             = "200"
        path                = "/"
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
        forward {
            stickiness {
                duration = 3600 
                enabled  = false 
            }
            target_group {
                arn    = "arn:aws:elasticloadbalancing:us-east-1:${data.aws_caller_identity.current.account_id}:targetgroup/tg-health-sys/11933881c0746628" 
                weight = 1 
            }
        }
    }
}

# Security Groups (1. alb sg)
resource "aws_security_group" "sg_alb_health" {
    name        = "security-group-alb-health-sys"
    description = "sg for alb"
    vpc_id      = var.vpc_id

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
    vpc_id      = var.vpc_id

    ingress {
        cidr_blocks      = []
        from_port        = 3306
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "tcp"
        security_groups  = [
            "sg-0ef29a6809f2a0880",
        ]
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
    vpc_id      = var.vpc_id

    ingress {
        cidr_blocks      = []
        from_port        = 8000
        ipv6_cidr_blocks = []
        prefix_list_ids  = []
        protocol         = "tcp"
        security_groups  = [
            "sg-0927241d96061854c",
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
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
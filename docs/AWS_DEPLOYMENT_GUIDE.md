# AWS DEPLOYMENT GUIDE - NRRC Arabic PoV System
## Complete AWS Cloud Deployment Strategy

**⚠️ CONFIDENTIAL - Internal Use Only**
**Date**: 2024
**Version**: 2.0
**Status**: Production Ready

---

## 🎯 AWS DEPLOYMENT OVERVIEW

### **Deployment Architecture Options**

#### **Option 1: ECS Fargate (Recommended)**
```
Internet Gateway
    ↓
Application Load Balancer (ALB)
    ↓
ECS Cluster (Fargate)
    ├── API Service (FastAPI)
    ├── Search Service (FAISS)
    └── Auth Service (JWT)
    ↓
RDS PostgreSQL (Users & Sessions)
    ↓
S3 (Document Storage + Indices)
    ↓
ElastiCache Redis (Caching)
```

#### **Option 2: Lambda + API Gateway**
```
API Gateway
    ↓
Lambda Functions
    ├── Search Function (FAISS)
    ├── Auth Function (JWT)
    └── Processing Function (PDF)
    ↓
DynamoDB (Metadata)
    ↓
S3 (Documents + Indices)
```

#### **Option 3: EKS (Kubernetes)**
```
EKS Cluster
    ├── API Pods (FastAPI)
    ├── Search Pods (FAISS)
    └── Auth Pods (JWT)
    ↓
RDS PostgreSQL
    ↓
S3 (Storage)
    ↓
ElastiCache Redis
```

---

## 🚀 STEP-BY-STEP AWS DEPLOYMENT

### **Phase 1: AWS Infrastructure Setup**

#### **1.1 Create VPC and Networking**
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=nrrc-vpc}]'

# Create Internet Gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=nrrc-igw}]'

# Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx

# Create Public Subnets
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nrrc-public-1a}]'
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nrrc-public-1b}]'

# Create Private Subnets
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.10.0/24 --availability-zone us-east-1a --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nrrc-private-1a}]'
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.20.0/24 --availability-zone us-east-1b --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=nrrc-private-1b}]'
```

#### **1.2 Create Security Groups**
```bash
# Create ALB Security Group
aws ec2 create-security-group --group-name nrrc-alb-sg --description "Security group for ALB" --vpc-id vpc-xxx

# Allow HTTP/HTTPS traffic
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 443 --cidr 0.0.0.0/0

# Create ECS Security Group
aws ec2 create-security-group --group-name nrrc-ecs-sg --description "Security group for ECS tasks" --vpc-id vpc-xxx

# Allow traffic from ALB
aws ec2 authorize-security-group-ingress --group-id sg-yyy --protocol tcp --port 8000 --source-group sg-xxx

# Create RDS Security Group
aws ec2 create-security-group --group-name nrrc-rds-sg --description "Security group for RDS" --vpc-id vpc-xxx

# Allow PostgreSQL traffic from ECS
aws ec2 authorize-security-group-ingress --group-id sg-zzz --protocol tcp --port 5432 --source-group sg-yyy
```

#### **1.3 Create Route Tables**
```bash
# Create Public Route Table
aws ec2 create-route-table --vpc-id vpc-xxx --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=nrrc-public-rt}]'

# Add route to Internet Gateway
aws ec2 create-route --route-table-id rtb-xxx --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxx

# Associate subnets with route table
aws ec2 associate-route-table --subnet-id subnet-xxx --route-table-id rtb-xxx
aws ec2 associate-route-table --subnet-id subnet-yyy --route-table-id rtb-xxx

# Create Private Route Table
aws ec2 create-route-table --vpc-id vpc-xxx --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=nrrc-private-rt}]'

# Associate private subnets
aws ec2 associate-route-table --subnet-id subnet-zzz --route-table-id rtb-yyy
aws ec2 associate-route-table --subnet-id subnet-aaa --route-table-id rtb-yyy
```

### **Phase 2: Database Setup**

#### **2.1 Create RDS Subnet Group**
```bash
# Create DB subnet group
aws rds create-db-subnet-group \
    --db-subnet-group-name nrrc-db-subnet-group \
    --db-subnet-group-description "Subnet group for NRRC database" \
    --subnet-ids subnet-zzz subnet-aaa
```

#### **2.2 Create RDS Instance**
```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
    --db-instance-identifier nrrc-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 13.7 \
    --master-username admin \
    --master-user-password YourSecurePassword123! \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids sg-zzz \
    --db-subnet-group-name nrrc-db-subnet-group \
    --backup-retention-period 7 \
    --multi-az \
    --storage-encrypted \
    --tags Key=Name,Value=nrrc-database
```

#### **2.3 Create ElastiCache Redis**
```bash
# Create Redis subnet group
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name nrrc-redis-subnet-group \
    --cache-subnet-group-description "Subnet group for NRRC Redis" \
    --subnet-ids subnet-zzz subnet-aaa

# Create Redis cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id nrrc-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1 \
    --cache-subnet-group-name nrrc-redis-subnet-group \
    --security-group-ids sg-zzz \
    --tags Key=Name,Value=nrrc-redis
```

### **Phase 3: S3 Storage Setup**

#### **3.1 Create S3 Buckets**
```bash
# Create main data bucket
aws s3 mb s3://nrrc-arabic-pov-data-prod

# Create backup bucket
aws s3 mb s3://nrrc-arabic-pov-backup-prod

# Create logs bucket
aws s3 mb s3://nrrc-arabic-pov-logs-prod

# Enable versioning
aws s3api put-bucket-versioning --bucket nrrc-arabic-pov-data-prod --versioning-configuration Status=Enabled
aws s3api put-bucket-versioning --bucket nrrc-arabic-pov-backup-prod --versioning-configuration Status=Enabled
```

#### **3.2 Configure S3 Bucket Policies**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowECSReadWrite",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::nrrc-arabic-pov-data-prod/*"
    }
  ]
}
```

### **Phase 4: ECS Deployment**

#### **4.1 Create ECS Cluster**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name nrrc-cluster --tags key=Name,value=nrrc-cluster
```

#### **4.2 Create ECR Repository**
```bash
# Create ECR repository
aws ecr create-repository --repository-name nrrc-arabic-pov --tags key=Name,value=nrrc-arabic-pov

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t nrrc-arabic-pov .
docker tag nrrc-arabic-pov:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/nrrc-arabic-pov:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/nrrc-arabic-pov:latest
```

#### **4.3 Create Task Definition**
```json
{
  "family": "nrrc-arabic-pov",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "nrrc-api",
      "image": "ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/nrrc-arabic-pov:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://admin:YourSecurePassword123!@nrrc-db.xxx.us-east-1.rds.amazonaws.com:5432/nrrc"
        },
        {
          "name": "REDIS_URL",
          "value": "redis://nrrc-redis.xxx.cache.amazonaws.com:6379"
        },
        {
          "name": "S3_BUCKET",
          "value": "nrrc-arabic-pov-data-prod"
        },
        {
          "name": "SECRET_KEY",
          "value": "your-super-secret-jwt-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/nrrc-arabic-pov",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### **4.4 Create Application Load Balancer**
```bash
# Create ALB
aws elbv2 create-load-balancer \
    --name nrrc-alb \
    --subnets subnet-xxx subnet-yyy \
    --security-groups sg-xxx \
    --tags Key=Name,Value=nrrc-alb

# Create target group
aws elbv2 create-target-group \
    --name nrrc-targets \
    --protocol HTTP \
    --port 8000 \
    --vpc-id vpc-xxx \
    --target-type ip \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --health-check-timeout-seconds 5 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:loadbalancer/app/nrrc-alb/xxx \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/nrrc-targets/xxx
```

#### **4.5 Create ECS Service**
```bash
# Create ECS service
aws ecs create-service \
    --cluster nrrc-cluster \
    --service-name nrrc-service \
    --task-definition nrrc-arabic-pov:1 \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-yyy],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/nrrc-targets/xxx,containerName=nrrc-api,containerPort=8000" \
    --enable-execute-command
```

### **Phase 5: Monitoring and Logging**

#### **5.1 Create CloudWatch Log Group**
```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/nrrc-arabic-pov --tags Name=nrrc-logs
```

#### **5.2 Create CloudWatch Alarms**
```bash
# Create CPU utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name nrrc-cpu-high \
    --alarm-description "High CPU utilization" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:nrrc-alerts

# Create memory utilization alarm
aws cloudwatch put-metric-alarm \
    --alarm-name nrrc-memory-high \
    --alarm-description "High memory utilization" \
    --metric-name MemoryUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:nrrc-alerts
```

---

## 💰 AWS COST ESTIMATION

### **Monthly Cost Breakdown**

#### **ECS Fargate**
- **2 tasks × 1 vCPU × 2GB RAM**: ~$60/month
- **Application Load Balancer**: ~$20/month
- **Data Transfer**: ~$10/month

#### **RDS PostgreSQL**
- **db.t3.micro (Multi-AZ)**: ~$25/month
- **Storage (20GB)**: ~$5/month
- **Backups**: ~$3/month

#### **ElastiCache Redis**
- **cache.t3.micro**: ~$15/month

#### **S3 Storage**
- **100GB storage**: ~$3/month
- **Requests**: ~$2/month
- **Data transfer**: ~$5/month

#### **CloudWatch**
- **Logs**: ~$5/month
- **Metrics**: ~$3/month
- **Alarms**: ~$2/month

#### **Total Estimated Cost**: ~$159/month

### **Cost Optimization Strategies**
- **Reserved Instances**: 30% savings with 1-year commitment
- **Spot Instances**: 70% savings for non-critical workloads
- **S3 Intelligent Tiering**: Automatic cost optimization
- **CloudWatch Logs Retention**: Reduce retention period
- **Auto Scaling**: Scale down during low usage

---

## 🔒 AWS SECURITY BEST PRACTICES

### **Network Security**
- **VPC**: Isolated network environment
- **Security Groups**: Restrictive firewall rules
- **NACLs**: Additional network-level security
- **Private Subnets**: Database and cache isolation

### **Data Security**
- **Encryption at Rest**: RDS and S3 encryption
- **Encryption in Transit**: SSL/TLS for all connections
- **KMS**: Key management service for encryption keys
- **IAM**: Least privilege access control

### **Application Security**
- **WAF**: Web application firewall
- **Shield**: DDoS protection
- **GuardDuty**: Threat detection
- **Config**: Compliance monitoring

### **Monitoring and Auditing**
- **CloudTrail**: API call logging
- **CloudWatch**: System monitoring
- **Security Hub**: Security posture management
- **Inspector**: Vulnerability assessment

---

## 🚀 DEPLOYMENT AUTOMATION

### **Terraform Configuration**
```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "nrrc_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "nrrc-vpc"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "nrrc_cluster" {
  name = "nrrc-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# RDS Instance
resource "aws_db_instance" "nrrc_db" {
  identifier     = "nrrc-db"
  engine         = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  
  db_name  = "nrrc"
  username = "admin"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.nrrc_db_subnet_group.name
  
  backup_retention_period = 7
  multi_az               = true
  storage_encrypted      = true
  
  tags = {
    Name = "nrrc-database"
  }
}
```

### **GitHub Actions CI/CD**
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push image
      run: |
        docker build -t nrrc-arabic-pov .
        docker tag nrrc-arabic-pov:latest $ECR_REGISTRY/nrrc-arabic-pov:latest
        docker push $ECR_REGISTRY/nrrc-arabic-pov:latest
    
    - name: Update ECS service
      run: |
        aws ecs update-service --cluster nrrc-cluster --service nrrc-service --force-new-deployment
```

---

## 📊 MONITORING AND OBSERVABILITY

### **CloudWatch Dashboards**
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", "ServiceName", "nrrc-service"],
          ["AWS/ECS", "MemoryUtilization", "ServiceName", "nrrc-service"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "us-east-1",
        "title": "ECS Service Metrics"
      }
    }
  ]
}
```

### **Application Performance Monitoring**
- **X-Ray**: Distributed tracing
- **CloudWatch Insights**: Log analysis
- **Custom Metrics**: Business-specific metrics
- **Synthetic Monitoring**: Uptime monitoring

---

## 🔧 TROUBLESHOOTING AWS DEPLOYMENT

### **Common Issues**

#### **1. ECS Service Not Starting**
```bash
# Check service status
aws ecs describe-services --cluster nrrc-cluster --services nrrc-service

# Check task logs
aws logs get-log-events --log-group-name /ecs/nrrc-arabic-pov --log-stream-name ecs/nrrc-api/task-id
```

#### **2. Database Connection Issues**
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier nrrc-db

# Test connectivity
aws rds describe-db-instances --db-instance-identifier nrrc-db --query 'DBInstances[0].Endpoint.Address'
```

#### **3. Load Balancer Issues**
```bash
# Check target health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:us-east-1:ACCOUNT:targetgroup/nrrc-targets/xxx

# Check ALB logs
aws s3 ls s3://nrrc-arabic-pov-logs-prod/ --recursive
```

### **Performance Optimization**
- **Auto Scaling**: Scale based on CPU/memory
- **Caching**: Redis for frequent queries
- **CDN**: CloudFront for static assets
- **Database Optimization**: Read replicas, connection pooling

---

## 📞 AWS SUPPORT AND RESOURCES

### **AWS Support Plans**
- **Basic**: Free (community support)
- **Developer**: $29/month (email support)
- **Business**: $100/month (phone support)
- **Enterprise**: $15,000/month (dedicated support)

### **Useful AWS Resources**
- **AWS Documentation**: https://docs.aws.amazon.com/
- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/
- **AWS Pricing Calculator**: https://calculator.aws/
- **AWS Support Center**: https://console.aws.amazon.com/support/

---

**End of AWS Deployment Guide**

*This document contains confidential and proprietary information. Distribution is restricted to authorized personnel only.*

**Version**: 2.0  
**Last Updated**: 2024  
**Classification**: CONFIDENTIAL  
**Distribution**: INTERNAL USE ONLY

#!/bin/bash


#################
# Author: Sundar
# Date: 14th June 2026
#
# Version: v1
#
# This script will report the AWS resource usage. 
#################

# AWS S3
# AWS EC2
# AWS Lambda
# AWS IAM Users

set -x

# list s3 buckets
aws s3 ls

# list ec2 instances
aws ec2 describe-instances | jq '.Reservations[].Instances[].InstanceId'

# list aws lambda functions
aws lambda list-functions

# list IAM users
aws iam list-users


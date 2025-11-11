from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Duration,
)
from constructs import Construct

class FastapiLambdaCdkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Lambda from Docker image
        docker_lambda = _lambda.DockerImageFunction(
            self, "FastApiDockerLambda",
            code=_lambda.DockerImageCode.from_image_asset("../",
            file="Dockerfile.api",
            exclude=[
              "infra/cdk.out",  # CDK output
              "infra/.venv",  # if CDK has its own venv
              "venv",  # app venv
              "*.md",  # README files
              "*.bat",  # scripts like source.bat
              "requirements-dev.txt"  # dev-only dependencies
          ]), #custom Dockerfile name

            timeout = Duration.seconds(120),
            memory_size = 1024,
        )
        # Attach Bedrock permissions to the Lambda role
        docker_lambda.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )
        # API Gateway endpoint
        apigw.LambdaRestApi(
            self, "FastApiEndpoint",
            handler=docker_lambda,
            proxy=True
        )

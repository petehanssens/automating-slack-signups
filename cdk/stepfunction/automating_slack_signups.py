from aws_cdk import (
    aws_dynamodb as _dynamodb,
    aws_s3 as _s3,
    aws_lambda as _lambda,
    aws_apigateway as _apigateway,
    aws_iam as _iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
    core
)



class MyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # DynamoDB Table
        my_table= _dynamodb.Table(self,
            id='dynamoTable',
            table_name='dev-cdk-automating-slack-signups-table',
            partition_key=_dynamodb.Attribute(
                name='timestamp',
                type=_dynamodb.AttributeType.STRING
            ),
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST
        )    

        # S3 Bucket
        # my_bucket= _s3.Bucket(self,
        #     id='s3bucket',
        #     bucket_name='dev-cdk-automating-slack-signups-bucket')
        
        layer = _lambda.LayerVersion(self, "MyLayer",
            code=_lambda.Code.from_asset("layer-code/python.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_7],
            license="Apache-2.0",
            description="A layer to test the L2 construct"
        )

        # Lambda Functions
        # Slack Function
        slack_lambda= _lambda.Function(self,id='slack-lambdafunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            function_name='dev-cdk-automating-slack-signups-slack-func',
            handler='slack.main', 
            code= _lambda.Code.asset('lambdacode'),
            layers=[layer]
        )

        slack_lambda.add_to_role_policy(_iam.PolicyStatement(
            actions=[
                "secretsmanager:*",
            ],
            resources=['arn:aws:secretsmanager:ap-southeast-2:${ACCOUNT_ID}:secret:secrets_automating_slack_signups-Nz9WWM']
        ))

        # Mailchimp Function
        mailchimp_lambda= _lambda.Function(self,id='mailchimp-lambdafunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            function_name='dev-cdk-automating-slack-signups-mailchimp-func',
            handler='mailchimp.main', 
            code= _lambda.Code.asset('lambdacode'),
            layers=[layer]
        )

        mailchimp_lambda.add_to_role_policy(_iam.PolicyStatement(
            actions=[
                "secretsmanager:*",
            ],
            resources=['arn:aws:secretsmanager:ap-southeast-2:${ACCOUNT_ID}:secret:secrets_automating_slack_signups-Nz9WWM']
        ))

        # Dynamodb Functon
        dynamodb_lambda= _lambda.Function(self,id='dynamodb-lambdafunction',
            runtime=_lambda.Runtime.PYTHON_3_7,
            function_name='dev-cdk-automating-slack-signups-dynamodb-func',
            handler='dynamodb.main', 
            code= _lambda.Code.asset('lambdacode'),
            layers=[layer]
        )

        dynamodb_lambda.add_to_role_policy(_iam.PolicyStatement(
            actions=[
                "dynamodb:DescribeTable",
                "dynamodb:Query",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem"
            ],
            resources=[my_table.table_arn]
        ))

        slack_lambda.add_to_role_policy(_iam.PolicyStatement(
            actions=[
                "secretsmanager:*",
            ],
            resources=['arn:aws:secretsmanager:ap-southeast-2:${ACCOUNT_ID}:secret:secrets_automating_slack_signups-Nz9WWM']
        ))
                    
        api_with_method = _apigateway.LambdaRestApi(self,
            id='restapi',
            rest_api_name='dev-cdk-automating-slack-signups-api',
            handler=slack_lambda)
        slack_api = api_with_method.root.add_resource('automating-slack-signups')
        slack_api.add_method('POST')



#!/usr/bin/env python3

from aws_cdk import core
from stepfunction.automating_slack_signups import MyStack

app = core.App()
MyStack(app, "aws-stepfunctions-integ")
app.synth()

import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";

export class TwdhCkanDockerCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const CODE_COMMIT = new cdk.aws_codecommit.Repository(
      this,
      "twdh_ckan_docker",
      {
        repositoryName: "twdh_ckan_docker",
        description: "repository for the twdh_ckan_docker image",
      }
    );
  }
}

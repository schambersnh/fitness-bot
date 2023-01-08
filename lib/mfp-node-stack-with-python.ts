import { Stack, StackProps } from 'aws-cdk-lib';

import * as cdk from 'aws-cdk-lib';
import * as sm from "aws-cdk-lib/aws-secretsmanager";
import * as kms from 'aws-cdk-lib/aws-kms';

import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { Runtime } from 'aws-cdk-lib/aws-lambda';


export class MfpNodeStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const kmsKey = kms.Key.fromKeyArn(this, 'MyImportedKey', 'arn:aws:kms:us-east-1:293572753380:key/1565af15-9587-483a-940b-144da8f2332b');
    const fitnessBotSecret = sm.Secret.fromSecretAttributes(this, "FitnessBotSecret", {
        secretCompleteArn:
          "arn:aws:secretsmanager:us-east-1:293572753380:secret:fitness-bot-secret-UPjYGM",
        encryptionKey: kmsKey
    });

    //todo: create runtimecode to fetch these secrets rather than storing them as environment variables
    const twilioAuthToken = fitnessBotSecret.secretValueFromJson('TWILIO_AUTH_TOKEN').unsafeUnwrap().toString()
    const spreadsheetApiKey = fitnessBotSecret.secretValueFromJson('SPREADSHEET_API_KEY').unsafeUnwrap().toString()
    const myFitnessPalPassword = fitnessBotSecret.secretValueFromJson('MFP_PASSWORD').unsafeUnwrap().toString()


    const environmentVariables = {
      'TWILIO_AUTH_TOKEN':  twilioAuthToken,
      'SPREADSHEET_API_KEY': spreadsheetApiKey,
      'MFP_PASSWORD': myFitnessPalPassword
    }


    new PythonFunction(this, 'FitnessBotLambda', {
      runtime: Runtime.PYTHON_3_9,
      entry: './lambda',
      index: 'fitness_bot.py'
    });

  }
}

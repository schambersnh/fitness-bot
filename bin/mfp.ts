#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { MfpNodeStack } from '../lib/mfp-node-stack';

const app = new cdk.App();
new MfpNodeStack(app, 'MfpNodeStack');

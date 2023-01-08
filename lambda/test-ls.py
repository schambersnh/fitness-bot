import os
#from mfp_client import MFPClient


def lambda_handler(event, context):
    print('/var/task LISTING')
    print(os.listdir('/var/task/'))

    print('/var/task/cryptography LISTING')
    print(os.listdir('/var/task/cryptography'))

    print('/var/task/cryptography/hazmat LISTING')
    print(os.listdir('/var/task/cryptography/hazmat'))

    print('/var/task/cryptography/hazmat/bindings/ LISTING')
    print(os.listdir('/var/task/cryptography/hazmat/bindings/'))



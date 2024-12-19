# python-bedrock-layer
AWS Lambda layer that simplifies the usage of Bedrock functionalities.
Includes all libs necessary to run Bedrock functions.

# Instructions
1. Create a .zip with the python folder inside it and add it to your AWS Lambda as a layer for usage.
2. Add Bedrock permissions to your Lambda function role.
3. Import 'bedrock-layer' to the function.

# Usable Methods
1. converse(prompt, model_id=None, system_prompt=None, file=None, temperature=None, topP=None)

   


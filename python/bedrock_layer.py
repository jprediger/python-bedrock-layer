import boto3
import urllib3
import magic
import re

# Inicia SDK 
bedrock = boto3.client("bedrock", "us-east-1")
bedrock_runtime = boto3.client("bedrock-runtime", "us-east-1")

def doGet(url):
    timeout = urllib3.util.Timeout(connect=10.0, read=17.0)
    http = urllib3.PoolManager(timeout=timeout,cert_reqs = 'CERT_NONE')#
    http.verify = True

    print("sending GET request at",url)
    try:
        r = http.request('GET',url,
            timeout=20)
        
        print(r.status)
        #print(r.data)

        return r.status,r.data
    except Exception as e:
        print(e)
        return -1,''
    
def is_file_bytes(value):
    return isinstance(value, bytes)
    
def is_url(value):
    url_pattern = re.compile(r'^(http|https)://[^\s]+$')
    return isinstance(value, str) and url_pattern.match(value) is not None

def converse(prompt, model_id=None, system_prompt=None, file=None, temperature=None, topP=None):
    content = []
    
    if not isinstance(prompt, str):
        {"success": False, "error": "Invalid prompt"}
    
    # Set model_id
    if (model_id is None):
        model_id = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
        
    # Set temperature and topP with validation
    if (temperature is not None and not (0 <= temperature <= 1)):
        return {"success": False, "error": "Temperature must be between 0 and 1"}
    else:
        temperature = 0.7

    if (topP is not None and not (0 <= topP <= 1)):
        return {"success": False, "error": "topP must be between 0 and 1"}
    else:
        topP = 0.9
        
    inference_config = {
        'temperature': temperature, # The likelihood of the model selecting higher-probability options while generating a response.
        'topP': topP # The percentage of most-likely candidates that the model considers for the next token.
    }
    
    # Check if file is present and is valid
    if (file is not None):
        
        if (is_url(file)):
            status, fileBytes = doGet(file)
            if (status != 200):
                return {"success": False, "error": "Failed to process file"}
            file = fileBytes
        elif (not is_file_bytes(file)):
            return {"success": False, "error": "Invalid file format, acepted formats: Bytes, URL"}
        
        fileMainType, fileSubType = magic.from_buffer(fileBytes, mime=True).split('/')
        valid_file_types = {
            'application': ['pdf', 'doc', 'docx'],
            'image': ['png', 'jpeg', 'webp']
        }

        if fileMainType not in valid_file_types or fileSubType not in valid_file_types[fileMainType]:
            return {"success": False, "error": "Invalid file format, accepted formats: PNG, JPEG, WEBP, PDF, DOC, DOCX"}
        
        if fileMainType == 'application':
            fileRequest = {
                'document': {
                    'format': fileSubType,
                    'name': 'string',
                    'source': {
                        'bytes': fileBytes
                    }
                }
            }
        else: 
            fileRequest = {
                'image': {
                    'format': fileSubType,
                    'source': {
                        'bytes': fileBytes
                    }
                }
            }
        
        if fileRequest:
            content.append(fileRequest)



    # add prompt to content
    content.append({"text": prompt})
    
    messages = [
        {
            'role': 'user',
            'content': content
        }
    ]
    
    try:

        request_args = {
            "modelId": model_id,
            "messages": messages,
            "inferenceConfig": inference_config
        }
    
        if system_prompt:
            request_args["system"] = [{'text': system_prompt}]
    
        # Faz a chamada com os argumentos preparados
        response = bedrock_runtime.converse(**request_args)
        return {"success": True, "data": response.get('output', {}).get('message', {}).get('content', [{}])[0]}
    except Exception as e:
        print(f"Error during Bedrock request: {e}")
        return {"success": False, "error": "Internal server error"}

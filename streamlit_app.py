# inspiration: 
# https://github.com/aarushdixit889/photo-semantics-analyzer/blob/main/app.py
# https://medium.com/@codingmatheus/sending-images-to-claude-3-using-amazon-bedrock-b588f104424f
# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
# https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/bedrock-runtime/models/anthropic_claude/converse.py#L4

import streamlit as st
import json
import base64
import boto3

bedrock_runtime_client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_REGION"]
)
model_id = "anthropic.claude-3-5-haiku-20241022-v1:0"


# Create a Bedrock Runtime client in the AWS Region you want to use.
#client = boto3.client("bedrock-runtime", region_name="us-east-1")

# functions

def make_payload(encoded_image):
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": encoded_image
                        }
                    },
                    {
                        "type": "text",
                        "text": "Explain this AWS architecture diagram."
                    }
                ]
            }
        ],
        #"anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500        
    }
    return payload

def get_LLM_analysis(image):
    print("converting image to b64")
    encoded_image = base64.b64encode(image.read()).decode()
    encoded_image
    st.write("converted")
    
    payload = make_payload(encoded_image)
    payload
    st.write("message ready")

    response = bedrock_runtime_client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        body=json.dumps(payload)
        )

    answer = response["output"]["message"]["content"][0]["text"]
            
    return answer


# main page
st.title("🎈 URI test app")
st.write("upload your urine test strip for analysis")

image=st.file_uploader("Upload your photo")
if image is not None:
    st.sidebar.image(image)
    answer=get_LLM_analysis(image)
    st.write(answer)

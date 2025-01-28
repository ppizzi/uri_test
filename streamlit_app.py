# inspiration: 
# https://github.com/aarushdixit889/photo-semantics-analyzer/blob/main/app.py
# https://medium.com/@codingmatheus/sending-images-to-claude-3-using-amazon-bedrock-b588f104424f
# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
# https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/bedrock-runtime/models/anthropic_claude/converse.py#L4

import streamlit as st
import json
import base64
import boto3
from botocore.exceptions import ClientError

# main page
st.title("🎈 URI test app")
st.write("upload your urine test strip for analysis")


client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_REGION"]
)

# Select model for inference
# naming conventions: https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
# model_id = "anthropic.claude-3-5-haiku-20241022-v1:0" #must use x-region inference??!!
model_id = "amazon.nova-lite-v1:0"
st.write(model_id)

# Create a Bedrock Runtime client in the AWS Region you want to use.
# client = boto3.client("bedrock-runtime", region_name="us-east-1")


# ---test model connection and response ---
# Start a conversation with the user message.
user_message = "what parameters are typically included in a urine strip test?"
conversation = [
    {
        "role": "user",
        "content": [{"text": user_message}],
    }
]

try:
    # Send the message to the model, using a basic inference configuration.
    response = client.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 512, "temperature": 0.5, "topP": 0.9},
    )

    # Extract and print the response text.
    response_text = response["output"]["message"]["content"][0]["text"]
    st.write(response_text)

except (ClientError, Exception) as e:
    st.write(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)

#--- end of test section ---


# functions
def make_payload(image, encoded_image):
    payload = {
        "messages":[
            { 
                "role": "user",
                "content":[
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
                        "text": "Describe an image of a dipstick test and provide key paramenters. Is there any sign of an infection?."
                    }
                ]               
            }                
        ],
        "system": [{"text" : "You are an expert medical doctor"}]
    }
    
    return payload

def get_LLM_analysis(image):
    print("converting image to b64")
    encoded_image = base64.b64encode(image.read()).decode()
    # encoded_image
    st.write("converted")
    
    payload = make_payload(image, encoded_image)
    payload
    st.write("message ready")

   # response = client.invoke_model(
   #     modelId=model_id,
   #     contentType="application/json",
   #     body=json.dumps(payload)
   #     )

    try:
        # Send the message to the model, using a basic inference configuration.
        response = client.converse(
            modelId=model_id,
            messages=payload,
            inferenceConfig={"temperature": 0.5, "topP": 0.9},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]
        st.write(response_text)

    except (ClientError, Exception) as e:
        st.write(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)


    

    answer = response["output"]["message"]["content"][0]["text"]
    
    return answer




image=st.file_uploader("Upload your photo")
if image is not None:
    st.sidebar.image(image)
    answer=get_LLM_analysis(image)
    st.write(answer)

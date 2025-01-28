# inspiration: 
# https://github.com/aarushdixit889/photo-semantics-analyzer/blob/main/app.py
# https://medium.com/@codingmatheus/sending-images-to-claude-3-using-amazon-bedrock-b588f104424f

import streamlit as st
import json
import base64
#import boto3

# model_id = "anthropic.claude-3-haiku-20240307-v1:0"


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
        "max_tokens": 1000,
        "anthropic_version": "bedrock-2023-05-31"
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

    # response = bedrock_runtime_client.invoke_model(
    # modelId=model_id,
    # contentType="application/json",
    # body=json.dumps(payload)
    #)
    
    return


# main page
st.title("🎈 URI test app")
st.write("upload your urine test strip for analysis")

image=st.file_uploader("Upload your photo")
if file is not None:
    st.sidebar.image(image)
    answer=get_LLM_analysis(image)
    # st.write(answer)

# inspiration: 
# https://github.com/aarushdixit889/photo-semantics-analyzer/blob/main/app.py
# https://medium.com/@codingmatheus/sending-images-to-claude-3-using-amazon-bedrock-b588f104424f
# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
# https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/bedrock-runtime/models/anthropic_claude/converse.py#L4
# https://docs.aws.amazon.com/nova/latest/userguide/modalities-image-examples.html

import streamlit as st
import json
import base64
import boto3
from botocore.exceptions import ClientError


# -- functions --

def print_legend(language):
    # Start a conversation with the user message.
    user_message = "List in bullet points the parameters that are typically included in a urine strip test and how to interpret them. Use markdown as formatting language in your response. Please respond in the following language: " + language
    # st.write(user_message)
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
            inferenceConfig={"temperature": 0.5, "topP": 0.9},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]
        st.write(response_text)

    except (ClientError, Exception) as e:
        st.write(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    return


def make_payload(encoded_image, language):
    # Define your system prompt(s).
    system_list = [
        {
            "text": "You are an expert medical doctor. When the user provides you with an image of their urine test strip, provide a short medical analysis and lookout for possible infection indicators. Provide your answer in a concise format. Provide your answer in markdown format. Do not analyze images that are not containing a urine test strip. Always end the response with a disclaimer that this is not a medical advice."
        }
    ]
    # Define a "user" message including both the image and a text prompt.
    message_list = [
        {
            "role": "user",
            "content": [
                {
                    "image": {
                        "format": "jpg",
                        "source": {"bytes": encoded_image},
                    }
                },
                {
                    "text": "Analyze the image provided by the user. Provide a short summary of your analysis first. Then provide a table with the following columns: parameter name (declare the order with respect to the photo of the test stick); detected color; result of the analysis; details (explain your analysis); indicator (green/yellow/red use markdown logos). For parameters that are out of normal range, provide a short analysis after the table. Please respond in the following language: " + language
                }
            ],
        }
    ]
    # Configure the inference parameters.
    inf_params = {"temperature": 0.5, "topP": 0.9}

    payload = {
        "messages": message_list,
        "system": system_list,
        "inferenceConfig": inf_params,
    }
  
    return payload

def get_LLM_analysis(image, language):
    print("converting image to b64")
    encoded_image = base64.b64encode(image.read()).decode("utf-8")
    # encoded_image
    # st.write("converted")
    
    payload = make_payload(encoded_image, language)
    # payload
    # st.write("message ready")

    try:
        # Send the message to the model, using a basic inference configuration.
        # response = client.converse(
        response = client.invoke_model(    
            modelId=model_id,
            #messages=payload,
            body=json.dumps(payload)
        )            

        # Extract and print the response text.
        model_response = json.loads(response["body"].read())
        # st.write("Model response:")
        # st.write(json.dumps(model_response, indent=2))
        content_text = model_response["output"]["message"]["content"][0]["text"]
        # st.write(content_text)   

    except (ClientError, Exception) as e:
        st.write(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    answer = content_text
    
    return answer

#--- end of function definition ---

#--- main page ---
st.title(":pill: Urine Test Analysis")
st.write("Upload a photo of your urine test strip for analysis")

# Select model for inference
# naming conventions: https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
# model_id = "anthropic.claude-3-5-haiku-20241022-v1:0" #must use x-region inference??!!
model_id = "amazon.nova-lite-v1:0"
st.write("\(note: this app uses the following LLM model: ", model_id, "\)" )
# st.write(model_id)

# Create a Bedrock Runtime client in the AWS Region you want to use.
# client = boto3.client("bedrock-runtime", region_name="us-east-1")
client = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets["AWS_REGION"]
)

output_language = st.radio("Select your language:", ["Spanish","Italian","English"]) 
st.write("You selected: ", output_language)


image=st.file_uploader("Upload your photo")
if image is not None:
    st.sidebar.image(image)
    answer=get_LLM_analysis(image, output_language)
    st.write(answer)


#-- print legenda of typical dipstick test
print_legend(output_language)



# -- end main--



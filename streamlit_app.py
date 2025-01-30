    # inspiration: 
# https://github.com/aarushdixit889/photo-semantics-analyzer/blob/main/app.py
# https://medium.com/@codingmatheus/sending-images-to-claude-3-using-amazon-bedrock-b588f104424f
# https://docs.streamlit.io/develop/tutorials/chat-and-llm-apps/build-conversational-apps
# https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code/bedrock-runtime/models/anthropic_claude/converse.py#L4
# https://docs.aws.amazon.com/nova/latest/userguide/modalities-image-examples.html
# https://discuss.streamlit.io/t/unique-key-for-every-items-in-radio-button/20654/4
# https://stackoverflow.com/questions/3715493/encoding-an-image-file-with-base64
# https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_ImageSource.html
# https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Message.html
# https://docs.anthropic.com/en/docs/build-with-claude/vision


import streamlit as st
import json
from PIL import Image
import PIL
import os
import base64
import boto3
from botocore.exceptions import ClientError


# -- functions --

def encode_image(image):
    #st.write("converting image to b64")
    try:
        encoded_image = base64.b64encode(image.read()).decode("utf-8") #< works with uploaded file from st.upload_file, but not with an image from PIL or from os.open
    except:
        encoded_image = base64.b64encode(image).decode("utf-8")
    #encoded_image
    #st.write("converted")
    
    return encoded_image

def print_legend(language):
    # Start a conversation with the user message.
    user_message = "List in bullet points the parameters that are typically included in a urine strip test and how to interpret them. Use markdown as formatting language in your response. Please respond in the following language: " + language + ". Finish the response with a line that states the LLM model provider."
    st.write(user_message)
    conversation = [
        {
        "role": "user",
        "content": [{"text": user_message}],
        }
    ]

    try:
        # Send the message to the model, using a basic inference configuration.
        response = client.converse(
            modelId=model_id2,
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
            "text": "You are an expert medical doctor. When the user provides you with an image of their urine test strip, analyze carefully the color of the various indicators on the test. Then provide a short medical analysis and lookout for possible infection indicators. Provide your answer in a concise format. Provide your answer in markdown format. Do not analyze images that are not containing a urine test strip. Always end the response with a disclaimer that this is not a medical advice. Finish the response with a line that states the LLM model provider. Please respond in the following language: " + language  
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
                    "text": "Analyze the image provided by the user, pay close attention to the colors of the indicators on the test strip and identify them precisely. Provide a short summary of your analysis first. Then provide a table where the rows are the test parameters in the same order as the picture provided, and the columns are the following: parameter name; detected color; result of the analysis; details (explain your analysis); indicator (green/yellow/red). For parameters that are out of normal range, provide a short analysis after the table."
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


def get_LLM_analysis(imageb64, language):
    
    payload = make_payload(imageb64, language)
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
model_id2 = "us.anthropic.claude-3-5-sonnet-20240620-v1:0" #must use x-region inference??!! --> add the us or eu prefix to the model?
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

st.sidebar.image("uri_test_reference.jpg")

up_image=st.file_uploader("Upload your photo", type=["jpg","png"])
if up_image is not None:
    img_holder = st.sidebar.image(up_image)
    st.write("Make sure your photo is aligned in the same way as the reference of the test-kit:")
    mapping = {"0":"OK", "90": "90º :arrows_counterclockwise:", "270": "90º :arrows_clockwise:", "180":"180º"}
    rotate = st.radio("Rotate photo: ", ("0","90","270","180"), format_func = lambda x: mapping[x])
    save = st.button("Save")
    if save:
        image = Image.open(up_image).rotate(int(rotate))
        img_holder.image(image)
        image.save("img.jpg")
       
launch_llm = st.button("Analyze")
if launch_llm: 
     with open("img.jpg", "rb") as f:
        image = f.read()
        st.sidebar.image(image)
        encoded_image = encode_image(image)
        st.write(encoded_image)
        answer=get_LLM_analysis(encoded_image, output_language)
        st.write(answer)


#-- print legenda of typical dipstick test
print_legend(output_language)


# -- end main--



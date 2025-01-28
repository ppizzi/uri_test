# inspiration: 
# https://github.com/aarushdixit889/photo-semantics-analyzer/blob/main/app.py
# https://medium.com/@codingmatheus/sending-images-to-claude-3-using-amazon-bedrock-b588f104424f

import streamlit as st
import json
import base64
#from PIL import Image # for image processing
#from transformers import BlipProcessor, BlipForConditionalGeneration

# model_id = "anthropic.claude-3-haiku-20240307-v1:0"


# functions
def get_LLM_analysis(image):
    print("converting image to b64")
    encoded_image = base64.b64encode(image.read()).decode()
    encoded_image
    print("converted")
    return

st.title("🎈 URI test app")
st.write(
    "upload your urine test strip for analysis"
)



file=st.file_uploader("Upload your photo")
if file is not None:
    st.sidebar.image(file)
    answer=get_LLM_analysis(file)
    # st.write(answer)

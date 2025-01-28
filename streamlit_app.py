import streamlit as st

st.title("🎈 URI test app")
st.write(
    "upload your urine test strip for analysis"
)



file=st.file_uploader("Upload your photo")
if file is not None:
    st.sidebar.image(file)
    # answer=get_semantics(file)
    # st.write(answer)

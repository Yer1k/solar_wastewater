import streamlit as st
import os
import pandas as pd

# Set page configuration
st.set_page_config(
    layout="wide", page_title="WWTP and Solar Panel Tagging Tool", page_icon="🏭"
)
# st.title("🌟Welcome to the WWTP and Solar Panel Tagging Tool🌟")
new_title = '<p style="font-size: 42px;">🌟 Welcome to the WWTP and Solar Panel Tagging Tool 🌟</p>'
st.markdown(new_title, unsafe_allow_html=True)

# User input for spreadsheet file
excel_file = st.file_uploader("Upload the comprehensive excel file", type=["xlsx"])

# User input for state name
state_name = st.text_input("👉 Enter the state name you want to tag:", value="").strip()
st.caption(
    "Example: California, Texas, New York, etc. Your image folder should have the same name."
)

# Add a confirmation button to proceed
if "is_tagging_started" not in st.session_state:
    st.session_state.is_tagging_started = False
if st.button("🚀 Start Tagging") and state_name and excel_file:
    st.session_state.is_tagging_started = True


def display_current_image(df_yes):
    """
    Display the current image and handle user responses for tagging.

    Inputs:
    - df_yes: Dataframe containing only images that have been tagged as "Yes"

    Outputs:
    - None
    """
    col1, col2 = st.columns([3, 2])  # Adjust column width ratios as needed

    if 0 <= st.session_state.current_image_index < len(df_yes):
        current_image = df_yes.iloc[st.session_state.current_image_index]
        current_image_path = os.path.join(IMAGE_FOLDER, current_image["filename"])

        if not os.path.exists(current_image_path):
            col1.error(f"Image {current_image_path} not found!")
            df.loc[df["filename"] == current_image["filename"], "Comments"] = (
                "IMAGE NOT FOUND"
            )
        else:
            # Use HTML to display image with enlargement feature
            with col1:
                st.write("<style> .image-container { margin-bottom: 20px; } img { max-width: 97%; height: auto; } </style>", unsafe_allow_html=True)
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(current_image_path, caption=current_image["filename"], use_column_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # display curent status of the image
            wwtp_status = (
                "Not Tagged"
                if pd.isnull(current_image["WWTP?"])
                else "Tagged as " + current_image["WWTP?"]
            )
            solar_status = (
                "Not Tagged"
                if pd.isnull(current_image["Solar?"])
                else "Tagged as " + current_image["Solar?"]
            )
            
            # Add margin to the top of col2
            col2.markdown('<style> .col2-container { margin-top: 200px; } </style>', unsafe_allow_html=True)
            col2.markdown('<div class="col2-container">', unsafe_allow_html=True)
            
            col2.write(
                f"📝 Current Status: WWTP - {wwtp_status}, Solar - {solar_status}"
            )
            col2.write("")

            # display curent status of the image
            wwtp_status = (
                "Not Tagged"
                if pd.isnull(current_image["WWTP?"])
                else "Tagged as " + current_image["WWTP?"]
            )
            solar_status = (
                "Not Tagged"
                if pd.isnull(current_image["Solar?"])
                else "Tagged as " + current_image["Solar?"]
            )
            col2.write(
                f"📝 Current Status: WWTP - {wwtp_status}, Solar - {solar_status}"
            )
            col2.write("")

            col2.write("🔍 Do you see a WWTP in this image?")
            if col2.button("WWTP Yes", key=f"wwtp_yes_{current_image['filename']}"):
                update_response(df_yes, current_image, "WWTP", "Yes")
                col2.success(
                    f'"Yes" response for "WWTP" saved for {current_image["filename"]}'
                )
            if col2.button("WWTP No", key=f"wwtp_no_{current_image['filename']}"):
                update_response(df_yes, current_image, "WWTP", "No")
                col2.success(
                    f'"No" response for "WWTP" saved for {current_image["filename"]}'
                )

            col2.write("☀️ Do you see solar panels in this image?")
            if col2.button("Solar Yes", key=f"solar_yes_{current_image['filename']}"):
                update_response(df_yes, current_image, "Solar", "Yes")
                col2.success(
                    f'"Yes" response for "Solar" saved for {current_image["filename"]}'
                )
            if col2.button("Solar No", key=f"solar_no_{current_image['filename']}"):
                update_response(df_yes, current_image, "Solar", "No")
                col2.success(
                    f'"No" response for "Solar" saved for {current_image["filename"]}'
                )

            col2.markdown('</div>', unsafe_allow_html=True)

            # Navigation buttons
            col2.write("")
            col2.write("Image Navigation")
            nav_col1, nav_col2, nav_col3 = col2.columns([1, 1, 1])
            if nav_col1.button("Previous", key="prev"):
                if st.session_state.current_image_index > 0:
                    st.session_state.current_image_index -= 1
                    st.session_state.last_image_reached = False
                st.rerun()
            if nav_col2.button("Next", key="next"):
                if st.session_state.current_image_index < len(df_yes) - 1:
                    st.session_state.current_image_index += 1
                else:
                    st.session_state.last_image_reached = True
                st.rerun()
            if nav_col3.button("Reset", key="reset"):
                st.session_state.current_image_index = 0
                st.session_state.selected_filename = None
                st.session_state.last_image_reached = False
                st.session_state.is_tagging_started = False

                # Optionally, clear the state name and spreadsheet file input
                if "state_name" in st.session_state:
                    del st.session_state["state_name"]
                if "excel_file" in st.session_state:
                    del st.session_state["excel_file"]

                # Rerun the app to refresh and show the initial input page
                st.rerun()

            if st.session_state.last_image_reached:
                col2.info("You've reached the last image in the folder.")


def update_response(df_yes, current_image, tag_type, response):
    """
    Update the response in the dataframe.

    Inputs:
    - current_image: Dictionary containing information about the current image
    - tag_type: String indicating the type of tag (WWTP or Solar)
    - response: String indicating the response (Yes or No)

    Outputs:
    - SPREADSHEET_FILE: Updated CSV file with the response
    """
    # Update the response in the dataframe based on the tag type and filename
    column_name = "WWTP?" if tag_type == "WWTP" else "Solar?"
    df_yes.loc[df_yes["filename"] == current_image["filename"], column_name] = response
    df_yes.to_csv(CURRENT_STATE_CSV, index=False)


if st.session_state.is_tagging_started:
    # Dynamically set paths based on user input
    IMAGE_FOLDER = os.path.join(os.getcwd(), state_name)
    CURRENT_STATE_CSV = os.path.join(
        os.getcwd(), "inference_tagging_for_" + state_name + ".csv"
    )

    # Check if the paths exist and proceed with the rest of the app
    if os.path.isdir(IMAGE_FOLDER):
        if not os.path.exists(CURRENT_STATE_CSV):
            # Create a new CSV file with the required columns
            df = pd.read_excel(excel_file)
            df_state = df.loc[df["State"] == state_name.upper()].reset_index(drop=True)
            df_yes = df_state[df_state["label"] == "Yes"].reset_index(drop=True)
            df_yes.to_csv(CURRENT_STATE_CSV, index=False)
            st.info(
                f"It's your first time to tag images for state: {state_name}."
                f"\n Tagging results will be saved in {CURRENT_STATE_CSV.split('/')[-1]}."
            )
            st.write(f"\n Total images to tag: {len(df_yes)}")

        else:
            df_yes = pd.read_csv(CURRENT_STATE_CSV)
            st.info(
                f"You tagged this state before: {state_name}. Loading previous results ..."
            )
            st.write(
                f'Total images to tag: {len(df_yes)}, tagged images: {len(df_yes[df_yes["WWTP?"].notnull() & df_yes["Solar?"].notnull()])}'
            )

        if "current_image_index" not in st.session_state:
            st.session_state.current_image_index = 0
        if "selected_filename" not in st.session_state:
            st.session_state.selected_filename = None
        if "last_image_reached" not in st.session_state:
            st.session_state.last_image_reached = False

        filenames = df_yes["filename"].tolist()
        filename_selected = st.selectbox(
            "📸 Select an image to start with:",
            filenames,
            index=st.session_state.current_image_index,
        )
        st.session_state.selected_filename = filename_selected

        if st.button("✅ Confirm Selection"):
            st.session_state.current_image_index = filenames.index(
                st.session_state.selected_filename
            )
            st.session_state.last_image_reached = False
            st.rerun()

        display_current_image(df_yes)
    else:
        st.error(
            "😢 Oh no! We couldn't find data for the specified state. Double-check the name and try again?"
        )

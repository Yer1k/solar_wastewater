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

# User input for state name
state_name = st.text_input("👉 Enter the state name you want to tag:", value="").strip()


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
            df.loc[df["filename"] == current_image["filename"], "manual tag"] = (
                "IMAGE NOT FOUND"
            )
        else:
            col1.image(current_image_path, caption=current_image["filename"], width=500)

            col2.write("🔍 Do you see a WWTP in this image?")
            if col2.button("WWTP Yes", key=f"wwtp_yes_{current_image['filename']}"):
                update_response(current_image, "WWTP", "Yes")
                col2.success(
                    f'"Yes" response for "WWTP" saved for {current_image["filename"]}'
                )
            if col2.button("WWTP No", key=f"wwtp_no_{current_image['filename']}"):
                update_response(current_image, "WWTP", "No")
                col2.success(
                    f'"No" response for "WWTP" saved for {current_image["filename"]}'
                )

            col2.write("☀️ Do you see solar panels in this image?")
            if col2.button("Solar Yes", key=f"solar_yes_{current_image['filename']}"):
                update_response(current_image, "Solar", "Yes")
                col2.success(
                    f'"Yes" response for "Solar" saved for {current_image["filename"]}'
                )
            if col2.button("Solar No", key=f"solar_no_{current_image['filename']}"):
                update_response(current_image, "Solar", "No")
                col2.success(
                    f'"No" response for "Solar" saved for {current_image["filename"]}'
                )

            # Navigation buttons
            col2.markdown("---")
            col2.write("Image Navigation")
            nav_col1, nav_col2, nav_col3 = col2.columns([1, 1, 1])
            if nav_col1.button("Previous", key="prev"):
                if st.session_state.current_image_index > 0:
                    st.session_state.current_image_index -= 1
                    st.session_state.last_image_reached = False
                st.experimental_rerun()
            if nav_col2.button("Next", key="next"):
                if st.session_state.current_image_index < len(df_yes) - 1:
                    st.session_state.current_image_index += 1
                else:
                    st.session_state.last_image_reached = True
                st.experimental_rerun()
            if nav_col3.button("Reset", key="reset"):
                st.session_state.current_image_index = 0
                st.session_state.selected_filename = None
                st.session_state.last_image_reached = False
                st.experimental_rerun()

            if st.session_state.last_image_reached:
                col2.info("You've reached the last image in the folder.")


def update_response(current_image, tag_type, response):
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
    column_name = "wwtp_tag" if tag_type == "WWTP" else "solar_tag"
    df.loc[df["filename"] == current_image["filename"], column_name] = response
    df.to_csv(SPREADSHEET_FILE, index=False)


if state_name:
    # Dynamically set paths based on user input
    IMAGE_FOLDER = os.path.join("data/", state_name)
    SPREADSHEET_FILE = f"data/predictions_best_{state_name}.csv"

    # Check if the paths exist and proceed with the rest of the app
    if os.path.isdir(IMAGE_FOLDER) and os.path.isfile(SPREADSHEET_FILE):
        df = pd.read_csv(SPREADSHEET_FILE)
        df_yes = df[df["label"] == "Yes"].reset_index(drop=True)

        st.write(f"You are tagging images for state: {state_name}")
        st.write(f"Total images to tag: {len(df_yes)}")

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
            st.experimental_rerun()

        display_current_image(df_yes)
    else:
        st.error(
            "😢 Oh no! We couldn't find data for the specified state. Double-check the name and try again?"
        )

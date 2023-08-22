""" 

This script has the function of setting up a Streamlit 
website servingas a user interface for the prediction of the
open, closed, or blinking status. This website is deployed 
using a Docker environment.

On this site, different tabs are available. The user can 
thus:
- either upload their photo,
- either take a picture with your camera,
- or make his prediction live by filming himself using his 
camera.

If he chooses the direct option, an alarm sounds when he 
keeps his eyes closed too long.

"""


###---------------------------------------------------------
### Import useful libraries
###---------------------------------------------------------

import streamlit as st
import os
import requests
from io import BytesIO
from streamlit_option_menu import option_menu
import numpy as np
from PIL import Image
import tensorflow as tf
from pygame import mixer
import cv2
import dlib
from imutils import face_utils
from mlxtend.image import extract_face_landmarks


###---------------------------------------------------------
### Prepare functions
###---------------------------------------------------------

# Function to detect eyes in a face picture
def eyes_recognition(landmarks, gray):

  # Calculate a margin around the eye
  extractmarge = int(len(gray)*0.05)
  color = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

  # Left eye maximal coordinates
  lx1 = landmarks[36][0]
  lx2 = landmarks[39][0]
  ly1 = landmarks[37][1]
  ly2 = landmarks[40][1]
  lefteye = color[ly1 - extractmarge : ly2 + extractmarge, lx1 - extractmarge : lx2 + extractmarge]

  # Right eye maximal coordinates
  rx1 = landmarks[42][0]
  rx2 = landmarks[45][0]
  ry1 = landmarks[43][1]
  ry2 = landmarks[46][1]
  righteye = color[ry1 - extractmarge : ry2 + extractmarge, rx1 - extractmarge : rx2 + extractmarge]

  # draw rectangles on color
  bonus = int(extractmarge/2)

  # Return eyes images
  return lefteye, righteye, lx1, lx2, ly1, ly2, rx1, rx2, ry1, ry2, bonus

# Function to preprocess eye informations extract with eye_detection function before launching the prediction
def eye_preprocess(eye):

  # Resize your image to fit model entry
  resize = tf.image.resize(
    eye,
    size = (52, 52),
    method = tf.image.ResizeMethod.BILINEAR
  )

  # Switch to grayscale
  grayscale = tf.image.rgb_to_grayscale(
      resize
  )

  # Normalize your data
  norm = grayscale / 255

  # Add one dimension to fit model entry
  final = tf.expand_dims(
      norm, axis = 0
  )

  # Return the final image to make your prediction
  return final

# Function to predict if eyes are opened or closed
def prediction(lefteye, righteye, model):

  class_labels = ["Fermes", "Ouverts"]

  # Predict and return predictions
  # For lefteye
  preds_left = model.predict(lefteye)
  pred_left = np.argmax(preds_left, axis = 1)
  # For righteye
  preds_right = model.predict(righteye)
  pred_right = np.argmax(preds_right, axis = 1)

  if pred_left == pred_right:
    state = class_labels[pred_left[0]]
  else:
    state = "Tu clignes!"

  return state


###---------------------------------------------------------
### Define your Streamlit app
###---------------------------------------------------------

def main():

    # Define sidebar (tabs) options
    with st.sidebar:


        choose = option_menu("Menu", ["Contexte","Montre ta tête !", "Balance ta cam", "Stream"],
                            icons=['house','camera fill','camera-video-fill'],
                            menu_icon="cast", default_index=0,
                            styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "green"},
            
        }
        )

    # Tab "Contexte": displays a page containing the description of the project context and the available options
    if choose == "Contexte":

        st.markdown(""" <style> .font {
        font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;} 
        </style> """, unsafe_allow_html=True)

        st.markdown('<p class="font">Projet Wake Up!</p>', unsafe_allow_html=True)    
        
        img = Image.open("C:/Users/Ophélie/Documents/Formations_Jedha/Data_Fullstack/WakeUp_projet/wakeup/App/vbt.jpg")
        st.image(img)

        st.markdown("""
                <br>Si vous conduisez régulièrement une voiture, il vous est forcément déjà arrivé de somnoler au volant...<br>
                Malheureusement ce n'est pas quelque chose que l'on peut se permettre et il est donc important d'éviter ce phénomène.<br><br>
                Pourtant, malgré le risque et la recommandation de s'arrêter toutes les 2h en moyenne, de nombreux accidents ont encore lieu à cause de la fatigue.
                Pour ce projet de fin d'étude nous avons donc cherché à mettre au point un algorithme capable de détecter l'un des signes d'endormissement: les yeux qui se ferment.<br>

                Bienvenue donc à toi dans notre interface de test!<br>
                Ici, tu peux tester notre algorithme de trois façons différentes:<br>
                - en téléchargeant directement ta photo depuis ton ordinateur (onglet Montre ta tête),<br>
                - en prenant une photo directement avec ta webcam (onglet Balance ta cam), <br>
                - ou encore en live, avec ta webcam (onglet Stream)!<br><br>

                Bonne viste! Et surtout, sois prudent au volant!<br>
                @La_Team_Wake_Up
                """, unsafe_allow_html=True)

    # Tab "Montre ta tête": displays a page offering the user to directly load an existing photo
    elif choose == "Montre ta tête !" :
        
        st.markdown(""" <style> .font {
        font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;} 
        </style> """, unsafe_allow_html=True)
        st.markdown('<p class="font">Montre ta tête!</p>', unsafe_allow_html=True)

        # File uploader
        uploaded_file = st.file_uploader("Sélectionne dans tes dossiers ou fais glisser ta photo...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:

            st.success("Ton image a bien été téléchargée!")
            st.image(uploaded_file)
            st.write("Ta prédiction va bientôt apparaître!")

            # Send request to FastAPI server
            api_url = "http://host.docker.internal:4000/predict"  
            data = {"file": uploaded_file.getvalue(), "type":"image/jpeg"}
            response = requests.post(api_url, files=data)

            if response.status_code == 200:
                result = response.json()
                if result['response'] == "close":
                    pred = "Tes yeux sont fermés!"
                elif result['response'] == "open":
                    pred = "Tes yeux sont ouverts!"
                else:
                    pred = "Tu clignes des yeux!"
                st.image(np.array(result["image"]))
                st.write("Résultat de la prédiction:", pred)

            else:
                st.image(uploaded_file)
                st.write("Oups... la prédiction a échoué! \nRetente avec une autre photo.")

    # Tab "Balance ta cam": displays a page offering the user to take a picture using their built-in camera
    elif choose == "Balance ta cam":

        st.markdown(""" <style> .font {
        font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;} 
        </style> """, unsafe_allow_html=True)
        st.markdown('<p class="font">Balance ta cam</p>', unsafe_allow_html=True)

        # File uploader
        uploaded_file = st.camera_input("Allume ta webcam et prends toi directement en photo!")

        if uploaded_file is not None:

            # Process the image here (e.g., save it to a specific location)
            st.success("Ton image a bien été téléchargée!")
            st.write("Ta prédiction va bientôt apparaître!")

            # Send request to FastAPI server
            api_url = "http://host.docker.internal:4000/predict"
            data = {"file": uploaded_file.getvalue(), "type":"image/jpeg"}
            response = requests.post(api_url, files=data)

            if response.status_code == 200:
                result = response.json()
                if result['response'] == "close":
                    pred = "Tes yeux sont fermés!"
                elif result['response'] == "open":
                    pred = "Tes yeux sont ouverts!"
                else:
                    pred = "Tu clignes des yeux!"
                st.image(np.array(result["image"]))
                st.write("Résultat de la prédiction:", pred)
                
            else:
                st.image(uploaded_file)
                st.write("Oups... la prédiction a échoué! \nRetente avec une autre photo.")

    # Tab "Stream": displays a page offering the user to make a live prediction of whether their 
    # eyes are open, closed (an alarm will sound if they are too long) or if they blink
    elif choose == "Stream":
        
        # Import model for predictions
        modelconv = tf.keras.models.load_model("CNN_model_2_gray.h5")

        st.markdown(""" <style> .font {
        font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;} 
        </style> """, unsafe_allow_html=True)
        st.markdown('<p class="font">Stream</p>', unsafe_allow_html=True)

        run = st.checkbox("Démarrer!")
        FRAME_WINDOW = st.image([])

        # Define a video capture object
        vid = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Import facial landmarks info and configure detector and predictor
        p = "shape_predictor_68_face_landmarks.dat"
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(p)

        # Initialize alarm 
        mixer.init()
        sound = mixer.Sound('The-purge-siren.wav')
        score = 0

        while run:
                
            state = "Oups... ca n'a pas marche"
                    
            # Capture the video frame by frame
            ret, frame = vid.read()

            height, width = frame.shape[:2] 
                
            # Converting the image to gray scale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Get faces into webcam's image
            rects = detector(frame, 0)

            # For each detected face, find eyes and make predictions
            # Increment a score of spleepiness
            for (i, rect) in enumerate(rects):

                shape = predictor(gray, rect)
                landmarks = face_utils.shape_to_np(shape)
                        
                lefteye, righteye, lx1, lx2, ly1, ly2, rx1, rx2, ry1, ry2, bonus = eyes_recognition(landmarks, gray)

                lefteye = eye_preprocess(lefteye)
                righteye = eye_preprocess(righteye)

                state = prediction(lefteye, righteye, modelconv)

                cv2.rectangle(frame, (lx1-bonus,ly1-bonus), (lx2+bonus,ly2+bonus), (255,0,0), 2)
                cv2.rectangle(frame, (rx1-bonus,ry1-bonus), (rx2+bonus,ry2+bonus), (255,0,0), 2)

            # Beep an alarm if the person if sleepy
            if state == "Fermes":
                score += 1
            elif state == "Ouverts":
                score -= 1

            if score < 0:
                score = 0
            if score > 5:
                sound.play(maxtime = 3000)
                score = 0
            
            # Show your state and score on live camera
            cam = state + "- Score : " + str(score)
            cv2.putText(frame, cam, (10, height-20), font, 1, (127, 0, 255), 1, cv2.LINE_AA)
                
            # Display the resulting frame
            FRAME_WINDOW.image(frame)
                    

if __name__ == '__main__':
    main()
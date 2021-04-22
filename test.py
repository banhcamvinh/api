import pyrebase
config = {
    "apiKey": "AIzaSyBYF170a8oXKkqgQrrfoPnZpa45a5AlGTI",
    "authDomain": "imgapi-144fe.firebaseapp.com",
    "databaseURL": "https://imgapi-144fe.firebaseio.com",
    "projectId": "imgapi-144fe",
    "storageBucket": "imgapi-144fe.appspot.com",
    "messagingSenderId": "888978133916",
    "appId": "1:888978133916:web:89c5a046ba04f30ad76e59",
    "measurementId": "G-6KX9HTXCGK"
}

firebase= pyrebase.initialize_app(config)
storage= firebase.storage()


# my_image="Screenshot (18).png"
# storage.child("/img/BANH CAM VINH.png").put(my_image)

# url= storage.child("/img/Screenshot (18).png").get_url(None)
# print(url)

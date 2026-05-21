from flask import Flask

app = Flask(__name__, static_folder='C:/Users/Ариша/PycharmProjects/PythonProject3/PythonProject/PythonProject/PythonProject/my_videoplatform/app/static', template_folder='C:/Users/Ариша/PycharmProjects/PythonProject3/PythonProject/PythonProject/PythonProject/my_videoplatform/app/templates')

from app import routes
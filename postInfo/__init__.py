from flask import Flask

from flask_cors import CORS

application = Flask(__name__)
CORS(application)

from postInfo import getAllPostInfo,getPostInfo,addAccommodation,addJob,addQandA,addOldProducts,addOtherServices
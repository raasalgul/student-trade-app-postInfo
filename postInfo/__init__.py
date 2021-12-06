from flask import Flask

application = Flask(__name__)

from postInfo import getAllPostInfo,getPostInfo,addAccommodation,addJob,addQandA,addOldProducts,addOtherServices
from flask import Flask

app = Flask(__name__)

from postInfo import getAllPostInfo,getPostInfo,addAccommodation,addJob,addQandA,addOldProducts,addOtherServices
# updateUserInfo,uploadPicture,verificationDoc
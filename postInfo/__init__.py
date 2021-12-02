from flask import Flask

app = Flask(__name__)

from postInfo import getAllPostInfo,getPostInfo
# updateUserInfo,uploadPicture,verificationDoc

from flask import Flask,redirect,render_template,request,make_response,jsonify
from werkzeug.utils import secure_filename
import os, pymongo, datetime
from bson.json_util import dumps

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='static/uploads/'
app.config['MAX_CONTENT_PATH']=512 * 1024 * 1024

@app.route('/')
def sayhi():
  return "Hi"

@app.route('/upload',methods=['GET','POST'])
def upload():
  if request.method=='GET':
    #display file upload box
    user=request.args['user']
    resp=make_response(render_template('upload.html',uplink='upload'))
    resp.set_cookie('user',user)
    return resp

  if request.method=='POST':
    #get file
    f = request.files['file']
    #save file name to database
    client = pymongo.MongoClient("mongodb+srv://lex:abcd1234@cluster0.ej3bx.mongodb.net/greyboard?retryWrites=true&w=majority")
    uploadername = request.cookies.get('user')
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    filename=secure_filename(f.filename)
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    moncollection = client.greyboard.upload
    id=moncollection.count_documents({})+1
    data={
      "id":id,
      "username":uploadername,
      "timeuploaded":current_time,
      "filename":filename
    }
    moncollection.insert_one(data)
    return 'success'

@app.route('/takequiz')
def takequiz():  
  if request.method=='GET':

    #get arguments from url
    user=request.args['user']
    id=request.args['id']

    #check database for score
    client = pymongo.MongoClient("mongodb+srv://lex:abcd1234@cluster0.ej3bx.mongodb.net/greyboard?retryWrites=true&w=majority")
    moncollection = client.greyboard.marks  
    data=moncollection.find({"name":user})
    try:
      datafin=list(data)[0]
    except:
      datafin=[]

    # display score if quiz already taken
    if id in datafin:
      scorecard={
        'marks':datafin[id],
        'name':user
      }
      
      # display as json
      return datafin[id]

    #Take quiz if no score
    else:

      moncollection = client.greyboard.quiz  
      data=moncollection.find({"quizid":id})
      datafin=list(data)
      datado=dumps(datafin[0]['data'])

      resp=make_response(render_template('takequiz.html',data=datado))
      resp.set_cookie('user',user)
      resp.set_cookie('id',id)
      return resp

@app.route('/savequiz', methods=['GET'])
# save quiz data from ajax jquery get
def savedata():
    user=request.cookies.get('user')
    id=request.cookies.get('id')
    score=request.args['score']

    data={
      "name":user,
      id:score,
    }

    client = pymongo.MongoClient("mongodb+srv://lex:abcd1234@cluster0.ej3bx.mongodb.net/greyboard?retryWrites=true&w=majority")
    moncollection = client.greyboard.marks
    moncollection.insert_one(data)
    resp=make_response("ok")
    return resp


   


@app.route('/makequiz')
def makequiz():
  #ask question and answers
  if request.method=='GET':
    user=request.args['user']
    resp=make_response(render_template('makequiz.html'))
    resp.set_cookie('user',user)
    return resp

  if request.method=='POST':
    #assign quiz id

    #store in db
    pass
  

if __name__ == '__main__':
    app.run(debug=True)

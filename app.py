from flask import Flask,request
from caesarcrud import CaesarCRUD
import datetime as dt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from caesarhash import CaesarHash
from flask_cors import CORS, cross_origin
from caesar_create_tables import CaesarCreateTables
import base64
from flask_socketio import SocketIO,emit
import jwt
import json
from flask_jwt_extended.utils import decode_token
import time
from CaesarAIEmail.CaesarAIEmail import CaesarAIEmail
#https://medium.com/@adrianhuber17/how-to-build-a-simple-real-time-application-using-flask-react-and-socket-io-7ec2ce2da977
app = Flask(__name__)
jwt = JWTManager(app)
app.config['SECRET_KEY'] = 'secret!'
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app,cors_allowed_origins="*")
JWT_SECRET = "Peter Piper picked a peck of pickled peppers, A peck of pickled peppers Peter Piper picked, If Peter Piper picked a peck of pickled peppers,Where's the peck of pickled peppers Peter Piper picked" #'super-secret'
JWT_ALGORITHM = app.config["JWT_ALGORITHM"]
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = dt.timedelta(days=1)

caesarcrud = CaesarCRUD()

# quotaposters table
caesarcreatetables = CaesarCreateTables()
caesarcreatetables.create(caesarcrud)
def jwt_secure_decode(authjwtheaderjson:dict):
    authorization = authjwtheaderjson["headers"]["Authorization"].replace("Bearer ","")
    current_user = decode_token(authorization)["sub"]
    return current_user
# $C, R, U, D
@app.route("/",methods=["GET"])
def index():
    return "Hello World"
@app.route('/quotapostersignup',methods=['POST'])
@cross_origin()
def quotapostersignup():
    try:
        signininfo = request.get_json()
        table = "quotaposters"
        company = signininfo['company']
        email = signininfo['email']
        password = signininfo['password']
        companyidentity = CaesarHash.hash_text(company + ":" + email)
        #print(companyidentity)
        fields = caesarcreatetables.quotapostersfields
        condition = f"company = '{company}' AND email = '{email}'"
        #print(condition)
        company_exists = caesarcrud.check_exists(("*"),table,condition)
        #print(company_exists)
        if company_exists:
            return {"message":"company already exists"}
        else:
            passwordhash = CaesarHash.hash_text_auth(password)
            result = caesarcrud.post_data(fields,(company,email,passwordhash,companyidentity),table)
            if result:
                access_token = create_access_token(identity=companyidentity)
                return {"access_token":access_token}
            else:
                return {"error":result["error"]}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
@app.route('/quotapostersignin',methods=['POST'])
@cross_origin() 
def quotapostersignin():
    try:
        signininfo = request.get_json()
        table = "quotaposters"
        company = signininfo['company']
        email = signininfo['email']
        password = signininfo['password']
        companyidentity = CaesarHash.hash_text(company + ":" + email)
        fields = caesarcreatetables.quotapostersfields
        condition = f"company = '{company}' AND email = '{email}'"
        company_exists = caesarcrud.check_exists(("*"),table,condition)
        if company_exists:
            result = caesarcrud.get_data(fields,table,condition)[0]
            password_matches = CaesarHash.match_hashed_text(result['password'],password)
            if password_matches:
                access_token = create_access_token(identity=companyidentity)
                return {"access_token":access_token}
            else:
                return {"message":"incorrect username or password"}
        else:
            return{"message":"incorrect username or password"}

    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
@app.route('/contributorsignin',methods=['POST'])
@cross_origin() 
def contributorsignin():
    try:
        signininfo = request.get_json()
        usernameid = signininfo.get("contributorid")
      
        table = "contributors"
        if not usernameid:
            username = signininfo['contributor']
            condition = f"contributor = '{username}'"
            contributoridentity = CaesarHash.hash_text(username)
        else:
            condition = f"contributorid = '{usernameid}'"
            contributoridentity = usernameid


        #email = signininfo['email']
        password = signininfo['password']
        
        fields = caesarcreatetables.contributorsfields
        
        contributor_exists = caesarcrud.check_exists(("*"),table,condition)
        if contributor_exists:
            result = caesarcrud.get_data(fields,table,condition)[0]
            password_matches = CaesarHash.match_hashed_text(result['password'],password)
            if password_matches:
                access_token = create_access_token(identity=contributoridentity)
                if usernameid:
                    username = caesarcrud.get_data(("contributor",),"contributors",f"contributorid = '{usernameid}'")
                    return {"access_token":access_token,"contributor":username[0]["contributor"]}
                else:   
                    return {"access_token":access_token}
            else:
                return {"message":"incorrect username or password"}
        else:
            return{"message":"incorrect username or password"}


    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
@app.route('/contributorsignup',methods=['POST'])
@cross_origin()
def contributorsignup():
    try:
        signininfo = request.get_json()
        table = "contributors"
        username = signininfo['contributor']
        email = signininfo['email']
        password = signininfo['password']
        companyidentity = CaesarHash.hash_text(username)
        emailhash = CaesarHash.hash_text(email)
        fields = caesarcreatetables.contributorsfields
        condition = f"contributor = '{username}'"
        contributor_exists = caesarcrud.check_exists(("*"),table,condition)
        if contributor_exists:
            return {"message":"contributor already exists"}
        else:
            passwordhash = CaesarHash.hash_text_auth(password)
            result = caesarcrud.post_data(fields,(username,email,passwordhash,emailhash,companyidentity),table)
            if result:
                access_token = create_access_token(identity=companyidentity)
                return {"access_token":access_token}
            else:
                return {"error":result["error"]}
    except Exception as ex:
        return {"error":f"{type(ex)}-{ex}"}
 

@app.route("/postquota",methods=["POST"])
@cross_origin()
@jwt_required() 
def postquota():
    user = get_jwt_identity()
   
    if user:
        try:
            data = request.get_json()
            table = "quotas"
            fields = caesarcreatetables.quotasfields
            quotatype = data["quotatype"]
            #print(data)

            quotahash = CaesarHash.hash_quota(data)
            quota_exists = caesarcrud.check_exists(("*"),table,f"quotahash = '{quotahash}'")
            if not quota_exists:
                data["quotahash"] = quotahash
                data["quoterkey"] = user
                thumbnail = data["thumbnail"] 
                
                filetype,thumbnailimg = thumbnail.split(",", 1)[0] + ",",thumbnail.split(",", 1)[1]
                thumbnailimg = thumbnailimg.encode("utf-8")
                thumbnailimg = base64.decodebytes(thumbnailimg)
                data["thumbnail"] = thumbnailimg
                data["thumbnailfiletype"] = filetype
                #print("ho")

                if tuple(data.keys()) == fields:
                
                    keys,data = caesarcrud.json_to_tuple(data)
                    #print(fields)
                    result = caesarcrud.post_data(fields,data,table)
                    if result:
                        quotatypetable = "quotatypes"
                        quotatypfields = caesarcreatetables.quotatypes
                        quotatypecondition = f"quotatype = '{quotatype}'"
                        quotatype_exists = caesarcrud.check_exists(("*"),quotatypetable,quotatypecondition)

                        if not quotatype_exists:
                            quotatyperesult = caesarcrud.post_data(quotatypfields,tuple([quotatype]),quotatypetable)
                            if quotatyperesult:
                                return {"message":"quota was posted."}
                            else:
                                return {"error":"quotatype was not added."}
                        else:
                            return {"message":"quota was posted."}
                    else:
                        return {"error":"An error occured, the quota was not posted."}

   
                else:
                    return {"error":"server side error, fields and values don't align."}

                
                #return {"message":"quota has been posted."}
            else:
                return {"message":"quota already exists."}
        except Exception as ex:
            CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"Post Quota Error: {type(ex)} - {ex}","attachment":None})
            return {"error":f"{type(ex)} -{ex}"}
    else:
        return {"error":"send jwt header."}
@app.route("/updatequota",methods=["PUT"])
@cross_origin()
@jwt_required() 
def updatequota():
    user = get_jwt_identity()
   
    if user:
        try:
            data = request.get_json()
            table = "quotas"
            old_quota = data["previousquota"]
            del data["previousquota"]
            quota = data
            old_quotahash = CaesarHash.hash_quota(old_quota)
            conditioncheck = f"quoterkey = '{user}' AND quotahash = '{old_quotahash}'"
            print(conditioncheck)
            quota_exists = caesarcrud.check_exists(("*"),table,conditioncheck)
            if "quotatitle" in quota and "quotatype" in quota:
                newquotahash = CaesarHash.hash_quota(quota)
                caesarcrud.post_data(caesarcreatetables.quotatypes,(quota["quotatype"],),"quotatypes")
            elif "quotatitle" in quota and "quotatype" not in quota:
                quotahashinp = {"quotatitle":quota["quotatitle"],"quotatype":old_quota["quotatype"]}
                newquotahash = CaesarHash.hash_quota(quotahashinp)
            elif "quotatitle" not in quota and "quotatype" in quota:
                quotahashinp = {"quotatitle":old_quota["quotatitle"],"quotatype":quota["quotatype"]}
                caesarcrud.post_data(caesarcreatetables.quotatypes,(quota["quotatype"],),"quotatypes")
                newquotahash = CaesarHash.hash_quota(quotahashinp)
            elif "quotatitle" not in quota and "quotatype" not in quota:
                newquotahash = None

            if quota_exists:
                
                if "thumbnail" in quota:
                    thumbnail = quota["thumbnail"]
                    filetype,thumbnailimg = thumbnail.split(",", 1)[0] + ",",thumbnail.split(",", 1)[1]
                    thumbnailimg = thumbnailimg.encode("utf-8")
                    thumbnailimg = base64.decodebytes(thumbnailimg)
                    fieldthumbnail,thumbnailvalue = "thumbnail",thumbnailimg
                    fieldthumbnailtype,thumbnailtypevalue = tuple(["thumbnailfiletype"]),tuple([filetype])
                    result = caesarcrud.update_blob(fieldthumbnail,thumbnailvalue,table,conditioncheck)
                    result = caesarcrud.update_data(fieldthumbnailtype,thumbnailtypevalue,table,conditioncheck)
                    del quota["thumbnail"]

                

                fieldsupdate = tuple(quota.keys())
                valuesupdate = tuple(quota.values())
                result = caesarcrud.update_data(fieldsupdate,valuesupdate,table,conditioncheck)
                if newquotahash:
                    fieldquotahash,quotahashvalue = tuple(["quotahash"]),tuple([newquotahash])
                    result = caesarcrud.update_data(fieldquotahash,quotahashvalue,table,conditioncheck)
                    res = caesarcrud.get_data(("company",),"quotaposters",f"quoterkey = '{user}'")
                    quotercompany = res[0]["company"]
                    result = caesarcrud.update_data(fieldquotahash,quotahashvalue,"askcontribpermission",f"quoter = '{quotercompany}'")


                if result:
                    return {"message":"quota was updated."}
                else:
                    return {"message":"quota was not updated."}
            else:
                return {"message":"quota doesn't exist."}
            # check old quota exixts
            # update set field  = newquota , condition oldquotahash
             
        except Exception as ex:
            CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"Update Quota Error: {type(ex)} - {ex}","attachment":None})
            return {"error":f"{type(ex)} -{ex}"}
@app.route("/responsequota",methods=["POST"])
@cross_origin()
def responsequota():
    data = request.get_json()
    return data

@socketio.on("getquotasbrowsews")
def getquotasbrowsews(dummydata):
    
    try:
        table = "quotas"
        fields = caesarcreatetables.quotasfields
        condition = f"visibility = 'public'"
        public_quota_exists = caesarcrud.check_exists(("*"),table,condition)
        #print(quoter_exists,"ho")
        if public_quota_exists:
            resultone = caesarcrud.get_data(fields,table,condition,getamount=1)
            if resultone:
                results = caesarcrud.get_large_data(fields,table,condition)
                for result in results:
                    
                    result = caesarcrud.tuple_to_json(fields,result)
                    del result["quotahash"],result["quoterkey"]
                    result["thumbnail"] = base64.b64encode(result["thumbnail"]).decode()
                    #print(result,"hi")
                    emit("getquotasbrowsews",{'data':result,'id':request.sid},broadcast=True)
                emit("getquotasbrowsews",{'data':{"message":"all data has been sent."},'id':request.sid},broadcast=True)
                    
            else:
                emit("getquotasbrowsews",{'data':{"message":"quotas do not exist."},'id':request.sid},broadcast=True)
        else:
            emit("getquotasbrowsews",{'data':{"message":"quoter has not posted first quota yet."},'id':request.sid},broadcast=True)


    except Exception as ex:
        CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"Get Quota Browse WS Error: {type(ex)} - {ex}","attachment":None})
        emit("getquotasws",{"error":f"{type(ex)} - {ex}"},broadcast=True)

@socketio.on("getquotasws")
def getquotasws(authinfo):
    
    try:
        #print(type(authinfo),authinfo)
        #authinfojson = json.loads(authinfo)
        current_user = jwt_secure_decode(authinfo)
        #print(current_user)
    

        table = "quotas"
        fields = caesarcreatetables.quotasfields
        condition = f"quoterkey = '{current_user}'"
        #print(condition)
        quoter_exists = caesarcrud.check_exists(("*"),table,condition)
        #print(quoter_exists,"ho")
        if quoter_exists:
            resultone = caesarcrud.get_data(fields,table,condition,getamount=1)
            if resultone:
                results = caesarcrud.get_large_data(fields,table,condition)
                for result in results:
                    
                    result = caesarcrud.tuple_to_json(fields,result)
                    del result["quotahash"],result["quoterkey"]
                    result["thumbnail"] = base64.b64encode(result["thumbnail"]).decode()
                    #print(result,"hi")
                    emit("getquotasws",{'data':result,'id':request.sid},broadcast=True)
                emit("getquotasws",{'data':{"message":"all data has been sent."},'id':request.sid},broadcast=True)
                    
            else:
                emit("getquotasws",{'data':{"message":"quotas do not exist."},'id':request.sid},broadcast=True)
        else:
            emit("getquotasws",{'data':{"message":"quoter has not posted first quota yet."},'id':request.sid},broadcast=True)


    except Exception as ex:
        if "(2013, 'Lost connection to MySQL server during query')" in str(ex):
            print("DB reset.")
            caesarcrud.caesarsql.reset_connection()
        CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"Get Quota WS Error: {type(ex)} - {ex}","attachment":None})
        emit("getquotasws",{"error":f"{type(ex)} - {ex}"},broadcast=True)
def fetchquota(subpath):
    try:
        table = "quotas"
        url = subpath.split("/")
        fields = caesarcreatetables.quotasfields
        data = {"quotatitle":url[1],"quotatype":url[2]}
        quotahash = CaesarHash.hash_quota(data)
        condition = f"quotahash = '{quotahash}' AND visibility = 'public'"
        
        quota_exists = caesarcrud.check_exists(("*"),table,condition)
        if quota_exists:
            quota = caesarcrud.get_data(fields,table,condition)[0]
            
            del quota["quotahash"],quota["quoterkey"]
            quota["thumbnail"] = base64.b64encode(quota["thumbnail"]).decode()
            return quota
        else:
            return {"quota doesn't exist."}
    except Exception as ex:
        CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"Get Quota Error: {type(ex)} - {ex}","attachment":None})
        return {"error":f"{type(ex)} -{ex}"}
@app.route("/getquota/<path:subpath>",methods=["GET"])
def getquota(subpath):
    return fetchquota(subpath)


        


@app.route("/deletequota/<path:subpath>",methods=["DELETE"])
@jwt_required()
def deletequota(subpath):
    user = get_jwt_identity()
    if user:
        try:
            table = "quotas"
            url = subpath.split("/")
            data = {"quotatitle":url[1],"quotatype":url[2]}
            quotahash = CaesarHash.hash_quota(data)
            condition = f"quotahash = '{quotahash}' AND quoterkey = '{user}'"
            quota_exists = caesarcrud.check_exists(("*"),table,condition)
            if quota_exists:
                quota = caesarcrud.delete_data(table,condition)
                quotaperm = caesarcrud.delete_data("askcontribpermission",f"quotahash = '{quotahash}' AND quoter = '{url[0]}'")
                if quota:
                    return {"message":"quota was deleted."}
                else:
                    return {"message":"quota was not deleted."}
            else:
                return {"message":"quota doesn't exist."}

            

        except Exception as ex:
            CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"Delete Quota Error: {type(ex)} - {ex}","attachment":None})
            return {"error":f"{type(ex)} -{ex}"}
@app.route("/getquotatypes",methods=["GET"])
def getquotatypes():
    try:
        fields = caesarcreatetables.quotatypes
        table = "quotatypes"
        quotatype_exists = caesarcrud.check_exists(("*"),table)
        if quotatype_exists:
            quotas = caesarcrud.get_data(fields,table,getamount=12)
            #rint(quotas)
            return {"quotatypes":quotas}
        else:
            return {"error":"there are no quotatypes."}
        



    except Exception as ex:
        CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"getquotatypes {type(ex)} - {ex}","attachment":None})
        return {"error":f"{type(ex)} -{ex}"}



@socketio.on('data')
def handle_message(data):
    """event listener when client types a message"""
    print("data from the front end: ",str(data))
    emit("data",{'data':data,'id':request.sid},broadcast=True)

@app.route("/contributeaskpermission/<path:subpath>",methods=["GET"])
@jwt_required()
def contributeaskpermision(subpath):
    user =  get_jwt_identity()
    if user:
        #rint(user)
        try:
            url = subpath.split("/")
            
            quotaposter = url[0]
            contributor = user
            quotadata = {"quotatitle":url[1],"quotatype":url[2]}
            quotahash = CaesarHash.hash_quota(quotadata)
            data = (quotaposter,contributor,quotahash,"pending") # Pending,Denied, Accepted
            quotatable = "quotas"
            conditioncheck = f"quotahash = '{quotahash}' AND quoter = '{quotaposter}'"
            quota_exists = caesarcrud.check_exists(("*"),quotatable,conditioncheck)
            if quota_exists:
                contributefields = caesarcreatetables.askcontribpermisionfield
                table = "askcontribpermission"
                condition = f"quoter = '{quotaposter}' AND contributor = '{contributor}' AND quotahash = '{quotahash}'"
                ask_contrib_perm_exists = caesarcrud.check_exists(("*"),table,condition)
                if ask_contrib_perm_exists:
                    return {"message":"Contribution permission already asked for."}
                else:
                    result = caesarcrud.post_data(contributefields,data,table)
                    if result:
                        return {"message":"Contributrion permission is now pending"}
                    else:
                        return {"message":"database post error."}


            else:
                return {"message":"quota doesn't exist to contribute."}
        except Exception as ex:
            CaesarAIEmail.send(**{"email":"amari.lawal@gmail.com","message":f"{type(ex)} - {ex}","subject":f"contributeaskpermision {type(ex)} - {ex}","attachment":None})
            return {"error":f"{type(ex)} -{ex}"}


        
        #condition = f"quotahash = '{quotahash}' AND visibility = 'public'"
        
        #quota_exists = caesarcrud.check_exists(("*"),table,condition)
        #return {"done":"message done."}
        #caesarai/ho/hem

@app.route("/checkaskpermission/<path:subpath>",methods=["GET"])
@jwt_required()
def checkaskpermission(subpath):
    user =  get_jwt_identity()
    if user:
        url = subpath.split("/")
        
        quotaposter = url[0]
        contributor = user
        quotadata = {"quotatitle":url[1],"quotatype":url[2]}
        quotahash = CaesarHash.hash_quota(quotadata)
        quotatable = "quotas"
        conditioncheck = f"quotahash = '{quotahash}' AND quoter = '{quotaposter}'"
        quota_exists = caesarcrud.check_exists(("*"),quotatable,conditioncheck)
        if quota_exists:
            contributefields = caesarcreatetables.askcontribpermisionfield
            table = "askcontribpermission"
            condition = f"quoter = '{quotaposter}' AND contributor = '{contributor}' AND quotahash = '{quotahash}'"
            ask_contrib_perm_exists = caesarcrud.check_exists(("*"),table,condition)
            if ask_contrib_perm_exists:
                return {"message":"true"}
            else:
                return {"message":"false"}


        else:
            return {"message":"quota doesn't exist to contribute."}
def fetchquotastatus(subpath,quotatable,conditioncheck,condition):
    quota_exists = caesarcrud.check_exists(("*"),quotatable,conditioncheck)
    if quota_exists:
        contributefields = caesarcreatetables.askcontribpermisionfield
        table = "askcontribpermission"
        
        ask_contrib_perm_exists = caesarcrud.check_exists(("*"),table,condition)
        if ask_contrib_perm_exists:
            result = caesarcrud.get_data(("contributor","permissionstatus"),table,condition)
            
            statuses = [contrib["permissionstatus"] for contrib in result]
            contributorhashes = [contrib["contributor"] for contrib in result]
            text = ""
            for i in contributorhashes:
                print(i)
                text += f"contributorid = '{i}'"
                text += " OR "
            finaltext = text[:text.rfind("OR")].strip()
            res = caesarcrud.get_data(("contributor",),"contributors",finaltext)
            print(result)
            if res:
                final_result = []
                for ind,contrib in enumerate(res):
                    if statuses[ind] != "denied":
                        contrib["permissionstatus"] = statuses[ind]
                        final_result.append(contrib) 
                #print(final_result)   
                quotaresult = fetchquota(subpath) 
                quotaresult["result"]  = final_result             
                return quotaresult
            else:
                quotaresult = fetchquota(subpath) 
                quotaresult["message"] = "get data failed."
                return quotaresult

        else:
            quotaresult = fetchquota(subpath) 
            quotaresult["message"] = "permission doesn't exist"
            return quotaresult


    else:
        return {"message":"quota doesn't exist to contribute."}
@app.route("/getquotastatusposter/<path:subpath>",methods=["GET"])
@jwt_required()
def getquotastatusposter(subpath):
    user =  get_jwt_identity()
    if user:
        try:

            url = subpath.split("/")
            
            quotaposter = url[0]
            quotadata = {"quotatitle":url[1],"quotatype":url[2]}
            quotahash = CaesarHash.hash_quota(quotadata)
            quotatable = "quotas"
            conditioncheck = f"quotahash = '{quotahash}' AND quoter = '{quotaposter}'"
            condition = f"quoter = '{quotaposter}' AND quotahash = '{quotahash}'"
            return fetchquotastatus(subpath,quotatable,conditioncheck,condition)

        except Exception as ex:
            return {"error":f"{type(ex)} - {ex}"}
        
@app.route("/getquotastatuscontrib/<path:subpath>",methods=["GET"])
@jwt_required()
def getquotastatuscontrib(subpath):
    user =  get_jwt_identity()
    if user:
        try:

            url = subpath.split("/")
            
            quotaposter = url[0]
            quotadata = {"quotatitle":url[1],"quotatype":url[2]}
            quotahash = CaesarHash.hash_quota(quotadata)
            quotatable = "quotas"
            conditioncheck = f"quotahash = '{quotahash}' AND quoter = '{quotaposter}'"
            condition = f"quoter = '{quotaposter}' AND quotahash = '{quotahash}' AND contributor = '{user}'"
            return fetchquotastatus(subpath,quotatable,conditioncheck,condition)

        except Exception as ex:
            return {"error":f"{type(ex)} - {ex}"}

@app.route("/changepermissionstatus",methods=["PUT"])
@jwt_required()
def changepermissionstatus():
    user =  get_jwt_identity()
    if user:
        data = request.get_json()
        status = data["status"]
        subpath = data["url"]
        contributor = data["contributor"]
        contributorhash = CaesarHash.hash_text(contributor)
        url = subpath.split("/")
        table= "askcontribpermission"
        quotaposter = url[0]
        quotadata = {"quotatitle":url[1],"quotatype":url[2]}
        quotahash = CaesarHash.hash_quota(quotadata)
        quotatable = "quotas"
        conditioncheck = f"quotahash = '{quotahash}' AND quoter = '{quotaposter}'"
        quota_exists = caesarcrud.check_exists(("*"),quotatable,conditioncheck)
        if quota_exists:
            table = "askcontribpermission"
            condition = f"quoter = '{quotaposter}' AND quotahash = '{quotahash}' AND contributor = '{contributorhash}'"
            ask_contrib_perm_exists = caesarcrud.check_exists(("*"),table,condition)
            if ask_contrib_perm_exists:
                res = caesarcrud.update_data(("permissionstatus",),(status,),table,condition)
                if res:
                    return {"message":f"contribution permission changed to {status}"}
                else:
                    return {"error":"error in update function. Didn't update correctly."}
            else:
                return {"error":"permission doesn't exist"}
        else:
            return {"error":"quota doesn't exist to contribute."}


@socketio.on("getcontribquotasws")
def getcontribquotasws(authinfo):
    
    try:
        #print(type(authinfo),authinfo)
        #authinfojson = json.loads(authinfo)
        current_user = jwt_secure_decode(authinfo)
        #print(current_user)
        table = "askcontribpermission"
        condition = f"contributor = '{current_user}'"
        #print(condition)
        contribution_exists = caesarcrud.check_exists(("*"),table,condition)
        #print(quoter_exists,"ho")
        if contribution_exists:
            result = caesarcrud.get_data(("quotahash","permissionstatus"),table,condition)
            if result:
                quotahashes = [contrib["quotahash"] for contrib in result]
                statuses = [contrib["permissionstatus"] for contrib in result]
                text = ""
                for i in quotahashes:
                    text += f"quotahash = '{i}'"
                    text += " OR "
                finaltext = text[:text.rfind("OR")].strip()
                quotafields = caesarcreatetables.quotasfields
                resultone = caesarcrud.get_data(quotafields,"quotas",finaltext,getamount=1)
                if resultone:
                    results = caesarcrud.get_large_data(quotafields,"quotas",finaltext)
                    for ind,result in enumerate(results):
                        result = caesarcrud.tuple_to_json(quotafields,result)
                        if quotahashes[ind] == result["quotahash"]:
                            result["permissionstatus"] = statuses[ind]
                        del result["quotahash"],result["quoterkey"]
                        result["thumbnail"] = base64.b64encode(result["thumbnail"]).decode()
                        #print(result,"hi")
                        emit("getcontribquotasws",{'data':result,'id':request.sid},broadcast=True)
                    emit("getcontribquotasws",{'data':{"message":"all data has been sent.","contributor":current_user},'id':request.sid},broadcast=True)
                        
                else:
                    emit("getcontribquotasws",{'data':{"message":"quotas do not exist."},'id':request.sid},broadcast=True)
            else:
                emit("getcontribquotasws",{'data':{"message":"permitted contribution exists."},'id':request.sid},broadcast=True)
        else:
            emit("getcontribquotasws",{'data':{"message":"first contribution has not been permitted.","contributor":current_user},'id':request.sid},broadcast=True)


    except Exception as ex:
        if "(2013, 'Lost connection to MySQL server during query')" in str(ex):
            print("DB reset.")
            caesarcrud.caesarsql.reset_connection()
        emit("getcontribquotasws",{"error":f"{type(ex)} - {ex}"},broadcast=True)

@app.route("/storemagneturi",methods=["GET","POST"])
@cross_origin()
@jwt_required()
def storemagneturi():
    current_user = get_jwt_identity()
    if current_user:
        try:
            torrentdetails = request.get_json()
            # TODO create a block for the blockchain without long mining and just reward them with a larger cut of coin.
            subpath = torrentdetails["quotaurl"]
            magneturi = torrentdetails["quotamagneturi"]
            torrentfilename = torrentdetails["torrentfilename"]
            filesize = torrentdetails["filesize"]
            url = subpath.split("/")
            table = "quotamagneturis"
            
            quotaposter = url[0]
            quotadata = {"quotatitle":url[1],"quotatype":url[2]}
            quotahash = CaesarHash.hash_quota(quotadata)
            condition = f"quotahash = '{quotahash}' AND contributor = '{current_user}' AND permissionstatus = 'accepted'"

            quota_exists = caesarcrud.check_exists(("*"),"askcontribpermission",condition)
            if quota_exists:
                magneturi_exists = caesarcrud.check_exists(("*"),table,f"quotahash = '{quotahash}' AND contributor = '{current_user}' AND quotamagneturi = '{magneturi}' AND quoter = '{quotaposter}'")
                if magneturi_exists:
                    return {"message":"magneturi already exists"},200
                else:
                    result = caesarcrud.post_data(caesarcreatetables.quotamagneturifields,(magneturi,torrentfilename,quotahash,current_user,quotaposter,filesize),table)
                    if result:
                        return {"message":"magneturi stored."},200
                    else:
                        return {"error","error when posting"},200

            else:
                return {"error":f"company or contributor doesn't exist."},200
            #quota_accepted_exists = importcsv.db.quotas_accepted.find_one({"companyid": companyid})
        except Exception as ex:
            return {"error":f"{type(ex)},{ex}"},400
def fetchmagneturi(condition,conditioncheck,getall=0):
    quota_exists = caesarcrud.check_exists(("*"),"quotas",conditioncheck)
    if quota_exists:
        table="quotamagneturis"
        magneturi_exists = caesarcrud.check_exists(("*"),table,condition)
        if magneturi_exists:
            result = caesarcrud.get_data(("quotamagneturi","torrentfilename","filesize"),table,condition)
            if result:
                if getall == 0:
                    return result[0]
                elif getall == 1:
                    return {"quotamagneturis":result}

            else:
                return {"message":" sql get request didn't work"},400
        else:
            return {"message":"magneturi does not exist."},200
    else:
        return {"error":"contributor is not authorized to fetch data to this quota."},200
@app.route("/getmagneturi",methods=["POST"])
@jwt_required()
def getmagneturi():
    current_user = get_jwt_identity()
    if current_user:
        data = request.get_json()
        subpath = data["quotaurl"]
        contributorid = CaesarHash.hash_text(data["contributor"]) 

        torrentfilename = data["torrentfilename"]
        url = subpath.split("/")
        quotaposter = url[0]
        data = {"quotatitle":url[1],"quotatype":url[2]}
        quotahash = CaesarHash.hash_quota(data)
        conditioncheck = f"quotahash = '{quotahash}' AND quoterkey = '{current_user}'"
        condition = f"quotahash = '{quotahash}' AND contributor = '{contributorid}' AND torrentfilename = '{torrentfilename}' AND quoter = '{quotaposter}'"
        return fetchmagneturi(condition,conditioncheck)

@app.route("/getallmagneturi",methods=["POST"])
@jwt_required()
def getallmagneturi():
    current_user = get_jwt_identity()
    if current_user:
        data = request.get_json()
        subpath = data["quotaurl"]
        contributorid = CaesarHash.hash_text(data["contributor"]) 

        url = subpath.split("/")
        quotaposter = url[0]
        data = {"quotatitle":url[1],"quotatype":url[2]}
        quotahash = CaesarHash.hash_quota(data)
        conditioncheck = f"quotahash = '{quotahash}' AND quoterkey = '{current_user}'"
        condition = f"quotahash = '{quotahash}' AND contributor = '{contributorid}' AND quoter = '{quotaposter}'"
        return fetchmagneturi(condition,conditioncheck,getall=1)
@app.route('/')
def hello_geek():
    print("hi")
    return '<h1>Welcome to the CaesarCoinMicroServices</h1>'
# generate jwt, and time -> hash 
# make request to 

# TODO Create quota poster CRUD API's

if __name__ == "__main__":
    #print(CaesarHash.hash_text("CaesarAI"))
    socketio.run(app, debug=True,port=5000,host="0.0.0.0")#,port=5000)
    #app.run(host="0.0.0.0", port=5000,debug=True)
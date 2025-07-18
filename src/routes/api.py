
import sanic, json, logging
import sanic.response
from .auth import protected

apiWebObj = sanic.Blueprint("apiWebObj", url_prefix="/api")

@apiWebObj.route("/login", methods=["POST"])
async def apiWebObj_login(request):
	jsonData = json.loads(request.body)
 	
	loginAttempt = await request.ctx.databaseObj.loginUser(request, jsonData["username"], jsonData["password"])
	logging.info(f"[ Login Attempt ] ( Status: {loginAttempt['status']} ) - Username: {jsonData['username']}")
	
	if loginAttempt['status'] == True:
		response = sanic.response.json({"status": True})
		
		response.add_cookie("token", loginAttempt["data"]['authToken'])

		return response
	else:
		return sanic.response.json({"status": False, "error": loginAttempt["message"]})
 
 
 
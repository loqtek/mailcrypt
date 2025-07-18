from functools import wraps

import jwt.exceptions
import sanic, random, string, time, hashlib, bcrypt
import jwt

def check_token(request):
	# check if required cookie/JWT token exists
	if request.cookies.get("token") == None: return {"status": False}

	# test jwt token to validate that it can be decoded with the secret_session_token
	try:
		jwtTokenObj = jwt.JWT().decode(
			message=request.cookies.get("token"),
			key=jwt.jwk.OctetJWK(request.ctx.configObj.secret_session_token.encode('utf-8')),
			algorithms=["HS256"],
			do_time_check=True
		)

		return {"status": True, "jwtTokenObj": jwtTokenObj}
	except:
		print("Invalid Token")
		return {"status": False}

def protected(wrapped):
# prevents unauthorized access to the system

	def decorator(f):
		@wraps(f)
		async def decorated_function(request, *args, **kwargs):
			authCheck = check_token(request) # check token for validity
			print(authCheck)
			if authCheck["status"] == True:
				request.ctx.authSessionObj = authCheck["jwtTokenObj"] # pass along decoded jwt contents in the "authSessionObj" context variable
				response = await f(request, *args, **kwargs)

				return response
			else: return sanic.response.redirect("/") # redirect 

		return decorated_function

	return decorator(wrapped)



async def verification(requestObj: sanic.Request, authUsername: str, authPasswd: str):

	# get user record from database
	userRecordObj = await requestObj.ctx.databaseObj.getUser(authUsername)

	# check if user is correct
	if authUsername == "admin":
		# make sure user-submitted passwd and stored database passwd match up
		if bcrypt.checkpw(authPasswd.encode('utf-8'), userRecordObj["data"].password.encode('utf-8')):
			randID = hashlib.sha256(str(random.getrandbits(128)).encode('utf-8')).hexdigest()
			# generate jwt token
			authToken = jwt.JWT().encode({
				"authUser": authUsername,
				"authTraveler": randID,
				"role": userRecordObj["data"].role,
				"iat": time.time()
			}, jwt.jwk.OctetJWK(requestObj.ctx.configObj.secret_session_token.encode('utf-8')))
   
			return {"status": True, "reason": "AUTH_SUCCESS", "authToken": authToken}
		else: return {"status": False, "reason": "INVALID_CREDENTIALS"}
	else: return {"status": False, "reason": "INVALID_CREDENTIALS"}


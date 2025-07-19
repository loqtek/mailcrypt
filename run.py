# import python modules
import sanic, argparse, logging, os, sys, sanic_jwt
from jinja2 import Environment, FileSystemLoader
import sanic.exceptions

# import webCore modules
from src.tools import toolkit, config, mail
from src import routes
from src.database import databaseFunc
from src.database.models import session

# ensure we running using root
if os.geteuid() != 0: 
    print("This script must be run as root (using sudo).")
    print(f"Re-run the script with: sudo (env/bin/python) {' '.join(sys.argv)}")
    exit(0)


logger = logging.basicConfig(level=logging.INFO)
logging.info("Logger setup successfully!")

# load config
configObj = config.Config()

sessionObj = session.sessionObj(configObj.database_full_url(), configObj.is_async())

databaseObj = databaseFunc.DatabaseObj(configObj=configObj, async_session=sessionObj.async_session)
toolkitObj = toolkit.toolkit(database=databaseObj, config=configObj)


argParseObj = argparse.ArgumentParser(
	prog='Mail Crypt Web (MCW)',
	description='The simple, lightweight, and portable email UI for SMTP / IMAP email servers',
 )

# args
argParseObj.add_argument("--dev", action="store_true", help="start server in debug/development mode")
argParseObj.add_argument("--prod", action="store_true", help="start server in production mode")
argParseObj.add_argument("-p", "--port", help="adjust/change server port from default (4020)")
argParseObj.add_argument("-v", "--verbose", action="store_true", help="enable verbose terminal output")
argParseObj.add_argument("-rst", "--reset", action="store_true", help="Attempt a 'reset' (Will Wipe Data)")

# initialization
dashboardObj = sanic.Sanic("map_dashboard")
parsedArgObj = argParseObj.parse_args()

# limiter
sanic_jwt.Initialize(dashboardObj, authenticate=routes.auth.verification, httponly=True, cookie_set=True, cookie_name="token", secure=True,cookie_expires=configObj.jwt_expire_time, secret=configObj.secret_session_token)

@dashboardObj.before_server_start
async def checkForResetDefault(app, loop):
	
	# database init
	if configObj.is_async():
		await sessionObj.init_db()
		logging.info("[DB] - The async database is ready")
	else:
		# for sqlite
		await sessionObj.init_db()
		logging.info("[DB] - The non-async database is ready")

	if configObj.reset_to_default == True:

		createAccount = await databaseObj.addNewUser(roleType="admin")
		if createAccount["status"]:
			print(f"Successfully created default user")
			logging.info(f"Successfully created default user")
		else:
			print(f"Error creating default user")

		configObj.set("setup", "reset_to_default", False); configObj.save()

	
	#if not parsedArgObj.dev:
	#    await databaseObj.randomizeSecretSessionToken()



# handle invalid page requests
@dashboardObj.exception(sanic.exceptions.NotFound)
async def handle_404(request, exception):
	error_page = Environment(loader=FileSystemLoader('./src/assets/public/html/')).get_template('notFound.html')
	return sanic.response.html(error_page.render(), status=404)


# server configuration
@dashboardObj.on_request
async def contextFiller(request):
    
	request.ctx.toolkitObj = toolkitObj
	request.ctx.configObj = configObj
	request.ctx.databaseObj = databaseObj
	request.ctx.authObj = routes.auth

	# variables
	request.ctx.serverMode = "development" if parsedArgObj.dev else "production"
	request.ctx.secretServerToken = request.ctx.configObj.secret_session_token

# blueprints
dashboardObj.blueprint(routes.publicWebObj)
dashboardObj.blueprint(routes.privateWebObj)
dashboardObj.blueprint(routes.apiWebObj)
dashboardObj.blueprint(routes.assetsWebObj)



if __name__ == "__main__":

	dashboardObj.run(
		host=("127.0.0.1" if not parsedArgObj.prod else "0.0.0.0"),
		port=(int(parsedArgObj.port) if parsedArgObj.port != None else 4020),
		dev=(True if parsedArgObj.dev else False),
		fast=(True if parsedArgObj.prod else False))

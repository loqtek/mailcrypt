import json, bcrypt, datetime, string, random
from .models import userModel
from sqlalchemy import select, func, and_, or_


class DatabaseObj:
	def __init__(self, configObj, async_session, debug: bool = False):
		self.async_session = async_session
		self.debug = debug
		self.configObj = configObj

	def _generate_id(self, count: int = 16):
		return ''.join(random.choices(string.ascii_letters + string.digits + r"!$%&*", k=count))


	async def loginUser(self, req: str, username, password: str):
		if self.configObj.is_async():
			async with self.async_session() as session:
				async with session.begin():
					result = await session.execute(
				        select(userModel.User).filter(userModel.User.username == username)
				    )
					user_record = result.scalar()
		else:
			with self.async_session() as session:
				result = session.execute(
		            select(userModel.User).filter(userModel.User.username == username)
		        )
				user_record = result.scalar()

		if not user_record:
			return {"status": False, "message": "Invalid username or password."}

		# paswd check
		if bcrypt.checkpw(password.encode('utf-8'), user_record.password.encode('utf-8')):
			if self.configObj.is_async():
				verifiyResults = await req.ctx.authObj.verification(req, username, password)
			else:
				verifiyResults = await req.ctx.authObj.verification(req, username, password)

			return {"status": True, "data": verifiyResults}
		else:
			return {"status": False, "message": "Invalid username or password."}



	async def addNewUser(self, username: str ="admin", password: str ="MailCryptAdmin!", roleType: str ="user"):
		if self.configObj.is_async():
			async with self.async_session() as session:
				async with session.begin():
					# Check for existing user
					result = await session.execute(
						select(userModel.User).filter(userModel.User.username == username)
					)
					existing_user = result.scalar()
					if existing_user:
						return {"status": False, "message": f"User '{username}' already exists."}

					if self.configObj.erase_database_on_reset and self.configObj.reset_to_default:
						await session.execute(userModel.User.__table__.delete())
	
					newUser = userModel.User(
						internalID=self._generate_id(32),
						username=username,
						password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
						role=roleType,
						created=datetime.datetime.now(),
						deleted=False,
					)					
					session.add(newUser)
	
				return {"status": True, "data": newUser}
		else:
			with self.async_session() as session:
				# Check for existing user
				result = session.execute(
					select(userModel.User).filter(userModel.User.username == username)
				)
				existing_user = result.scalar()
				if existing_user:
					return {"status": False, "message": f"User '{username}' already exists."}

				if self.configObj.erase_database_on_reset and self.configObj.reset_to_default:
					session.execute(userModel.User.__table__.delete())

				newUser = userModel.User(
					internalID=self._generate_id(32),
					username=username,
					password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
					role=roleType,
					created=datetime.datetime.now(),
					deleted=False,
				)

				session.add(newUser)
				session.commit()
				return {"status": True, "data": newUser}


	async def getUser(self, username: str):
		if self.configObj.is_async():
			async with self.async_session() as session:
				async with session.begin():
					query = select(userModel.User).filter(
					    or_(
					        userModel.User.username == username,
					        userModel.User.internalID == username
					    )
					)
					result = await session.execute(query)
					user = result.scalar()
		else:
			with self.async_session() as session:
				query = select(userModel.User).filter(
				    or_(
				        userModel.User.username == username,
				        userModel.User.internalID == username
				    )
				)
				result = session.execute(query)
				user = result.scalar()
		
		if user:
			return {"status": True, "data": user}
		else:
			return {"status": False}
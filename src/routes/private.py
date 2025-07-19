
import sanic

from jinja2 import Environment, FileSystemLoader

from .auth import protected

privateWebObj = sanic.Blueprint("privateWebObj", url_prefix="/private")
env = Environment(loader=FileSystemLoader('./src/assets/private/'))

# /mail
@privateWebObj.route("/mail")
@protected
async def homeWebObj_mail(request):
	indexTemplateObj = env.get_template('html/mail.html')
	
	indexRenderedTemplateObj = indexTemplateObj.render(

	)

	return sanic.response.html(indexRenderedTemplateObj)
 
 
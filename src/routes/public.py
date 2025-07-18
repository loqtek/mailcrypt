
import sanic, re, logging
import sanic.response

from jinja2 import Environment, FileSystemLoader

from .auth import protected

publicWebObj = sanic.Blueprint("publicWebObj", url_prefix="/")
env = Environment(loader=FileSystemLoader('./src/assets/public/'))


# /
@publicWebObj.route("/")
#@protected
async def homeWebObj_index(request):
	indexTemplateObj = env.get_template('html/login.html')
	
	indexRenderedTemplateObj = indexTemplateObj.render(

	)

	return sanic.response.html(indexRenderedTemplateObj)
 
 
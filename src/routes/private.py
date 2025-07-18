
import sanic

from jinja2 import Environment, FileSystemLoader

from .auth import protected

privateWebObj = sanic.Blueprint("privateWebObj", url_prefix="/mail")
env = Environment(loader=FileSystemLoader('./src/assets/private/'))


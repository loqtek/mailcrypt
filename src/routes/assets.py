
import sanic


assetsWebObj = sanic.Blueprint("assets", url_prefix="/assets")


assetsWebObj.static("/js/sweetalerts.js", "./src/assets/public/js/sweetalert.js", name="sweetalerts_js")
assetsWebObj.static("/js/tailwind.js", "./src/assets/public/js/tailwind.js", name="tailwind_js")



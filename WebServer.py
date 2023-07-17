import logging

from flask_login import LoginManager

import AIPlatformFrameworkConfig
from flask import Blueprint, render_template
from flask import Flask, request, jsonify
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect

global login_manager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
webserver_blueprint = Blueprint('webserver', __name__)
# auth = HTTPTokenAuth(scheme='Bearer')

class Config(object):
    DEBUG = AIPlatformFrameworkConfig.__IS_DEBUG__
    # SECRET_KEY = SECRET
    # UPLOAD_FOLDER = PlatformConfig.documents_path + UNPROCESSED
    # RECAPTCHA_PUBLIC_KEY = RECAPTCHA_PK
    # RECAPTCHA_PRIVATE_KEY = RECAPTCHA_SECRET



def create_webserver(maya_platform_):
    global maya_platform
    global webserver, csrf
    global api, jwt
    webserver = Flask(__name__, static_url_path='/static')
    webserver.register_blueprint(webserver_blueprint)
    webserver.config.from_object(Config)
    # webserver.secret_key = SECRET
    #webserver.config['WTF_CSRF_CHECK_DEFAULT'] = False #not Config.DEBUG

    #csrf=CSRFProtect(webserver)
    #api = Api(webserver)
    maya_platform = maya_platform_
    # api.add_resource(graph_data_base_endpoint, '/graph_data_base')
    # global service
    # service = service_

    return webserver

#@webserver_blueprint.before_request
#def check_csrf():
 #       csrf.protect()

@webserver_blueprint.route("/", methods=["GET"])
@webserver_blueprint.route("/index", methods=["GET"])
def index():
    return render_template('index.html',
                           title="Maya Gen 3",
                           version='v e r s i o n : ' + AIPlatformFrameworkConfig.VERSION)

"""
Get and post request for KG qa
"""
@webserver_blueprint.route('/import_pdf',methods=["POST"])
def import_pdf():
    data = request.get_json()
    url = data['url']
    #maya_platform.graph_service.kg.download_pdf(url, AIPlatformFrameworkConfig.document_path)
    # service.kg.download_pdf(url, AIPlatformFrameworkConfig.document_path)
    # service.core()

@webserver_blueprint.route('/import_conversation',methods=["POST"])
def import_conversation():
    data = request.get_json()
    user_id = int(data['user_id'])
    text = data['conversation']
    maya_platform.graph_service.kg.convert_conversation(user_id, text)
    return render_template('index.html',
                           title="Maya Gen 3",
                           version='v e r s i o n : ' + AIPlatformFrameworkConfig.VERSION)
    #if maya_platform.graph_service.kg.total_valid_sentence == 0:
     #   return "No valid information is stored"
    #else:
     #   return "information stored in graph memory system"


@webserver_blueprint.route('/query_info_extract',methods=["GET"])
def query_info_extract():
    #pass
    data = request.get_json()
    query = data['query']
    try:
        df = maya_platform.graph_service.kg.extract_table()
    except:
        #result = {
        #'error': "Can't retrieve graph memory system, no memory system is stored"
        #}
        #return jsonify(result)
        #return render_template('index.html',
        #                  title="Can't retrieve graph memory system, no memory system is stored",
        #                 version='v e r s i o n : ' + AIPlatformFrameworkConfig.VERSION)
        return "Can't retrieve graph memory system, no memory system is stored"
    #
    result = maya_platform.graph_service.qm.keyword_entity_extraction(query, df)
    if result == None:
        #result = {
        #'error': "There is no information related to query entity:"
        #}
        #return jsonify(result)
        #return render_template('index.html',
        #                  title="There is no information related to query entity:",
        #                 version='v e r s i o n : ' + AIPlatformFrameworkConfig.VERSION)
        return "Can't retrieve graph memory system, no memory system is stored"
    if maya_platform.graph_service.qm.returned_sentences == '':
        #result = {
        #'error': "There is no information related to query entity:"
        #}
        #return jsonify(result)
        #return render_template('index.html',
        #                  title="There is no information related to query entity:",
        #                 version='v e r s i o n : ' + AIPlatformFrameworkConfig.VERSION)
        #for i in self.query_entity:
        #print(i)
        return "Can't retrieve graph memory system, no memory system is stored"
    else:
        #return maya_platform.graph_service.qm.returned_sentences
        #result = {
        #'Information': maya_platform.graph_service.qm.returned_sentences
        #}
        #return jsonify(result)
        #return render_template('index.html',
                          # title=maya_platform.graph_service.qm.returned_sentences,
                           #version='v e r s i o n : ' + AIPlatformFrameworkConfig.VERSION)
        return maya_platform.graph_service.qm.returned_sentences




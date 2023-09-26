from zapv2 import ZAPv2
from random import randint
import socket,time
api="a2li71ihu873onr3mob525gnqc"
zap_ip = 'localhost' #name of a Docker container running Zap
target = 'http://localhost:30000'
auth_url = target + "webui/index.html"
port=3000
scanners = ['90020', '90029']
# authorized Web UI user
username = "admin"
password = "password"
auth_data = 'password={%password%}&username={%username#%}'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
zap = ZAPv2(proxies={'http': 'http://' + zap_ip + ':' + str(port),
    'https': 'http://' + zap_ip + ':' + str(port)},apikey=api)
new_context = randint(1, 100000000000)
# session = zap.core.session_location
session_name = 'session_1.session' if zap.core.session_location == \
    'session_0.session' else 'session_0.session'
zap.core.new_session(name=session_name)
zap.core.load_session(session_name)
context_id = zap.context.new_context(new_context)
zap.context.include_in_context(new_context, '.*')
zap.ascan.disable_all_scanners()
for scanner in scanners:
    zap.ascan.enable_scanners(scanner)
all_rules = [scanner for scanner in \
    zap.ascan.scanners() if scanner['enabled'] == 'true']
start_url = auth_url if auth_url else target
zap.urlopen(start_url)
auth_method_name = 'formBasedAuthentication'
authmethod_configparams = 'loginUrl=%s&loginRequestData=%s' % (auth_url, auth_data)
authcred_configparams = 'username=%s&password=%s' % (username, password)
zap.authentication.set_authentication_method(contextid=context_id,
    authmethodname=auth_method_name, 
    authmethodconfigparams=authmethod_configparams)
user_id = zap.users.new_user(contextid=context_id, name=username)
zap.users.set_authentication_credentials(contextid=context_id,
    userid=user_id,
    authcredentialsconfigparams=authcred_configparams)
zap.users.set_user_enabled(contextid=context_id, userid=user_id, enabled=True)
zap.forcedUser.set_forced_user(context_id, user_id)
zap.forcedUser.set_forced_user_mode_enabled('true')
spider = zap.spider.scan_as_user(url=target, contextid=context_id, 
    userid=user_id, recurse='false')
while (int(zap.spider.status()) < 100):
    time.sleep(2)
zap.ascan.scan(target)
zap.ascan.remove_all_scans()
zap.core.delete_all_alerts()
zap.context.remove_context(new_context)
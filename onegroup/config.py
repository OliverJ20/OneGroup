#GENERAL GLOBALS
working_dir = "/usr/local/onegroup"

database = "OneGroup.db"

config_file = "onegroup.conf"
config_path_main = "/etc/onegroup/"+config_file
config_path_backup = "/usr/local/onegroup/"+config_file

keys_dir = working_dir+"/keys/"
log_dir = "/var/log/"



#STANDARD CONFIG
tag = 'OG_'
base_config = {
    "openvpn_keys" : "/etc/openvpn/keys",
    "openvpn_ersa" : "/etc/openvpn/easy-rsa",
    "openvpn_server_config" : "/etc/openvpn/server.conf",
    "openvpn_client_config" : "/etc/openvpn/client.conf",
    "secret" : "RANDOM",
    "server_port" : 80,
    "server_host" : '0.0.0.0',
    "email" : "email@domain.com",
    "password" : "password",
    "mail_server" : "smtp.gmail.com",
    "mail_port" : 465,
}

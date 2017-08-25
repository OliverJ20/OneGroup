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

#IPTABLES RULES
iptables = [
    #Policy
    {"Rule" : "INPUT DROP", "Policy" : 1},
    {"Rule" : "FORWARD DROP", "Policy" : 1},
    {"Rule" : "OUTPUT DROP", "Policy" : 1},
    #VPN
    {"Rule" : "INPUT -i eth0 -s 192.168.1.0/24 -p udp --dport 1194 -j ACCEPT", "Policy" : 0}, 
    {"Rule" : "FORWARD -i eth0 -s 192.168.1.0/24 -p udp --dport 1194 -j ACCEPT", "Policy" : 0}, 
    {"Rule" : "OUTPUT -d 192.168.1.0/24 -p udp --sport 1194 -j ACCEPT", "Policy" : 0},

    {"Rule" : "INPUT -i tun0 -j ACCEPT", "Policy" : 0},
    {"Rule" : "FORWARD -i tun0 -j ACCEPT", "Policy" : 0},
    {"Rule" : "OUTPUT -o tun0 -j ACCEPT", "Policy" : 0},

    #Web Server
    {"Rule" : "INPUT -p tcp --dport 53 -j ACCEPT", "Policy" : 0}, 
    {"Rule" : "OUTPUT -p tcp --sport 53 -j ACCEPT", "Policy" : 0},
    
    {"Rule" : "INPUT -p tcp --dport 80 -j ACCEPT", "Policy" : 0}, 
    {"Rule" : "OUTPUT -p tcp --sport 80 -j ACCEPT", "Policy" : 0},

    {"Rule" : "INPUT -p tcp --dport 443 -j ACCEPT", "Policy" : 0}, 
    {"Rule" : "OUTPUT -p tcp --sport 443 -j ACCEPT", "Policy" : 0},

    {"Rule" : "INPUT -p tcp --dport 3128 -j ACCEPT", "Policy" : 0}, 
    {"Rule" : "OUTPUT -p tcp --sport 3128 -j ACCEPT", "Policy" : 0},

    #SSH
    {"Rule" : "INPUT -p tcp --dport 22 -j ACCEPT", "Policy" : 0}, 
    {"Rule" : "OUTPUT -p tcp --sport 22 -j ACCEPT", "Policy" : 0},
]


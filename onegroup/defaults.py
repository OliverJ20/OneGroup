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
    "openvpn_ccd" : "/etc/openvpn/ccd",
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

#USABLE 4TH OCTETS FOR GROUP SUBNETS
usable_octets = [1,2,5,6,9,10,13,14,17,18,
        21,22,25,26,29,30,33,34,37,38,
        41,42,45,46,49,50,53,54,57,58,
        61,62,65,66,69,70,73,74,77,78,
        81,82,85,86,89,90,93,94,97,98,
        101,102,105,106,109,110,113,114,117,118,
        121,122,125,126,129,130,133,134,137,138,
        141,142,145,146,149,150,153,154,157,158,
        161,162,165,166,169,170,173,174,177,178,
        181,182,185,186,189,190,193,194,197,198,
        201,202,205,206,209,210,213,214,217,218,
        221,222,225,226,229,230,233,234,237,238,
        241,242,245,246,249,250,253,254]


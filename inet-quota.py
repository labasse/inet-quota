import subprocess, json, sys, os
from datetime import datetime


def block_user(mac_addresses, block=True):
    """Block or unblock user by mac addresses"""
    cmd, stderr = ("-I", None) if block else ("-D", subprocess.DEVNULL)
    for mac in mac_addresses:
        subprocess.run(["iptables", cmd, "FORWARD", "-m", "mac", "--mac-source", mac, "-j", "DROP"], stderr=stderr)


def get_traffic_stats():
    """Packet num by iptable rule"""
    output = subprocess.check_output(["sudo", "iptables", "-L", "FORWARD", "-vn", "-x"]).decode()
    stats = {}
    for line in output.splitlines():
        if "MAC" in line:
            parts = line.split()
            bytes_count = int(parts[1])
            mac = parts[11].upper()
            stats[mac] = bytes_count
    return stats


def main():   
    if len(sys.argv) != 3:
        print("Usage: quota_manager.py <config_file> <data_path>")
        sys.exit(1)

    data_file = os.path.join(
        sys.argv[2], 
        f"usage-{datetime.now().strftime('%Y-%m-%d')}.json"
    )
    with open(sys.argv[1], 'r') as f: 
        conf = json.load(f)
    
    if not os.path.exists(data_file):
        data = { "user_times": {}, "devices": {} }
        for user, info in conf["users"].items():
            data["user_times"][user] = 0
            for mac in info["devices"].values():
                data["devices"][mac] = { "user": user, "bytes": 0 }
            block_user(info["devices"].values(), block=False)
    else:
        with open(data_file, 'r') as f: data = json.load(f)

    current_stats = get_traffic_stats()    
    users = set()
    for mac, bytes_count in current_stats.items():
        if mac in data["devices"] and bytes_count > data["devices"][mac]["bytes"]:
            data["devices"][mac]["bytes"] = bytes_count
            users.add(data["devices"][mac]["user"])

    for userid, info in conf["users"].items():
        limit = conf["daily"][datetime.now().weekday()]
        data[userid] += 1
        if data[userid] >= limit:
            print(f"Blocked {userid} (Quota reached: {limit}min)")
            block_user(info["devices"].values())
        
    with open(data_file, 'w') as f: json.dump(data, f)


if __name__ == "__main__":
    main()
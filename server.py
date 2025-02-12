import gzip
import json
import os
import time
import traceback
import sys
from datetime import timedelta, date, datetime

import requests

worth = {
    216: 0,  # starter helm
    222: 0,  # starter hatch
    117: 0,  # starter wrench
    231: 0,  # starter thruster
    118: 0,  # starter shredder
    119: 0,  # hand cannon
    247: 0,  # starter fab
    254: 0,  # annilator
    259: 0,  # bulk
    260: 0,  # bulk
    261: 0,  # nav
    227: 0,  # starter rc
    162: 0,  # Booster
    163: 0,  # Booster
    164: 0,  # Booster
    165: 0,  # Booster

    300: 0,  # Eternal bronze
    301: 0,  # Eternal silver
    302: 0,  # Eternal gold
    304: 0,  # Eternal Platinum
    303: 0,  # Eternal flux

    323: 0, # Red Gremlin (r/place ship)
    121: 0, # Sandbox RCD

    1: 1 / 24,  # metal
    2: 1 / 24,  # explo
    4: 1 / 2,  # rubber
    5: 1,  # flux
    49: 1 / 32 * 24,  # compressed explo
    50: 1 / 32 * 24,  # compressed metal

    51: 16,  # Vollyball
    53: 16,  # Basketball
    55: 16,  # beachjabll
    56: 16,  # football
    115: 20,  # Manifest
    116: 20,  # bom
    120: 2,  # bp scanner
    122: 32,  # flux rcd
    123: 1 / 6,  # core
    226: 2,  # RC
    228: 14,  # burst
    229: 20,  # auto / machine
    234: 1 / 4,  # ice
    256: 2,  # shield generator
    257: 8,  # shield proj
    258: 2,  # enchanced
    108: 2, # backpack

    264: 2, # munitions supply unit
    263: 20, # acute
    265: 20, # obtuse

    326: 16, # elimination lootbox

    246: 30000,  # Leg
    102: 60000,  # gs
    305: 1500000,  # gold null
    306: 1000000,  # bug hunter
    307: 300000,  # silver null
}
worth[167] = worth[234] * 4;
worth[166] = worth[234] * 4;

ignore = [
    3, # silica
    225, # Normal turrets prob
    100000 # Debug item?
]
raw_schema = requests.get("https://pub.drednot.io/test/econ/item_schema.json").json()
schema = {}
for s in raw_schema:
    schema[s["id"]] = s
ALERT = [
    323, # Gremlin
    121
]

LEADERBOARD_HEX = []
def getworth(item):
    if "fab_recipe" in item:
        count = item["fab_recipe"]["count"]
        w = 0
        for i in item["fab_recipe"]["input"]:
            w += getworth(schema[i["id"]]) * i["count"]
        w /= count
        return w
    else:
        if item["id"] in worth:
            return worth[item["id"]]
        else:
            raise Exception(f"Failed to find item:\nID:{item['id']}\nName:{item['name']}")

def calculateNetworth(hexcode, items, full):
    w = 0
    for item in items:
        itemid = int(item)
        if itemid in ignore:
            continue
        if itemid == 244:
            itemid = 252
        if itemid in ALERT:
            log("ALERT ITEM FOUND", json.dumps(full, indent=4))
        w += getworth(schema[itemid]) * items[item]
    if len(hexcode) == 4:
        w += worth[246]
    return w
FETCHING = False
log = None
def fetchShips(logger):
    global FETCHING, log, sorted_items, LEADERBOARD_HEX
    log = logger
    log("testing.")
    if FETCHING: return
    FETCHING = True
    today = datetime.utcnow().date()
    if currentShips["dates"] == "":
        current_date = date(2022, 11, 23)
    else:
        dd = currentShips["dates"].split("_")
        current_date = date(int(dd[0]), int(dd[1]), int(dd[2]))

    st = time.time()
    total = (today - current_date).days
    averageFetchTime = -1
    savecounter = 0
    updated = False
    first = True
    checker = today - timedelta(days=1)
    if f"{today.year}_{today.month}_{today.day}" == currentShips["dates"]:
        log(f"Attempted to fetch, dates same! ({current_date}, {today.year}_{today.month}_{today.day})")
        return
    else:
        log(f"Attempting to fetch shiplist, starting at day {current_date} - {today.year}_{today.month}_{today.day}")
    while current_date <= today:
        date_string = f"{current_date.year}_{current_date.month}_{current_date.day}"
        updated = True
        url = f"https://pub.drednot.io/prod/econ/{date_string}/ships.json.gz"
        pt = time.time()
        cont = requests.get(url).content
        try:
            data = json.loads(gzip.decompress(cont))
        except:
            log(traceback.format_exc())
            log(cont)
            sorted_items = sorted(currentShips["ships"].items(), key=lambda item: item[1]['w'], reverse=True)
            LEADERBOARD_HEX = [item[0] for item in sorted_items]
            return


        for ship in data:
            currentShips["ships"][ship["hex_code"]] = {
                "n":ship["name"],
                "c": ship["color"],
                "w": calculateNetworth(ship["hex_code"], ship["items"], ship)
            }

        daysleft = (today - current_date).days
        fetchtime = time.time() - pt
        averageFetchTime = averageFetchTime*0.75 + fetchtime*0.25 if averageFetchTime != -1 else fetchtime

        current_date += timedelta(days=1)
        currentShips["dates"] = date_string
        st = time.time()
        savecounter += 1
        if savecounter > 10:
            savecounter = 0
            json.dump(currentShips, open("./savedata/ships.json", "w"))
        log(f"Fetched {date_string} in {int(fetchtime*100)/100} sec // {total-daysleft}/{total} // est: {int(daysleft * averageFetchTime*1000)/1000} // Saved in {int((time.time() - st) * 1000)/1000} // Total ships: {len(currentShips['ships'])} v {len(data)}")
    if updated:
        json.dump(currentShips, open("./savedata/ships.json", "w"))
    sorted_items = sorted(currentShips["ships"].items(), key=lambda item: item[1]['w'], reverse=True)
    LEADERBOARD_HEX = [item[0] for item in sorted_items]
    FETCHING = False

def calculateNetworthShiplist(shiplist):
    out = []
    totalworth = 0
    for shiptag in shiplist["ships"]:
        if shiplist["ships"][shiptag]["owned"]:
            hex_code = shiplist["ships"][shiptag]["hex_code"]
            name = shiplist["ships"][shiptag]["team_name"]
            icon = shiplist["ships"][shiptag]["icon_path"]
            load_time = datetime.utcfromtimestamp(shiplist["ships"][shiptag]["time"]).strftime('%Y-%m-%d')
            shipworth = round(currentShips["ships"][hex_code]["w"]) if hex_code in currentShips["ships"] else -1
            totalworth += max(shipworth, 0)
            placement = LEADERBOARD_HEX.index(hex_code) + 1 if hex_code in LEADERBOARD_HEX else -1
            out.append({
                "hex_code": hex_code,
                "name": name,
                "icon": icon,
                "load_time": load_time,
                "shipworth": shipworth,
                "placement": placement
            })
    out = sorted(out, key=lambda x: x['shipworth'], reverse=True)
    return [currentShips["dates"], totalworth, out]
def abbreviate_number(num):
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}b"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}m"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}k"
    else:
        return str(num)
def createShipEntree(hex_code):
    ship = currentShips["ships"][hex_code]
    return {
      "name": ship["n"],
      "hex": hex_code,
      "value": round(ship['w']),
    }

def safeGetEntree(hex_code: str):
    hex_code = hex_code.upper().strip().replace("{", "").replace("}", "")
    if hex_code in LEADERBOARD_HEX:
        return {"shipData":createShipEntree(hex_code), "rank":LEADERBOARD_HEX.index(hex_code) + 1}
    else:
        return {"shipData":None}

ENTREES_PER_PAGE = 20
def get_page_entries(data, page):
    start_index = int(page) * ENTREES_PER_PAGE
    end_index = start_index + ENTREES_PER_PAGE

    if start_index >= len(data):
        return False

    return data[start_index:end_index]

def findShipByName(name):
    results = []
    name = name.lower()
    for hex_code in LEADERBOARD_HEX:
        if name in currentShips["ships"][hex_code]["n"].lower():
            results.append(hex_code)
        if len(results) >=500:
            break
    return results

def text_findshipbyname(name):
    r = findShipByName(name)
    if len(r) == 0:
        return json.dumps({"entries": 0, "ships":[]})
    text = {"entries": len(r), "ships":[]};
    for hexcode in r:
        text["ships"].append({"shipData":createShipEntree(hexcode), "rank":LEADERBOARD_HEX.index(hexcode) + 1});
    return json.dumps(text);

def getLeaderboardNetworth(page):
    ships = get_page_entries(LEADERBOARD_HEX, page)
    if not ships:
        return {"ships":[]};
    content = {"ships":[]}
    for ship in ships:
        content["ships"].append({"rank": LEADERBOARD_HEX.index(ship)+1, "shipData":createShipEntree(ship)});
    return content

def start(logger):
    global currentShips, sorted_items, LEADERBOARD_HEX
    try:
        currentShips = json.load(open("./savedata/ships.json"))
    except:
        currentShips = {"dates": "", "ships": {}}
    sorted_items = sorted(currentShips["ships"].items(), key=lambda item: item[1]['w'], reverse=True)
    LEADERBOARD_HEX = [item[0] for item in sorted_items]
    fetchShips(logger)
    
import json
import requests
from datetime import timedelta, date, datetime, timezone
import os
import time
import gzip
import math
import lz4.frame as lz4
import msgpack

SOURCE_MAP = ["Orange Fool", "The Coward", 
              "Red Sentry", "Blue Rusher", "Aqua Shielder", "The Shield Master", "Shield Helper", 
              "Yellow Hunter", "Red Sniper", "The Lazer Enthusiast", "Yellow Mine Guard",
              "bot - zombie", "bot - zombie tank", "bot - zombie hunter", "bot - zombie boss",
              "giant rubber ball",
              "block - iron mine",
              "block - flux node",
              "block - vault",
              "block - treasure diamond",

              "block - flux mine",
              "bot - blue melee", "bot - orange fool", "bot - red sentry", 
              "bot - yellow rusher", "bot - red hunter", "bot - green roamer",
              "bot - blue shield"]
ZONE_MAP = [
    "The Nest",
    "Hummingbird", "Finch", "Sparrow",
    "Raven", "Falcon",
    "Canary", "The Pits", "Vulture",
    "Event Lobby",

    "Freeport I", "Freeport II", "Freeport III", "Combat Simulator",

    "Super Special Event Zone"
]

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def _compress_metadata(time, zone, serv, item, count, srclength, dstlength, hurt, killed):
    hurt = int(hurt)
    killed = int(killed)
    assert 0 <= time < (1 << 32)
    assert 0 <= zone < (1 << 8)
    assert 0 <= serv < (1 << 8)
    assert 0 <= item < (1 << 12)
    assert 0 <= count < (1 << 24)
    assert 0 <= srclength < (1 << 5)
    assert 0 <= dstlength < (1 << 5)
    assert 0 <= hurt < (1 << 1)
    assert 0 <= killed < (1 << 1)

    return (time << (8 + 8 + 12 + 24 + 5 + 5 + 1 + 1)) | \
               (zone << (8 + 12 + 24 + 5 + 5 + 1 + 1)) | \
               (serv << (12 + 24 + 5 + 5 + 1 + 1)) | \
               (item << (24 + 5 + 5 + 1 + 1)) | \
               (count << (5 + 5 + 1 + 1)) | \
               (srclength << (5 + 1 + 1)) | \
               (dstlength << (1 + 1)) | \
               (hurt << 1) | \
               killed

def _compress_hex(hex_str):
    if len(hex_str) > 12:
        raise ValueError("Invalid hex string, " + hex_str)
    return (int(hex_str, 16) & (1 << 48) - 1).to_bytes(6, byteorder='big')

SIMPLIFICATION_TIME = 60
def _compress_log(date, path, logger):
    st = time.time()
    url = f"https://pub.drednot.io/prod/econ/{date}/log.json.gz"
    logger("")
    logger(f"Fetching {url}")
    timer_fetch = time.time()
    fetch_raw = gzip.decompress(requests.get(url).content).decode("utf-8")
    logfile = json.loads(fetch_raw)
    timer_fetch = time.time() - timer_fetch
    timer_simplify = time.time()
    compressed = []
    compressed_dict = {}

    # Iterate through logfile
    for log in logfile:
        key = (log["src"], log["dst"], log["item"], log["zone"], log["serv"])
        
        if key in compressed_dict:
            if compressed_dict[key]["lastTime"] + SIMPLIFICATION_TIME > log["time"]:
                c = compressed_dict[key]
                c["lastTime"] = log["time"]
                c["count"] += log["count"]
            else:
                compressed.append(compressed_dict[key])
                del compressed_dict[key]
                log["lastTime"] = log["time"]
                compressed_dict[key] = log
        else:
            log["lastTime"] = log["time"]
            compressed_dict[key] = log
    compressed.extend(compressed_dict.values())
    compressed = sorted(compressed, key=lambda x: x["time"])
    timer_simplify = time.time() - timer_simplify
                    
    chunks = []
    c = 0
    timer_encode = time.time()
    for log in compressed:
        log_time = log["time"]
        zone = log["zone"]
        serv = log["serv"]
        src = log["src"]
        dst = log["dst"]
        item = log["item"]
        count = log["count"]
        hurt = False

        srclength = 0
        dstlength = 0
        killed = False
        if src[0] == "{":
            if "hurt" in src:
                hurt = True
            src = src.split(" ")[0].strip("{}")
            srclength = len(src)
            src = _compress_hex(src)
        else:
            if src not in SOURCE_MAP:
                raise Exception("source, " + src)
            src = SOURCE_MAP.index(src).to_bytes(6, byteorder='big')
        if dst[0] == "{":
            dst = dst.strip("{}")
            dstlength = len(dst)
            dst = _compress_hex(dst)
        else:
            killed = True
            dst = (0).to_bytes(6, byteorder='big')
        if zone not in ZONE_MAP:
            raise Exception("zone, " + zone)
        zone = ZONE_MAP.index(zone)

        metadata = _compress_metadata(log_time, zone, serv, item, count, srclength, dstlength, hurt, killed)
        metadata = metadata.to_bytes(12, byteorder='big')
        newlog = metadata+src+dst
        chunks.append(newlog)
        c += 1
    timer_encode = time.time() - timer_encode
    timer_unchunk = time.time()
    strawblog = b"".join(chunks)
    timer_unchunk = time.time() - timer_unchunk
    with open(path, "wb") as write:
        write.write(lz4.compress(strawblog))
    logger(f"Processed in {round(time.time() - st, 2)} sec // "+\
           f"Fetch {round(timer_fetch, 2)} // Simp: {round(timer_simplify, 2)} // Process {round(timer_encode, 2)} // CNK: {round(timer_unchunk, 2)}")
    logger(f"({len(logfile)} -> {len(compressed)} entries, {convert_size(len(fetch_raw))} -> {convert_size(len(strawblog))})")
    return strawblog

def _decode_metadata(combined):
    killed = bool(combined & 0b1)
    hurt = bool((combined >> 1) & 0b1)
    dstlength = (combined >> 2) & 0b11111
    srclength = (combined >> 7) & 0b11111
    count = (combined >> 12) & 0xFFFFFF
    item = (combined >> 36) & 0xFFF
    serv = (combined >> 48) & 0xFF
    zone = (combined >> 56) & 0xFF
    time = (combined >> 64) & 0xFFFFFFFF
    return time, ZONE_MAP[zone], serv, item, count, srclength, dstlength, hurt, killed

def _decode_entry(chunk):
    metadata = int.from_bytes(chunk[:12], byteorder='big')
    metadata = _decode_metadata(metadata)
    a = metadata[5]
    b =  metadata[6]
    if a == 0:
        src = SOURCE_MAP[int.from_bytes(chunk[12:18], 'big')]
    else:
        src = chunk[12:18].hex().lstrip('0').upper().zfill(a)
    
    if b == 0:
        dst = "killed"
    else:
        dst = chunk[18:24].hex().lstrip('0').upper().zfill(b)
    d = {
            "time":metadata[0],
            "zone":metadata[1],
            "serv":metadata[2],
            "src":src,
            "dst":dst,
            "item":metadata[3],
            "count":metadata[4]
        }
    return d

SERVER_TO_NAME = ["US", "EU", "AS"]

class Econlogger:
    def __init__(self, logger) -> None:
        logger("Starting transfer logger, os: " + os.name)
        self.log = logger
        self.fetching = False
        self.DATABASE_PATH = os.path.abspath("./savedata/strawblogs")
        self.data = []
        self.current_date = date(2022, 11, 23)
        rawschema = requests.get('https://pub.drednot.io/prod/econ/item_schema.json').json()
        self.schema = {}
        self.loaded = False
        for item in rawschema:
            self.schema[item["id"]] = item
        if not os.path.exists(self.DATABASE_PATH):
            logger("Created database")
            os.mkdir(self.DATABASE_PATH)
        st = time.time()
        logger("Starting loading shipname data")
        if not os.path.exists(self.DATABASE_PATH + "/shipnames.strawblogs"):
            with open(self.DATABASE_PATH + "/shipnames.strawblogs", "wb") as f:
                f.write(lz4.compress(msgpack.dumps({"current_date": [2022, 11, 22]})))
            self.shipnames = {"current_date": [2022, 11, 22]}
            self.shipnamescurrentdate = date(2022, 11, 22)
        else:
            with open(self.DATABASE_PATH + "/shipnames.strawblogs", "rb") as f:
                self.shipnames = msgpack.loads(lz4.decompress(f.read()))
            d = self.shipnames["current_date"]
            self.shipnamescurrentdate = date(d[0], d[1], d[2])
        logger(f"Loaded shipname data in {round(time.time()-st)} sec.")

    def _get_ship_names(self, date_string):
        st = time.time()
        url = f"https://pub.drednot.io/prod/econ/{date_string}/ships.json.gz"
        self.log("")
        self.log(f"Fetching {url}")
        timer_fetch = time.time()
        fetch_raw = gzip.decompress(requests.get(url).content).decode("utf-8")
        ship_logs = json.loads(fetch_raw)
        timer_fetch = time.time() - timer_fetch
        timer_process = time.time()
        for ship in ship_logs:
            hex_code = ship["hex_code"].strip("{}")
            color = ship["color"]
            name = ship["name"]
            if hex_code in self.shipnames:
                if self.shipnames[hex_code][-1][0] != name or self.shipnames[hex_code][-1][1] != color:
                    self.shipnames[hex_code].append((name, color, date_string))
            else:
                self.shipnames[hex_code] = [(name, color, date_string)]
        timer_process = time.time() - timer_process
        d = [int(x) for x in date_string.split("_")]
        self.shipnamescurrentdate = date(d[0], d[1], d[2])
        self.shipnames["current_date"] = d
        self.log(f"Processed in {round(time.time() - st, 2)} sec // "+\
           f"Fetch {round(timer_fetch, 2)} // Process {round(timer_process, 2)}")
        self.log(f"({len(ship_logs)} entries, {convert_size(len(fetch_raw))} -> {convert_size(len(lz4.compress(msgpack.dumps(self.shipnames))))})")

    def fetch(self):
        if self.fetching:
            return
        if not self.loaded:
            st = time.time()
            self.log("Loading econlogger data to ram.")
        self.fetching = True
        today = datetime.now(timezone.utc).date()
        needToSave = False
        while self.current_date <= today:
            date_string = f"{self.current_date.year}_{self.current_date.month}_{self.current_date.day}"
            path = self.DATABASE_PATH + f"/{date_string}.strawblog"
            # if not os.path.exists(path):
            #     strawblog = _compress_log(date_string, path, self.log)
            # else:
            #     with open(path, 'rb') as f:
            #         strawblog = lz4.decompress(f.read())
            # self.data.append(strawblog)

            if self.current_date > self.shipnamescurrentdate:
                self._get_ship_names(date_string)
                needToSave = True

            self.current_date += timedelta(days=1)
        if needToSave:
            with open(self.DATABASE_PATH + "/shipnames.strawblogs", "wb") as w:
                w.write(lz4.compress(msgpack.dumps(self.shipnames)))
        if not self.loaded:
            self.log(f"Loaded trans log data to ram in {round(time.time() - st, 2)} seconds!")
            self.loaded = True
        self.fetching = False
    
    def find_dst_by_hex(self, hex_code):
        title = "DST Search of {" + hex_code + "}" 
        hex_code = hex_code.strip("{} ")
        print(f"Finding logs with destination {hex_code}")
        res = self._find_by_index(_compress_hex(hex_code), 18)
        if len(res) == 0:
            return title, "Failed to find any results.", False
        transfers = {}
        for log in res:
            w = networth.getworth(self.schema[log["item"]]) * log["count"]
            if log["src"] in transfers:
                transfers[log["src"]] += w
            else:
                transfers[log["src"]] = w
        transfers = sorted(transfers.items(), key=lambda item: item[1], reverse=True)
        transfers = transfers[:10] if len(transfers) > 10 else transfers
        basic_desc = f"Results: `{len(res)}` results\n\n====================\n**Top ten most transfered:**\n====================\n"
        for transfer in transfers:
            if transfer[0] not in SOURCE_MAP:
                basic_desc += f"**{self.shipnames[transfer[0]][-1][0]}** " + "`{" + transfer[0] + "}`"+ f": {round(transfer[1])} flux\n"
            else:
                basic_desc += f"**{transfer[0]}:** {round(transfer[1])} flux\n"
        raw = self.create_detailed_logs(res)
        return title, basic_desc, raw
    
    def find_src_by_hex(self, hex_code):
        title = "SRC Search of {" + hex_code + "}" 
        hex_code = hex_code.strip("{} ")
        res =  self._find_by_index(_compress_hex(hex_code), 12)
        if len(res) == 0:
            return title, "Failed to find any results.", False
        transfers = {}
        for log in res:
            w = networth.getworth(self.schema[log["item"]]) * log["count"]
            if log["dst"] in transfers:
                transfers[log["dst"]] += w
            else:
                transfers[log["dst"]] = w
        transfers = sorted(transfers.items(), key=lambda item: item[1], reverse=True)
        transfers = transfers[:10] if len(transfers) > 10 else transfers
        basic_desc = f"Results: `{len(res)}` results\n\n====================\n**Top ten most transfered:**\n====================\n"
        for transfer in transfers:
            if transfer[0] != "killed":
                basic_desc += f"**{self.shipnames[transfer[0]][-1][0]}** " + "`{" + transfer[0] + "}`"+ f": {round(transfer[1])} flux\n"
            else:
                basic_desc += f"**Killed:** {round(transfer[1])} flux\n"
        raw = self.create_detailed_logs(res)
        return title, basic_desc, raw
      
    def _find_by_index(self, searcher, offsetIndex, past=0):
        occurrences = []
        r = range(0, len(self.data)) if past == 0 else range(len(self.data)-past, len(self.data))
        for i in r:
            log = self.data[i]
            index = log.find(searcher)
            while index != -1:
                o = index - offsetIndex
                if o % 24 == 0:
                    occurrences.append(_decode_entry(log[o:o+24]))
                index = log.find(searcher, index + 24)
        return occurrences
    
    def create_detailed_logs(self, data):
        raw_log = "Detailed Logs:\nserver dd/mm/yyyy hh:mm UTC zone, src -> dst, of count item\n\n"
        for log in data:
            t = datetime.fromtimestamp(log["time"], timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
            if log['src'] not in SOURCE_MAP:
                src = self.shipnames[log['src']][-1][0] + " {" + log['src'] + "}"
            else:
                src = log["src"]
            
            if log["dst"] != "killed":
                dst = self.shipnames[log['dst']][-1][0] + " {" + log['dst'] + "}"
            else:
                dst = "killed"
            l = f"{SERVER_TO_NAME[log['serv']]} {t} {log['zone']} {src} -> {dst} of {log['count']} {self.schema[log['item']]['name']}"
            raw_log += l + "\n"
        return raw_log

if __name__ == "__main__":

    cmd = sys.argv[1]
    try:
        arg = open("./argument.txt").read();
    except:
        arg = ""
    try:
        currentShips = json.load(open("./savedata/ships.json"))
    except:
        currentShips = {"dates": "", "ships": {}}
    fetchShips(open('output.txt','w').write)
    dbgLog = open('output.txt', 'w').write
    sorted_items = sorted(currentShips["ships"].items(), key=lambda item: item[1]['w'], reverse=True)
    LEADERBOARD_HEX = [item[0] for item in sorted_items]
    dbgLog("COMMAND="+cmd+"\n")
    if (cmd == 'ValueTotal'):
        data = calculateNetworthShiplist(json.load(open('test.json', encoding="utf-8")))
        output = {"value": data[1], "date": data[0], "shipData":[]};# f"N={data[1]} \nD={data[0]}\n"
        for ship in data[2]:
           output["shipData"].append(ship);
        print(json.dumps(output))
    elif (cmd == 'NameSearch'):
        data = text_findshipbyname(arg)
        print(data)
    elif (cmd == 'leaderboard'):
        print(json.dumps(getLeaderboardNetworth(arg)));
    elif (cmd == 'byHex'):
        print(json.dumps(safeGetEntree(arg)));
    elif (cmd == 'pastNames'):
        ECONOMY_MANAGER = Econlogger(log)
        ECONOMY_MANAGER.fetch();
        hex_code = "CA27D4"
        if hex_code in ECONOMY_MANAGER.shipnames:
            names = ECONOMY_MANAGER.shipnames[hex_code]
            s = ""
            for name in names:
                s += f"**{name[2]}**: `{name[0]}` (Color: #{str(hex(name[1])).replace('0x', '').upper().zfill(6)})\n"
            print(s)
        else:
            print("cannot find")
        
    
    

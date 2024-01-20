import json
import datetime
from datetime import datetime
from datetime import timedelta
import os
from tabulate import tabulate

print("Reading user data...")
user_self = json.loads(open("account/user.json", "r").read())

# load servers
print("Reading server data...")
server_index = json.loads(open("servers/index.json", "r").readline())
dm_index = {}

# load dms
print("Reading message data...")
messages_dir = os.listdir("messages")
for m in messages_dir:
    if ".json" in m:
        continue

    channel = json.loads(open(f"messages/{m}/channel.json", "r").read())

    if channel["type"] != 1:
        continue

    user_id_notself = channel["recipients"][0]
    if channel["recipients"][0] == user_self["id"]:
        user_id_notself = channel["recipients"][1]

    user_name_notself = "Unknown user"

    for r in user_self["relationships"]:
        if r["id"] == user_id_notself:
            user_name_notself = f'{r["user"]["global_name"]} ({r["user"]["username"]})'
            break

    dm_index[channel["id"]] = user_name_notself

# read data
data = open("activity/reporting/events-2023-00000-of-00001.json", encoding="utf8")

print("Reading activity data...")
lines = data.readlines()

events = []

for line in lines:
    line_json = json.loads(line)

    ts = line_json["timestamp"].split(".")[0].replace("Z", "").replace('"', '')
    timestamp = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')

    pre_2022 = timestamp < datetime(2022,1,1)

    if not pre_2022:
        if line_json["event_type"] != "join_voice_channel" and line_json["event_type"] != "leave_voice_channel":
            continue
    else:
        if line_json["event_type"] != "start_listening":
            continue

    guild = -1

    if "guild_id" in line_json:
        guild = line_json["guild_id"]
    elif "server" in line_json:
        guild = line_json["server"]

    channel = -1
    if "channel_id" in line_json:
        channel = line_json["channel_id"]
    elif "channel" in line_json:
        channel = line_json["channel"]

    event = {
        "event_type": line_json["event_type"],
        "timestamp": timestamp,
        "guild_id": guild,
        "channel_id": channel,
        "legacy": pre_2022
    }

    events.append(event)

events = sorted(events, key=lambda d: d['timestamp'])

# calculate time in voice
total_time_in_voice = timedelta(0)

time_in_voice_per_guild = {}
time_in_voice_per_user = {}

in_voice_channel = False
voice_join_time = datetime(2021,10,11)

print("Calculating time in voice chat...")

# post-2021 voice chat events
for e in events:

    if e["legacy"]:
        continue

    timestamp = e["timestamp"]

    if e["event_type"] == "join_voice_channel":
        in_voice_channel = True
        voice_join_time = timestamp
    
    if e["event_type"] == "leave_voice_channel" and in_voice_channel:
        in_voice_channel = False
        time_in_voice : timedelta = timestamp - voice_join_time
        total_time_in_voice += time_in_voice

        if e["guild_id"] == -1:
            if e["channel_id"] in time_in_voice_per_user:
                time_in_voice_per_user[e["channel_id"]] += time_in_voice
            else:
                time_in_voice_per_user[e["channel_id"]] = time_in_voice
        else:
            if e["guild_id"] in time_in_voice_per_guild:
                time_in_voice_per_guild[e["guild_id"]] += time_in_voice
            else:
                time_in_voice_per_guild[e["guild_id"]] = time_in_voice


last_voice_listen = datetime(2016,1,1)
first_check = True

# pre-2022 voice chat events
for e in events:

    if not e["legacy"]:
        continue
    
    if first_check:
        last_voice_listen = e["timestamp"]
        last_voice_join = e["timestamp"]
        first_check = False
        continue

    time_since_last_listen : timedelta = e["timestamp"] - last_voice_listen

    if time_since_last_listen.seconds < 1000:
        total_time_in_voice += time_since_last_listen

        if e["guild_id"] == -1:
            if e["channel_id"] in time_in_voice_per_user:
                time_in_voice_per_user[e["channel_id"]] += time_since_last_listen
            else:
                time_in_voice_per_user[e["channel_id"]] = time_since_last_listen
        else:
            if e["guild_id"] in time_in_voice_per_guild:
                time_in_voice_per_guild[e["guild_id"]] += time_since_last_listen
            else:
                time_in_voice_per_guild[e["guild_id"]] = time_since_last_listen
    
    last_voice_listen = e["timestamp"]

# sort results
time_in_voice_per_guild = dict(sorted(time_in_voice_per_guild.items(), key=lambda x: x[1], reverse=True))
time_in_voice_per_user = dict(sorted(time_in_voice_per_user.items(), key=lambda x: x[1], reverse=True))

# print results
final_voice_per_context = []

final_voice_per_context.append(["Total", "Total time in voice chat", total_time_in_voice])

for guild in time_in_voice_per_guild:
    server_name = "Unknown server"

    if guild in server_index:
        server_name = server_index[guild]

    final_voice_per_context.append(["Server", server_name, time_in_voice_per_guild[guild]])

for user in time_in_voice_per_user:
    if user not in dm_index:
        continue

    final_voice_per_context.append(["DM", dm_index[user], time_in_voice_per_user[user]])

output = f"DISCORD VOICE CALL STATISTICS FOR @{user_self['username']}\n\n"
output += tabulate(final_voice_per_context, headers=["Context", "Name", "Time"], tablefmt='fancy_grid')
open("output.txt", "w+", encoding="utf-8").write(output)

print("Done! The results are in output.txt!")
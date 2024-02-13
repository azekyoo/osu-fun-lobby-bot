import socket
import osu_irc
import random
import requests
from datetime import datetime, timedelta

#############################################################################################

TARGET_CHANNEL = '#mp_XXXXXXX'

api_key = "YOUR_OSU_API"

NICK = 'YOUR_OSU_USERNAME'

OAUTH_TOKEN = 'YOUR iirc.ppy.sh KEY'

#############################################################################################



##### MAP #################################

start_date = "2016-01-01"
end_date = datetime.today().strftime("%Y-%m-%d")

def generate_random_date(start_date, end_date):
    # Convert start_date and end_date strings to datetime objects
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    # Calculate the range of days between start_date and end_date
    delta_days = (end_datetime - start_datetime).days

    # Generate a random number of days within the range
    random_days = random.randint(0, delta_days)

    # Add the random number of days to start_date to get the random date
    random_date = start_datetime + timedelta(days=random_days)

    # Format the random date as a string in "YYYY-MM-DD" format
    formatted_random_date = random_date.strftime("%Y-%m-%d")

    return formatted_random_date



def get_random_standard_beatmap_url(api_key):
    random_date = generate_random_date(start_date, end_date)
    # Make a request to the osu! API to get a list of beatmaps in standard mode
    api_url = f"https://osu.ppy.sh/api/get_beatmaps?since={random_date} 00:00:00&k={api_key}&m=0"  # '0' corresponds to the osu! standard mode
    response = requests.get(api_url)
    
    try:
        response.raise_for_status()  # Check for errors in the HTTP response
        data = response.json()

        # Check if the API request was successful
        if data and "error" not in data:
            filtered_beatmaps = [beatmap for beatmap in data if int(beatmap.get("total_length")) < 120]
            if len(filtered_beatmaps)==0: 
                return get_random_standard_beatmap_url(api_key)
            # Select a random beatmap from the list
            random_beatmap = random.choice(filtered_beatmaps)

            # Extract beatmap ID and set ID
            beatmap_id = random_beatmap["beatmap_id"]
            set_id = random_beatmap["beatmapset_id"]

            # Construct the beatmap URL
            beatmap_url = f"https://osu.ppy.sh/beatmapsets/{set_id}#osu/{beatmap_id}"
            
            max_combo = int(random_beatmap["max_combo"])
            
            return [beatmap_url, max_combo, beatmap_id]
        else:
            print(f"Error: {data.get('error')}")
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    
##### GAMES ############################

acc = [50, 60, 70, 75, 80, 85, 90, 95]

combo_type = ['max combo', 'ending combo']

score = [100, 200, 300, 400, 500]

mods = ["+EZ", "+HD", "+HR", "+HDHR", "+FL", "+EZHD", "+EZFL"]
modsMSG = ["ez", "hd", "hr", "hd hr", "fl", "ez hd", "ez fl"]

other = ['CTB lowest score', 'Highest 50s count', 'Highest 100s count']

##### REQUIREMENTS ###################

def osu():
    result = get_random_standard_beatmap_url(api_key)
    
    map = result[0]
    
    max_combo = result[1]
        
    combo = random.randint(round(max_combo/10), round(max_combo/2))
    
    miss = random.randint(round(max_combo/10), round(max_combo/3))
    
    req = [acc, combo, score, other]

    mod = random.choice(mods) if random.random() < 0.7 else "+NM"

    if mod == "+NM":
        modMSG = "nm"
    else:
        modMSG = modsMSG[mods.index(mod)]
    
    game = random.choice(req)
    
    
    if game == acc:
        game =  f'Closest acc to {random.choice(acc)}% wins'

    elif game == combo:
        game = f'Closest {random.choice(combo_type)} to {combo} wins'
    
    elif game == miss:
        game = f'Closest misscount to {miss} wins'

    elif game == score:
        game = f'Closest score to {random.choice(score)}k wins'

    elif game == other:
        game = f'{random.choice(other)} wins'

    #print("")
    #start = f'{map}\n**{mod}**\n{game}'
    #print(start)
    #pyperclip.copy(start)
    #print("")
    return [map, mod, game, result[2], modMSG]

#############################################################################################

def send(texte):
    # Connect to osu! IRC server
    server = 'irc.ppy.sh'
    port = 6667
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((server, port))

    # Log in with osu! username and oauth token
    irc.send(bytes(f'PASS {OAUTH_TOKEN}\r\n', 'UTF-8'))
    irc.send(bytes(f'NICK {NICK}\r\n', 'UTF-8'))

    # Join the target channel

    irc.send(bytes(f'JOIN {TARGET_CHANNEL}\r\n', 'UTF-8'))
    irc.send(bytes(f'PRIVMSG {TARGET_CHANNEL} :{texte}\r\n', 'UTF-8'))

    # Close the connection
    irc.close()

class MyBot(osu_irc.Client):

  async def onReady(self):
    await self.joinChannel(TARGET_CHANNEL)

  async def onMessage(self, message):
    msg = str(message)
    if msg in ["!game","!g"]:
        game = osu()
        send(f'!mp map {game[3]}')
        send(f'!mp mods {game[4]}')
        send("WINNING CONDITION:")
        send(game[2])
    
x = MyBot(token=OAUTH_TOKEN, nickname=NICK)
x.run()
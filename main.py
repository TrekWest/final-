import discord
from discord import ui
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import time
import random
import webserver

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
score = [0,0,0]
balance = [10,10,10]
claimedcouncils = {}
lockedcouncils = []
GUILD_ID = discord.Object(id=1389514810865225879)
failed_challenge_cooldowns = {}
active_challenge_cooldowns = set()
COOLDOWN_SECONDS = 600

entire_list = [[],[],[]]
items = [[],[],[]]

@bot.event
async def on_ready():
    if not hasattr(bot, "synced"):
        await bot.tree.sync()
        bot.synced = True
        print("Logged in as {}".format(bot.user.name))

countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
    "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia",
    "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo (Congo-Brazzaville)", "Costa Rica",
    "Croatia", "Cuba", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador",
    "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
    "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland",
    "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait",
    "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
    "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico",
    "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru",
    "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway", "Oman",
    "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
    "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia",
    "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa",
    "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan",
    "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
    "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela",
    "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

STATIONS = [["Berowra","Mount Kuring-gai", "Mount Colah", "Asquith", "Hornsby", "Waitara", "Wahroonga", "Warrawee", "Turramurra", "Pymble", "Gordon", "Killara", "Lindfield", "Roseville", "Chatswood", "Artarmon", "St Leonards", "Wollstonecraft", "Waverton", "North Sydney", "Milsons Point", "Wynyard", "Town Hall", "Central", "Redfern", "Strathfield", "Lidcombe", "Auburn", "Clyde", "Granville", "Harris Park", "Parramatta", "Westmead", "Wentworthville", "Pendle Hill", "Toongabbie", "Seven Hills", "Blacktown"],
            ["Central", "Museum", "St James", "Circular Quay", "Wynyard", "Town Hall", "Central", "Redfern", "Macdonaldtown", "Newtown", "Stanmore", "Petersham", "Lewisham", "Summer Hill", "Ashfield", "Croydon", "Burwood", "Strathfield", "Homebush", "Flemington", "Lidcombe", "Auburn", "Clyde", "Granville", "Merrylands", "Guildford", "Yennora", "Fairfield", "Canley Vale", "Cabramatta", "Warwick Farm", "Liverpool"],
            ["Central", "Museum", "St James", "Circular Quay", "Wynyard", "Town Hall", "Central", "Redfern", "Macdonaldtown", "Stanmore", "Petersham", "Lewisham", "Summer Hill", "Ashfield", "Croydon", "Burwood", "Strathfield", "Homebush", "Flemington", "Lidcombe", "Berala", "Regents Park", "Sefton", "Chester Hill", "Leightonfield", "Villawood", "Carramar", "Cabramatta", "Warwick Farm", "Liverpool"],
            ["Bondi Junction", "Edgecliff", "Kings Cross", "Martin Place", "Town Hall", "Central", "Redfern", "Sydenham", "Tempe", "Wolli Creek"],
            ["Blacktown", "Seven Hills", "Toongabbie", "Pendle Hill", "Wentworthville", "Westmead", "Parramatta", "Harris Park", "Merrylands", "Guildford", "Yennora", "Fairfield", "Canley Vale", "Cabramatta", "Warwick Farm", "Liverpool"],
            ["Lidcombe", "Berala", "Regents Park", "Birrong", "Yagoona", "Bankstown"],
            ["Central", "Town Hall", "Wynyard", "Circular Quay", "St James", "Museum", "Central", "Redfern", "Erskineville", "St Peters", "Sydenham"],
            ["Central", "Town Hall", "Wynyard", "Circular Quay", "St James", "Museum", "Central", "Green Square", "Mascot", "Domestic Airport", "International Airport", "Wolli Creek"],
            ["Gordon", "Killara", "Lindfield", "Roseville", "Chatswood", "Artarmon", "St Leonards", "Wollstonecraft", "Waverton", "North Sydney", "Milsons Point", "Wynyard", "Town Hall", "Central", "Redfern", "Burwood", "Strathfield", "North Strathfield", "Concord West", "Rhodes", "Meadowbank", "West Ryde", "Denistone", "Eastwood", "Epping", "Cheltenham", "Beecroft", "Pennant Hills", "Thornleigh", "Normanhurst", "Hornsby"],
            ["Tallawong", "Rouse Hill", "Kellyville", "Bella Vista", "Norwest", "Hills Showground", "Castle Hill", "Cherrybrook", "Epping", "Macquarie University", "Macquarie Park", "North Ryde", "Crows Nest", "Victoria Cross", "Barangaroo", "Martin Place", "Gadigal", "Central", "Waterloo", "Sydenham"],
            ["Wynyard", "Neutral Bay Junction", "Spit Junction", "Manly Vale", "Warringah Mall", "Dee Why", "Collaroy", "Narrabeen", "Warriewood", "Mona Vale"]]
LINES = {"T1": 0, "T2": 1, "T3": 2, "T4": 3, "T5": 4, "T6": 5, "T8 South": 6, "T8 Airport": 7, "T9": 8, "Metro": 9}

coin_challenges = [
    ["Choose a starting position and attempt to walk 1 kilometre without consulting Google Maps. Once you think you’ve walked 1 kilometre, check with Google Maps. If you are within 20% of 1km, you get the coins", 3],
    ["Capture a video of a bird for 30 seconds without the bird leaving the screen, submit video evidence", 3],
    ["Find a building that is at least 100 years old and take a picture", 3],
    ["Take a picture of a building in a different suburb and correctly guess what suburb it’s in", 3],
    ["Transfer water from one body of water (they have to be named differently on Google Maps and bubblers do not count) to another (and that water can’t be your drinking water), take a picture of the first and second body of water, including the names of both bodies of water", 5],
    ["Immediately claim the coins, but the next time you want to board a train, the direction you go from the station has to be determined by a random number generator. You only need to ride one stop on a train for the direction to have been travelled", 3],
    ["Claim coins immediately, but for the next 30 minutes, you cannot use your phone to do research (unless a challenge requires you to confirm something)", 3],
    ["Photograph 5 different species of animals (humans do not count)", 3],
    ["Take a picture of the flag of a country that is not Australia and correctly identify it without the use of resources apart from your brains", 5],
    ["Take a picture of a license plate from a different state", 3],
    ["Become a chess knight for 15 minutes. This means for every two steps forward you take, you must take one step to the side", 3],
    ["Scrunch up a piece of paper and throw it into a bin from 4 metres away (3 official attempts, but you can practice beforehand), submit video evidence", 3],
    ["Take a picture of three shops with neon signage ", 3],
    [f"Find the square root of {random.randint(10000,99999)} to the nearest whole number without the aid of a calculator within five minutes. Once this challenge is pulled, you have five minutes to find a suitable starting location before starting the timer.", 3],
    ["Solve a rubik’s cube. However, you and your partner must take turns making one move each. ie. once a member of the team makes a move, the other must make the next move. You may not mention specific pieces or how to move a piece, but you can discuss strategies. eg: 'I don't know this OLL', 'do a J perm'", 5],
    ["One team member will choose someone from their teammate’s contacts list to call. If they pick up, the challenge has been completed. If not, then it’s a fail", 3],
    ["One team member chooses a random country, the other must guess this country correctly in under 10 guesses", 3]
]

team_1_coin_challenges = [
    ["Choose a starting position and attempt to walk 1 kilometre without consulting Google Maps. Once you think you’ve walked 1 kilometre, check with Google Maps. If you are within 20% of 1km, you get the coins", 3],
    ["Capture a video of a bird for 30 seconds without the bird leaving the screen, submit video evidence", 3],
    ["Find a building that is at least 100 years old and take a picture", 3],
    ["Take a picture of a building in a different suburb and correctly guess what suburb it’s in", 3],
    ["Transfer water from one body of water (they have to be named differently on Google Maps and bubblers do not count) to another (and that water can’t be your drinking water), take a picture of the first and second body of water, including the names of both bodies of water", 5],
    ["Immediately claim the coins, but the next time you want to board a train, the direction you go from the station has to be determined by a random number generator. You only need to ride one stop on a train for the direction to have been travelled", 3],
    ["Claim coins immediately, but for the next 30 minutes, you cannot use your phone to do research (unless a challenge requires you to confirm something)", 3],
    ["Photograph 5 different species of animals (humans do not count)", 3],
    ["Take a picture of the flag of a country that is not Australia and correctly identify it without the use of resources apart from your brains", 5],
    ["Take a picture of a license plate from a different state", 3],
    ["Become a chess knight for 15 minutes. This means for every two steps forward you take, you must take one step to the side", 3],
    ["Scrunch up a piece of paper and throw it into a bin from 4 metres away (3 official attempts, but you can practice beforehand), submit video evidence", 3],
    ["Take a picture of three shops with neon signage ", 3],
    [f"Find the square root of {random.randint(10000,99999)} to the nearest whole number without the aid of a calculator within five minutes. Once this challenge is pulled, you have five minutes to find a suitable starting location before starting the timer.", 3],
    ["Solve a rubik’s cube. However, you and your partner must take turns making one move each. ie. once a member of the team makes a move, the other must make the next move. You may not mention specific pieces or how to move a piece, but you can discuss strategies. eg: 'I don't know this OLL', 'do a J perm'", 5],
    ["One team member will choose someone from their teammate’s contacts list to call. If they pick up, the challenge has been completed. If not, then it’s a fail", 3],
    ["One team member chooses a random country, the other must guess this country correctly in under 10 guesses", 3]
]

team_2_coin_challenges = [
    ["Choose a starting position and attempt to walk 1 kilometre without consulting Google Maps. Once you think you’ve walked 1 kilometre, check with Google Maps. If you are within 20% of 1km, you get the coins", 3],
    ["Capture a video of a bird for 30 seconds without the bird leaving the screen, submit video evidence", 3],
    ["Find a building that is at least 100 years old and take a picture", 3],
    ["Take a picture of a building in a different suburb and correctly guess what suburb it’s in", 3],
    ["Transfer water from one body of water (they have to be named differently on Google Maps and bubblers do not count) to another (and that water can’t be your drinking water), take a picture of the first and second body of water, including the names of both bodies of water", 5],
    ["Immediately claim the coins, but the next time you want to board a train, the direction you go from the station has to be determined by a random number generator. You only need to ride one stop on a train for the direction to have been travelled", 3],
    ["Claim coins immediately, but for the next 30 minutes, you cannot use your phone to do research (unless a challenge requires you to confirm something)", 3],
    ["Photograph 5 different species of animals (humans do not count)", 3],
    ["Take a picture of the flag of a country that is not Australia and correctly identify it without the use of resources apart from your brains", 5],
    ["Take a picture of a license plate from a different state", 3],
    ["Become a chess knight for 15 minutes. This means for every two steps forward you take, you must take one step to the side", 3],
    ["Scrunch up a piece of paper and throw it into a bin from 4 metres away (3 official attempts, but you can practice beforehand), submit video evidence", 3],
    ["Take a picture of three shops with neon signage ", 3],
    [f"Find the square root of {random.randint(10000,99999)} to the nearest whole number without the aid of a calculator within five minutes. Once this challenge is pulled, you have five minutes to find a suitable starting location before starting the timer.", 3],
    ["Solve a rubik’s cube. However, you and your partner must take turns making one move each. ie. once a member of the team makes a move, the other must make the next move. You may not mention specific pieces or how to move a piece, but you can discuss strategies. eg: 'I don't know this OLL', 'do a J perm'", 5],
    ["One team member will choose someone from their teammate’s contacts list to call. If they pick up, the challenge has been completed. If not, then it’s a fail", 3],
    ["One team member chooses a random country, the other must guess this country correctly in under 10 guesses", 3]
]

team_3_coin_challenges = [
    ["Choose a starting position and attempt to walk 1 kilometre without consulting Google Maps. Once you think you’ve walked 1 kilometre, check with Google Maps. If you are within 20% of 1km, you get the coins", 3],
    ["Capture a video of a bird for 30 seconds without the bird leaving the screen, submit video evidence", 3],
    ["Find a building that is at least 100 years old and take a picture", 3],
    ["Take a picture of a building in a different suburb and correctly guess what suburb it’s in", 3],
    ["Transfer water from one body of water (they have to be named differently on Google Maps and bubblers do not count) to another (and that water can’t be your drinking water), take a picture of the first and second body of water, including the names of both bodies of water", 5],
    ["Immediately claim the coins, but the next time you want to board a train, the direction you go from the station has to be determined by a random number generator. You only need to ride one stop on a train for the direction to have been travelled", 3],
    ["Claim coins immediately, but for the next 30 minutes, you cannot use your phone to do research (unless a challenge requires you to confirm something)", 3],
    ["Photograph 5 different species of animals (humans do not count)", 3],
    ["Take a picture of the flag of a country that is not Australia and correctly identify it without the use of resources apart from your brains", 5],
    ["Take a picture of a license plate from a different state", 3],
    ["Become a chess knight for 15 minutes. This means for every two steps forward you take, you must take one step to the side", 3],
    ["Scrunch up a piece of paper and throw it into a bin from 4 metres away (3 official attempts, but you can practice beforehand), submit video evidence", 3],
    ["Take a picture of five shops with neon signage ", 3],
    [f"Find the square root of {random.randint(10000,99999)} to the nearest whole number without the aid of a calculator within five minutes. Once this challenge is pulled, you have five minutes to find a suitable starting location before starting the timer.", 3],
    ["Solve a rubik’s cube. However, you and your partner must take turns making one move each. ie. once a member of the team makes a move, the other must make the next move. You may not mention specific pieces or how to move a piece, but you can discuss strategies. eg: 'I don't know this OLL', 'do a J perm'", 5],
    ["One team member will choose someone from their teammate’s contacts list to call. If they pick up, the challenge has been completed. If not, then it’s a fail", 3],
    ["One team member chooses a random country, the other must guess this country correctly in under 10 guesses", 3]
]

councilchallenges = {
    "Hornsby Shire": "Find and photograph the 10 items listed below from Kmart. **The distance between your camera and the item must be less than 1 metre when the picture is taken.** **You have 30 minutes, and your time starts after you finish reading this message.** Here are the items:",
    "The Hills Shire": "Go to the bus stop in Castle Hill (two of them exist so you can pick one) and go on the first non-express bus that shows up and take it to the first stop. Then, find your way back to the station **without the help from anyone except for your teammate**.",
    "City of Parramatta": "Beat today’s Wordle. To use any letters, you must first find a shop with its name starting with the letter you want to use. This is a one-time thing; you must repeat this process if you want to use the same letter again. Eg T for target.",
    "Ku-Ring-Gai": "Run one lap of the cross country course at TPS (Justin remembers), must walk from Turramurra Station to TPS. If the school is closed, just walk back to the station. The route: https://docs.google.com/document/d/1RgcG9WUIvVpRgtX4-CVQCN3bA_JsUxPKIoZBPZ2mva0/edit?tab=t.0",
    "Northern Beaches": "Visit three beaches and **take a selfie of both group members** with the welcome sign and **submit it in the discord server.**",
    "City of Blacktown": "Visit “The Leo Kelly Blacktown Arts Centre”(free entry) and recreate one of the artworks there. **Submit this in the discord server**",
    "Cumberland": "Identify 10 different types of plants correctly in Holroyd Gardens (google allowed but not google image search), **an image of each plant must be submitted. Start a 30 minute timer once you arrive at Holroyd Gardens.**",
    "City of Fairfield": "Locate 10 different languages on shop fronts. You must then identify all ten languages correctly. Identifying a language incorrectly fails the challenge automatically. A photo of each shop front must be submitted with your guess. **You can only check if you’re correct after submitting the photo and your guess to the discord server**",
    "Canterbury-Bankstown": "Find 10 Vietnamese restaurants in **30 minutes, submitting an image of each shop front on discord**. You must start the timer as soon as you finish reading this.",
    "Strathfield": "Challenge a stranger to a chess game on the large chessboard in Strathfield Square and win.If the chess board is not there or you are unable to locate an opponent, you have to beat the chess.com bot whose elo is closest to the rapid elo of your highest-rated chess player. **Submit an image of the final position to discord once the challenge has been completed. You have two attempts(applies to both challenges).**",
    "Inner West": "Visit all 5 Ovals labelled on the map of Sydney University and throw/kick a ball through the goalposts at each of the 5 ovals in Sydney University from a distance of at least 25m. If an oval is inaccessible or occupied, you must successfully pass a ball to your partner 10 times in a row from a distance of at least 10 metres. (Each team member completes 5 passes) **A video recording of you throwing/kicking the ball through each goalpost is required.**",
    "City of Sydney": "Walk from Circular Quay train station to Central train station. No proof is required.",
    "Bayside Council": "Film five planes taking off and identify each airline correctly. The full takeoff does not need to be filmed. Filming a plane that has just taken off is also fine. Identifying the airline incorrectly leads to the challenge being failed automatically. **All five videos need to be submitted to Discord.**",
    "Waverley": "Using realestate.com, find a property in Waverly that has sold for more than the median house price ($3.1M) in the last six months in 45 minutes. **Take a selfie with both group members in front of the house. If the houseowner if visible, you can skip this step as it would be awkward.**",
    "Willoughby": "Find a book in Chatswood Library first published in a specific(random year from 1900-2000) year in 20 minutes. **Submit an image of the cover of this book to discord.**",
    "City of Ryde": "Locate 5 exits in Macquarie Shopping Centre. Exits that lead to the parking lot count as well. **Submit a selfie with both group members and the exit.**"
}

line_choices = [
    app_commands.Choice(name="T1", value=0),
    app_commands.Choice(name="T2", value=1),
    app_commands.Choice(name="T3", value=2),
    app_commands.Choice(name="T4", value=3),
    app_commands.Choice(name="T5", value=4),
    app_commands.Choice(name="T6", value=5),
    app_commands.Choice(name="T8 South", value=6),
    app_commands.Choice(name="T8 Airport", value=7),
    app_commands.Choice(name="T9", value=8),
    app_commands.Choice(name="Metro", value=9),
    app_commands.Choice(name="B-Line", value=10)
]


COUNCIL_CHOICES = [
    app_commands.Choice(name="Hornsby Shire", value="Hornsby Shire"),
    app_commands.Choice(name="The Hills Shire", value="The Hills Shire"),
    app_commands.Choice(name="City of Parramatta", value="City of Parramatta"),
    app_commands.Choice(name="Ku-Ring-Gai", value="Ku-Ring-Gai"),
    app_commands.Choice(name="Northern Beaches", value="Northern Beaches"),
    app_commands.Choice(name="City of Blacktown", value="City of Blacktown"),
    app_commands.Choice(name="Cumberland", value="Cumberland"),
    app_commands.Choice(name="City of Fairfield", value="City of Fairfield"),
    app_commands.Choice(name="Canterbury-Bankstown", value="Canterbury-Bankstown"),
    app_commands.Choice(name="Strathfield", value="Strathfield"),
    app_commands.Choice(name="Inner West", value="Inner West"),
    app_commands.Choice(name="City of Sydney", value="City of Sydney"),
    app_commands.Choice(name="Bayside Council", value="Bayside Council"),
    app_commands.Choice(name="Waverley", value="Waverley"),
    app_commands.Choice(name="Willoughby", value="Willoughby"),
    app_commands.Choice(name="City of Ryde", value="City of Ryde"),
]

@bot.tree.command(name="checkbalance", description="Check each team's balance", guild=GUILD_ID)
async def checkbalance(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Balance",
        color=discord.Color.blue()
    )
    embed.add_field(name="Team 1", value=str(balance[0]), inline=True)
    embed.add_field(name="Team 2", value=str(balance[1]), inline=True)
    embed.add_field(name="Team 3", value=str(balance[2]), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="checkscore", description="Check the current score", guild=GUILD_ID)
async def checkscore(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Current Scores",
        color=discord.Color.blue()
    )
    embed.add_field(name="Team 1", value=str(score[0]), inline=True)
    embed.add_field(name="Team 2", value=str(score[1]), inline=True)
    embed.add_field(name="Team 3", value=str(score[2]), inline=True)
    await interaction.response.send_message(embed=embed)

@app_commands.describe(council="Choose a council to claim")
@app_commands.choices(council=COUNCIL_CHOICES)
@bot.tree.command(name="claim", description="Claim a council", guild=GUILD_ID)
async def claim(interaction: discord.Interaction, council: app_commands.Choice[str]):
    team = None
    for i in range(3):
        if discord.utils.get(interaction.user.roles, name=f"Team {i + 1}"):
            team = i
    if team == None:
        await interaction.response.send_message(
            "You must be on a team to use this command",
            ephemeral=True
        )
        return
    if council.value in claimedcouncils:
        await interaction.response.send_message(f"**{council.value}** has already been claimed.",)
    else:
        score[team] += 1
        embed = discord.Embed(
            title="🏛️ Council Claimed!",
            description=f"**Team {team + 1}** has claimed **{council.value}**.",
            color=discord.Color.green()
        )
        embed.add_field(name="Team 1", value=str(score[0]), inline=True)
        embed.add_field(name="Team 2", value=str(score[1]), inline=True)
        embed.add_field(name="Team 3", value=str(score[2]), inline=True)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        claimedcouncils[council.value] = team
class StealChallengeView(ui.View):
    def __init__(self, interaction: discord.Interaction, council: str, team_index: int):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.council = council
        self.team_index = team_index

    @ui.button(label="Complete Challenge", style=discord.ButtonStyle.success)
    async def complete(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("You're not allowed to interact with this challenge.", ephemeral=True)
            return

        if self.council in lockedcouncils:
            await interaction.response.send_message("You cannot steal a council that has been locked")
            return

        prev_owner = claimedcouncils.get(self.council, None)
        if prev_owner is not None:
            score[prev_owner] -= 1
        claimedcouncils[self.council] = self.team_index
        score[self.team_index] += 1

        embed = discord.Embed(
            title="Council Stolen:",
            description=f"Team {self.team_index + 1} successfully stole **{self.council}**!",
            color=discord.Color.orange()
        )
        embed.add_field(name="Updated Scores", value=f"Team 1: {score[0]}\nTeam 2: {score[1]}\nTeam 3: {score[2]}")
        await interaction.response.edit_message(embed=embed, view=None)

    @ui.button(label="Failed Challenge", style=discord.ButtonStyle.danger)
    async def fail(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("You're not allowed to interact with this challenge.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Steal Failed",
            description=f"Team {self.team_index + 1} failed to steal **{self.council}**.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

@app_commands.describe(council="Choose a council to steal")
@app_commands.choices(council=COUNCIL_CHOICES)
@bot.tree.command(name="steal", description="Attempt to steal a claimed council", guild=GUILD_ID)
async def steal(interaction: discord.Interaction, council: app_commands.Choice[str]):
    member = interaction.user
    team_index = None
    for i in range(3):
        if discord.utils.get(member.roles, name=f"Team {i + 1}"):
            team_index = i
            break
    if team_index is None:
        await interaction.response.send_message("You must be on a team to use this command", ephemeral=True)
        return

    if council.value in lockedcouncils:
        await interaction.response.send_message(
            f"The council **{council.value}** is locked and cannot be stolen.",
            ephemeral=True
        )
        return

    if council.value not in claimedcouncils:
        await interaction.response.send_message(f"**{council.value}** hasn’t been claimed yet.", ephemeral=True)
        return

    if claimedcouncils[council.value] == team_index:
        await interaction.response.send_message("You already own this council.", ephemeral=True)
        return

    # Create the challenge embed
    if council.value == "Hornsby Shire":
        team_lists = [0,1,2]
        team_lists.remove(team_index)
        chosen_items = []
        for i in team_lists:
            for j in range(5):
                item = random.choice(items[i])
                chosen_items.append(item)
                items[i].remove(item)
        embed = discord.Embed(
            title="Steal Attempt",
            description=f"Team {team_index + 1} is attempting to steal {council.value}",
            color = discord.Color.dark_gold()
        )
        embed.add_field(name="Challenge", value=councilchallenges[council.value], inline=False)
        for k in chosen_items:
            embed.add_field(name=f"Item {chosen_items.index(k)+1}", value=k, inline=False)
        view = StealChallengeView(interaction, council.value, team_index)
        await interaction.response.send_message(embed=embed, view=view)
    else:
        embed = discord.Embed(
            title=f"Steal Attempt",
            description=f"Team {team_index + 1} is attempting to steal **{council.value}**!",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Challenge", value=councilchallenges[council.value], inline=False)
        view = StealChallengeView(interaction, council.value, team_index)
        await interaction.response.send_message(embed=embed, view=view)
class LockChallengeView(ui.View):
    def __init__(self, interaction: discord.Interaction, council: str, team_index: int):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.council = council
        self.team_index = team_index

    @ui.button(label="Complete Challenge", style=discord.ButtonStyle.success)
    async def complete(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message(
                "You're not allowed to interact with this challenge.", ephemeral=True)
            return

        if self.council in lockedcouncils:
            await interaction.response.send_message("You cannot lock a council that is already locked")
            return
        lockedcouncils.append(self.council)

        embed = discord.Embed(
            title="Council Locked",
            description=f"Team {self.team_index + 1} successfully locked {self.council}.",
            color=discord.Color.dark_gold()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @ui.button(label="Failed Challenge", style=discord.ButtonStyle.danger)
    async def fail(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message(
                "You're not allowed to interact with this challenge.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Lock Failed",
            description=f"Team {self.team_index + 1} failed to lock {self.council}.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)


@app_commands.describe(council="Choose a council to lock")
@app_commands.choices(council=COUNCIL_CHOICES)
@bot.tree.command(name="lock", description="Attempt to lock your claimed council", guild=GUILD_ID)
async def lock(interaction: discord.Interaction, council: app_commands.Choice[str]):
    member = interaction.user
    team_index = None

    for i in range(3):
        if discord.utils.get(member.roles, name=f"Team {i + 1}"):
            team_index = i
            break

    if team_index is None:
        await interaction.response.send_message(
            "You must be on a team to use this command", ephemeral=True)
        return

    if council.value not in claimedcouncils:
        await interaction.response.send_message(
            f"{council.value} hasn’t been claimed yet.", ephemeral=True)
        return

    if claimedcouncils[council.value] != team_index:
        await interaction.response.send_message(
            "Only the team that claimed this council can lock it.", ephemeral=True)
        return

    if council.value in lockedcouncils:
        await interaction.response.send_message(
            f"{council.value} is already locked.", ephemeral=True)
        return

    if council.value == "Hornsby Shire":
        team_lists = [0,1,2]
        team_lists.remove(team_index)
        chosen_items = []
        for i in team_lists:
            for j in range(5):
                item = random.choice(items[i])
                chosen_items.append(item)
                items[i].remove(item)
        embed = discord.Embed(
            title="Lock Attempt",
            description=f"Team {team_index + 1} is attempting to lock {council.value}",
            color = discord.Color.dark_gold()
        )
        embed.add_field(name="Challenge", value=councilchallenges[council.value], inline=False)
        for k in chosen_items:
            embed.add_field(name=f"Item {chosen_items.index(k)+1}", value=k, inline=False)
        view = LockChallengeView(interaction, council.value, team_index)
        await interaction.response.send_message(embed=embed, view=view)
    else:
        embed = discord.Embed(
            title="Lock Attempt",
            description=f"Team {team_index + 1} is attempting to lock {council.value}.",
            color=discord.Color.dark_gold()
        )
        embed.add_field(name="Challenge", value=councilchallenges[council.value], inline=False)

        view = LockChallengeView(interaction, council.value, team_index)
        await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="travel", description="Travel between stations using coins", guild=GUILD_ID)
@app_commands.describe(
    start_location="Your starting station",
    end_location="Your destination",
    line="Train line you're travelling on"
)
@app_commands.choices(line=line_choices)
async def travel(
    interaction: discord.Interaction,
    start_location: str,
    end_location: str,
    line: app_commands.Choice[int]
):
    team = None
    member = interaction.user
    for i in range(3):
        if discord.utils.get(member.roles, name=f"Team {i + 1}"):
            team = i
            break

    if team is None:
        await interaction.response.send_message("You are not part of any team!", ephemeral=True)
        return

    if start_location.lower().strip() == end_location.lower().strip():
        await interaction.response.send_message("What was the point of that?", ephemeral=True)
        return

    s1_list = []
    s2_list = []
    trainline = line.value
    for i, station in enumerate(STATIONS[trainline]):
        if station.lower().strip() == start_location.lower().strip():
            s1_list.append(i)
        if station.lower().strip() == end_location.lower().strip():
            s2_list.append(i)

    if not s1_list or not s2_list:
        await interaction.response.send_message("Invalid station(s) for the selected line.", ephemeral=True)
        return

    stops = min(abs(i - j) for i in s1_list for j in s2_list)

    if balance[team] < stops:
        embed = discord.Embed(
            title="Not enough money",
            description=f"Team {team+1} needs an extra ${stops - balance[team]}.",
            color=discord.Color.red()
        )
    else:
        balance[team] -= stops
        embed = discord.Embed(
            title="Success",
            description=f"Team {team+1} has successfully traveled from {start_location} to {end_location}. ${balance[team]} remaining.",
            color=discord.Color.green()
        )

    await interaction.response.send_message(embed=embed)
class CoinChallengeView(ui.View):
    def __init__(self, interaction: discord.Interaction, team_index: int, reward: int, challenge_name: str):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.team_index = team_index
        self.reward = reward
        self.challenge_name = challenge_name

    @ui.button(label="Complete Challenge", style=discord.ButtonStyle.success)
    async def complete(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("Only the user who started the challenge can complete it.", ephemeral=True)
            return

        balance[self.team_index] += self.reward

        # Remove challenge
        global coin_challenges
        coin_challenges = [ch for ch in coin_challenges if ch[0] != self.challenge_name]

        embed = discord.Embed(
            title="Challenge Completed!",
            description=f"Team {self.team_index + 1} earned ${self.reward}!",
            color=discord.Color.green()
        )
        embed.add_field(name="New Balance", value=f"${balance[self.team_index]}")
        active_challenge_cooldowns.remove(self.team_index)
        await interaction.response.edit_message(embed=embed, view=None)

    @ui.button(label="Fail Challenge", style=discord.ButtonStyle.danger)
    async def fail(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("Only the user who started the challenge can fail it.", ephemeral=True)
            return

        # Apply 10-minute cooldown
        failed_challenge_cooldowns[self.team_index] = time.time()
        active_challenge_cooldowns.remove(self.team_index)

        embed = discord.Embed(
            title="Challenge Failed",
            description=f"Team {self.team_index + 1} failed. You must wait 10 minutes to try again.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)


#make it so that each team can do each challenge
@bot.tree.command(name="coin_challenge", description="Complete a challenge to earn coins", guild=GUILD_ID)
async def coin_challenge(interaction: discord.Interaction):
    team_index = None
    for i in range(3):
        if discord.utils.get(interaction.user.roles, name=f"Team {i + 1}"):
            team_index = i
            break

    if team_index is None:
        await interaction.response.send_message("You must be on a team to use this command", ephemeral=True)
        return

    # Check cooldown
    last_failed = failed_challenge_cooldowns.get(team_index)
    if last_failed and time.time() - last_failed < COOLDOWN_SECONDS:
        remaining = int((COOLDOWN_SECONDS - (time.time() - last_failed)) // 60) + 1
        await interaction.response.send_message(
            f"Team {team_index + 1} must wait {remaining} more minute(s) before attempting another challenge.",
            ephemeral=True
        )
        return

    if team_index == 0:
        if not team_1_coin_challenges:
            await interaction.response.send_message("No more coin challenges left", ephemeral=True)
            return

        if team_index in active_challenge_cooldowns:
            await interaction.response.send_message("You already have an active challenge", ephemeral=True)
            return

        active_challenge_cooldowns.add(team_index)

        challenge_name, reward = random.choice(team_1_coin_challenges)

        embed = discord.Embed(
            title="Coin Challenge",
            description=f"**Challenge:** {challenge_name}\n**Reward:** ${reward}",
            color=discord.Color.gold()
        )

        view = CoinChallengeView(interaction, team_index, reward, challenge_name)
        team_1_coin_challenges.remove([challenge_name, reward])
        await interaction.response.send_message(embed=embed, view=view)
    elif team_index == 1:
        if not team_2_coin_challenges:
            await interaction.response.send_message("No more coin challenges left", ephemeral=True)
            return

        if team_index in active_challenge_cooldowns:
            await interaction.response.send_message("You already have an active challenge", ephemeral=True)
            return

        active_challenge_cooldowns.add(team_index)

        challenge_name, reward = random.choice(team_2_coin_challenges)

        embed = discord.Embed(
            title="Coin Challenge",
            description=f"**Challenge:** {challenge_name}\n**Reward:** ${reward}",
            color=discord.Color.gold()
        )

        view = CoinChallengeView(interaction, team_index, reward, challenge_name)
        team_2_coin_challenges.remove([challenge_name, reward])
        await interaction.response.send_message(embed=embed, view=view)
    elif team_index == 2:
        if not team_3_coin_challenges:
            await interaction.response.send_message("No more coin challenges left", ephemeral=True)
            return

        if team_index in active_challenge_cooldowns:
            await interaction.response.send_message("You already have an active challenge", ephemeral=True)
            return

        active_challenge_cooldowns.add(team_index)

        challenge_name, reward = random.choice(team_3_coin_challenges)

        embed = discord.Embed(
            title="Coin Challenge",
            description=f"**Challenge:** {challenge_name}\n**Reward:** ${reward}",
            color=discord.Color.gold()
        )

        view = CoinChallengeView(interaction, team_index, reward, challenge_name)
        team_3_coin_challenges.remove([challenge_name, reward])
        await interaction.response.send_message(embed=embed, view=view)

@app_commands.describe(item="Add an item")
@bot.tree.command(name="additem", description="Add an item to the list", guild=GUILD_ID)
async def additem(interaction: discord.Interaction, item: str):
    team = None
    member = interaction.user
    for i in range(3):
        if discord.utils.get(member.roles, name=f"Team {i + 1}"):
            team = i
            break

    if team is None:
        await interaction.response.send_message("You are not part of any team!", ephemeral=True)
        return

    if len(entire_list[team]) < 10:
        items[team].append(item)
        entire_list[team].append(item)
        await interaction.response.send_message(f"{item} successfully added", ephemeral=True)
    else:
        await interaction.response.send_message(f"You have reached the item limit", ephemeral=True)

@bot.tree.command(name="removelastitem", description="Remove the last item added to the list", guild=GUILD_ID)
async def removelastitem(interaction: discord.Interaction):
    team = None
    member = interaction.user
    for i in range(3):
        if discord.utils.get(member.roles, name=f"Team {i + 1}"):
            team = i
            break
    if team is None:
        await interaction.response.send_message("You are not part of any team!", ephemeral=True)
        return
    items[team].pop()
    entire_list[team].pop()
    await interaction.response.send_message(f"Item successfully removed", ephemeral=True)

@bot.tree.command(name="country", description="Generate a random country", guild=GUILD_ID)
async def country(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Country",
        description=f"{random.choice(countries)}",
        color=discord.Color.gold()
    )

    await interaction.response.send_message(embed=embed)

#admin commands
@bot.tree.command(name="listlength", description="admin command", guild=GUILD_ID)
async def listlength(interaction: discord.Interaction):
    if discord.utils.get(interaction.user.roles, name="."):
        await interaction.response.send_message(f"Team 1: {len(items[0])}, Team 2: {len(items[1])}, Team 3: {len(items[2])}")
    else:
        await interaction.response.send_message("Invalid Permissions", ephemeral=True)


@app_commands.describe(team1="team 1's new score")
@app_commands.describe(team2="team 2's new score")
@app_commands.describe(team3="team 3's new score")
@bot.tree.command(name="setscore", description="admin command", guild=GUILD_ID)
async def setscore(interaction: discord.Interaction, team1: int, team2: int, team3: int):
    if discord.utils.get(interaction.user.roles, name="."):
        global score
        score = [team1,team2,team3]
        await interaction.response.send_message(f"The score has been set to {team1}-{team2}-{team3}")
    else:
        await interaction.response.send_message("Invalid Permissions", ephemeral=True)

@app_commands.describe(pponthepp="Are you sure you want to do this?")
@bot.tree.command(name="reset", description="admin command", guild=GUILD_ID)
async def reset(interaction: discord.Interaction, pponthepp: str):
    if pponthepp != "pponthepp":
        return await interaction.response.send_message("Cancelled", ephemeral=True)
    if discord.utils.get(interaction.user.roles, name="."):
        global score
        global balance
        global claimedcouncils
        global lockedcouncils
        global failed_challenge_cooldowns
        global active_challenge_cooldowns
        global items
        global entire_list
        items = [lst.copy() for lst in entire_list]
        lockedcouncils = []
        failed_challenge_cooldowns = {}
        active_challenge_cooldowns = set()
        claimedcouncils = {}
        balance = [10,10,10]
        score = [0,0,0]
        return await interaction.response.send_message("Game has been successfully reset", ephemeral=True)
    else:
        return await interaction.response.send_message("Invalid Permissions", ephemeral=True)

webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)

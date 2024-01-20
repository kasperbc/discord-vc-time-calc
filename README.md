# Discord Voice Chat Time Calculator
A tool to see how long you have spent in Discord voice chats, including per server and user.

## Requirements
* Python 3.12.1 or later (earlier versions might work too)
* The `tabulate` package
* A Discord account with a verified email and some time spent in voice chats

## Usage

### Step 1: Download the repository
Clone or download the repository as a zip file.

### Step 2: Request and download your data package
First, [request a copy of your data on Discord](https://support.discord.com/hc/en-us/articles/360004027692). Getting your data might take a few days, but you should get an email with the data package attached once it's ready.

### Step 3: Extract the data package
Download the package and place the contents inside the same folder as the `discord-data-extract.py` file. It should be correct once the Python script is in the same folder as the "activity", "account", "messages" and the other folders.

### Step 4: Run the script
Install the required packages and run the Python script. After it's done, the results will be in a file called `output.txt`.
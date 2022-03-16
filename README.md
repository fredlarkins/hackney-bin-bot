# hackney-bin-bot
A friendly robot that'll email you what bins are being collected that week, if you live in Hackney.

## Prerequisites
✔️ You live in the London Borough of Hackney.  
✔️ You frequently forget what bins are due for collection in a given week.  
✔️ You've grown tired of using the [Waste Collection Checker tool](https://hackney-waste-pages.azurewebsites.net/) every evening before bin collection.  
✔️ You have access to a Linux installation.  
✔️ You have access to a dummy Gmail account.  

## Setup
**1) Clone the repo**
```
git clone https://github.com/fredlarkins/hackney-bin-bot.git
```

**2) Use the requirements.txt file to create a virtual environment**  
```
cd /path/to/hackney-bin-bot-repo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3) Create a dummy Gmail account**  
Create a dummy Gmail account/Google account (they're the same thing) [here](https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp). This will be the email address from which you'll receive notifications about when bins are due. Don't forget to note down the password - the script will ask you for this when you first run it (and it will be stored in a .env file).

You'll need to lower the security permissions on your Google account for this script to work. Toggle the setting for 'Allow less secure apps' (available [here](https://myaccount.google.com/lesssecureapps)) to `ON`. _Note: this feature expires on 30 May 2022 - at which point this repo becomes absolutely useless._

**4) Run the `check-bins.py` script to set everything up**  
With your venv activated, run:
```
python3 check-bins.py
```
This will run through the same flow that the [Waste Collection Checker tool](https://hackney-waste-pages.azurewebsites.net/) takes you through, via the command line. Your address details - necessary for the subsequent times that the script runs - will be saved in an `address_details.json` file, while the bin timetables will be saved in `bin-collection-data.json`. _Note: these will be overwritten every time `check-bins.py` runs._

The other nitfy thing this will do is spit out a `binbot.sh` file that you can use to schedule the bin checker to run as a Cron Job.

**5) Schedule the `binbot.sh` file as a Cron Job**  
Cron Jobs are recurring commands you can tell your computer to execute at specified intervals. In this case, I've got this running as a daily job on my Raspberry Pi. The script figures out whether your bins are due the following day, and will only email you if this is the case, telling you which bins are up for collection.

To create a cron job, run:
```
sudo crontab -e
```
...and enter the following in your crontab file:
```
30 19 * * * . /absolute/path/to/binbot.sh >/dev/null 2>&1
```
This tells cron to run the `binbot.sh` script daily at 1930. This [useful website](https://crontab.guru/) helps you write your crontab expression.

The `>/dev/null 2>&1` section of the expression simply tells the computer to discard any output from the script (in our case, print statements) to /dev/null - a black hole. This [StackExchange thread](https://unix.stackexchange.com/questions/163352/what-does-dev-null-21-mean-in-this-article-of-crontab-basics) sums it up nicely.

Finally, you can validate whether your Cron Job ran as expected with the following command:
```
grep CRON /var/log/syslog
```
Thanks again [StackExchange](https://askubuntu.com/questions/56683/where-is-the-cron-crontab-log).
# SubRedditBackgroundImages
The idea behind this is to make a program that cycles through and sets your desktop background based
 off of popular wallpapers submitted to a subreddit of your choice. This program will also try to combine
 portrait photos together to match your aspect ratio of your device so that the image is never cut off and looks awesome. 
 
 It will also gather up popular weekly images and save them into a folder to be used for a lockscreen
 slideshow if that is what is wanted.

# Important
 - This program does NOT work on anything other than Windows, since it uses Windows specific
 python libraries for setting the background image.
 - Note that the NSFW filter requires that the post be tagged appropiately with the NSFW tag
. There can be cases in which content should have been tagged, but wasn't and will result in showing
up as a possible background image.

# Setup Instructions
1. git clone https://github.com/kvosbur/SubRedditBackgroundImages.git
2. cd into the git repository
3. pip install -r requirements.txt (download needed dependencies)
4. Edit config.ini to change how program will work. This is where you will set the subreddit that is to be accessed and whether
to filter for NSFW is on or not. 
5. Create a Reddit API project. Please make sure that you choose Script from the three types of applications listed. (it lists web app, installed app, script) This can be done by going to https://www.reddit.com/prefs/apps and creating a new app (this is needed to access the images)
6. Create a .env file in the directory that is a copy of the example.env with your api secret key in the file instead of 'aaaaaaaaaaaaa'. Your api secret 
can be found where you created your Reddit API app. If you aren't seeing it then you will need to click to edit the app and then 
it will popup with the applications secret.
7. Will need to update your USER_AGENT field in your .env to follow the guidelines set in https://github.com/reddit-archive/reddit/wiki/API
for your reddit project.
8. Will need to update your CLIENT_ID field in your .env file. This value can be found just under your
Reddit API application Name on their website. (an example of what it will look like value wise is already in example.env)
9. If you want to setup your own config options copy the example_config.ini file as a base and then make 
your changes there and then change the REDD_CONFIG_PATH variable in your .env file to match the new file name(path can be relative to the repository or absolute)


# Running the Program
The program is executed by way of running the following command in terminal 

`<python installation>python.exe <git repo>/reddit_run.py`  

There are command line options that you can see by adding --help.
These include showing a progress bar for image downloads or not running the weekly locksreen photo section.

If you want to have this program run daily then make sure to set this up in task scheduler for a recurring task.

# Notice an issue?
I am not perfect if you notice something that just quite isn't right or is crashing please make
an issue on github with as much information and possibly photos of what is occurring. 

If you want support for other OS consider figuring out what changes need to be made and make a pull request to get it added 
to the current release.

If you have any suggestions on improvements other than OS support make a github issue for it and
maybe try tackling it yourself and make a pull request from it.





# SubRedditBackgroundImages
The idea behind this is to make a program that cycles through and sets your desktop background based off of popular wallpapers submitted to a subreddit of your choice.

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
5. Create a Reddit API project ( this is needed to access the images)
6. Create a .env file in the directory that is a copy of the example.env with your api secret key in the file instead of 'aaaaaaaaaaaaa'
7. Will need to update the line in reddit_api.py for USER_AGENT to follow the guidlines set in https://github.com/reddit-archive/reddit/wiki/API
for your reddit project.

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





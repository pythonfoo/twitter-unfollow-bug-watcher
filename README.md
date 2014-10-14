Note:
Inspiration and parts of the code are from orithena: https://github.com/orithena/twitter-follower-report

## INSTALLATION ##

For Python you will need twython
  pip install twython


### CONNECT WITH TWITTER ###
Those instructions are from orithena and slightly modified

* Go to https://dev.twitter.com/
* Sign in with your twitter account.
* Due high-frequent changes of the UI, you have to find "Manage My Apps" last time checked it lead here: https://apps.twitter.com/

* Click on "Create a new application" and register an application.
* When you're done with this, choose the "Settings" tab on the application's page.
* Set the "Application type" to "Read"
* Save setting by clicking "Update this Twitter application's settings"
* Go to the "Details" tab of the application
* Click "Create access token" and wait a while (some minutes or so).
* Reload the "Details" tab
* Copy and paste the access key data into the correct variables in your python file:
  * Consumer key        -> app_key
  * Consumer secret     -> app_secret
  * Access token        -> oauth_token
  * Access token secret -> oauth_token_secret
* Re-check the key's access level below the token secret.


## USE ##

Put the **start.py** in a cronjob or start it from time to time manually.  
Make sure you call it not more than every 5 minutes (Twitter does NOT like spam!)  
If you unfollow someone by intention, you can run
  start.py --mode=mark iRemoved
That will set ALL persons listed to **removed by me** and will never ever be displayed as "LOST".

## TROUBLESHOOTING ##

When you get an error like **.... DOES NOT EXIST!** rename **iFollow.sqlite**.
Maybe you need a "restart", because its indev and I messed the DB up.
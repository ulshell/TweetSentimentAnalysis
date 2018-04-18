# TweetSentimentAnalysis
A web application for analysis of tweets on twitter using Natural Language ToolKit, positive and negative words txt files to know approximate percentage of positive, negative and neutral words used. 

>This app is made to know sentiments of people which they possess in their tweets on twitter and keep analysis of them. The analysis image can be downloaded and person can see the tweets also, was it positive, negative or neutral. One can improve its sentiments by keeping up to date analysis.  

## Login Page

>For login of users into web app implementing secure login with password encryption 256-bit.

![alt login](https://github.com/ulshell/TweetSentimentAnalysis/blob/master/static/login.png)

## Register Page

>For registeration of new user into web app implementing secure login with password encryption 256-bit.

![alt register](https://github.com/ulshell/TweetSentimentAnalysis/blob/master/static/Register.png)

## User's Home Page

>Home page of user for searching different scree_names of twitter account that are not private.

![alt home](https://github.com/ulshell/TweetSentimentAnalysis/blob/master/static/Index.png)

## Tweet Analysis Page

>Page describing whole analysis of atmost 200 recent tweets (positive , negative or neutral)

![alt analysis](https://github.com/ulshell/TweetSentimentAnalysis/blob/master/static/analysis.png)

# How to run :-

>For installing all required python3 libraries

->$ pip3 install --user -r requirements.txt

>Goto your Twitter account create an app and get API_KEY and API_SECRET to run app.

-> $export API_KEY=your api key

-> $export API_SECRET=your api secret key

>Provide the FLASK_APP environment variable

-> $export FLASK_APP=application.py

>Run Flask Application

-> $python3 -m flask run

>Open http link provided in terminal. 

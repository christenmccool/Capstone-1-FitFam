# Capstone-1-FitFam 
An app to connect families along their fitness journeys.
https://mccool-fitfam.herokuapp.com/
Target demographic: Family groupings, including self-defined families, of all ages.

### Overview:  
FitFam allows family members to complete shared daily workouts posted on FitFam. Members log their workout results and respond to each other's efforts with comments. Members can view a log of previously completed workouts as well as the upcoming workout plan.
Family administrators choose the daily workout for their family either from the FitFam workout database or by creating their own workout.

### Features:
- New FitFam users either join an existing family or create a new family. Individual users are a family of one.
- The home page for a logged in user is the daily workout for their family. Users post their score for the workout and any comments about their score. 
- Family members can comment on each other's workout results.
- Results and comments can be edited and deleted by the user that created them.
- Family administrators add workouts for each day. They can either add the default FitFam workout, a workout from the FitFam database, or a workout they create themselves.
- Family members can view a log of all previously completed workouts, grouped by day.
- Family memebers can view the week's workout plan.

### API:   
The workouts in the FitFam workout database were obtained from SugarWOD API. Daily default workouts come from SugarWOD as well.
https://app.sugarwod.com/developers-api-docs  
The ZenQuotes API provides a daily quote. 
https://zenquotes.io/api/

### Technology Stack:   
This app was created using Python, Flask, SQLAlchemy, and Javascript.

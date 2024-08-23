import tkinter as tk #imports tkinter library and allows it to be reffered as tk for the game
import time #imports time library for use in the stopwatch
import sqlite3 #imports sqlite for the database
import os #imports the operating system to access images from the assets folder
import pygame #imports pygame for use in the majority of the application
import sys #imports variables and functions maintained by the system

from tkinter import Label, Scale, HORIZONTAL, PhotoImage #imports labels + scales for use in the menus
from os import listdir #imports listdir for accessing images 
from os.path import isfile,join #imports isfile and join from the os path to access images

window = tk.Tk() #creates tkinter window

flashing = False #constant used for creating a flashing block

doubleJump = False #constant used to see if user has unlocked double jump
increasedJump = False #constant used to see if user has unlocked increased jump
increasedSpeed = False #constant used to see if user has unlocked increased speed
fallingCollision = False #constant used to check collision to make block fall
doubleJumpClicked = False
increasedJumpClicked = False
increasedSpeedClicked = False #boolean variables to check if the button has been pressed
tips = True #tips set to on by default

spriteSheet = None #variable for objects sprite sheet
flashCollisions = [] #checks for flash collisions
fallingCollisions = [] #checks for falling collisions

pygame.init() #initiates pygame window
pygame.mixer.init() #allows for sound effects
WIDTH = 1000
HEIGHT = 500
FONT_SIZE = 36 #sets up constants for pygame window
FPS = 60 #caps fps to 60 for performance purposes
PLAYER_VEL = 5 #constant for player velocity
volume = 5 #variable measuring volume
leaderboardNo = 0 #holds current leaderboard screen

fontPath = join("assets", "Fonts", "Pixel Digivolve.otf") #uses join to get the location of the font
font = pygame.font.Font(fontPath, FONT_SIZE) #creates font using font size constant

stopwatchX = 850
stopwatchY = 5 #sets up constants for the location of the stopwatch

levelWindow = pygame.display.set_mode((WIDTH, HEIGHT)) #setups pygame window using constants
pygame.display.set_caption("Platforming Paradise") #sets name of pygame window
pygame.display.set_mode((1, 1), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.NOFRAME) #flags make rendering more efficient
#creates the window small and in the background as the tkinter window will be open upon running

def createWindow(usedWindow, name): #function creates tkinter window
  usedWindow.title(name) #sets name of tkinter window
  usedWindow.geometry("725x373") #size of tkinter window
  usedWindow.configure(background="#242424") #hex background colour of tkinter window

#creating sqlite backend database
def createTable(): #function creates sqlite tables
  with sqlite3.connect("AccountInfo.db") as db: #establishes connection to sqlite database
    cursor = db.cursor() #creates cursor object
    sql = """ CREATE TABLE IF NOT EXISTS
              tblAccountInfo
              (Username TEXT Primary Key,
              Password TEXT,
              CurrentLevel Integer,
              DoubleJump Integer,
              IncreasedJump Integer,
              IncreasedSpeed Integer,
              Coins Integer) """ #creates table with username as unique identifier
    cursor.execute(sql) #sql executed
    cursor = db.cursor()
    sql = """CREATE TABLE IF NOT EXISTS
             tblAccountTimes
             (Username TEXT,
              TotalTime Float,
              Level1 Float,
              Level2 Float,
              Level3 Float,
              Level4 Float,
              Level5 Float,
              FOREIGN KEY (Username) REFERENCES tblAccountInfo(Username))""" #creates table referencing account info
    cursor.execute(sql)

createTable() #calls function to create table when program is run

def addData(usernameCreds, passwordCreds): #function which adds data to the table
  length = len(passwordCreds) #finds length of inputted password
  if length < 6: 
    print("That password is too short!") #if character is less than 6 characters, it is rejected
  else:
    with sqlite3.connect("AccountInfo.db") as db:
      cursor = db.cursor()
      cursor.execute("SELECT COUNT(*) FROM tblAccountInfo WHERE Username = ?", (usernameCreds,)) #counts if the inputted username is already in the table
      count = cursor.fetchone()[0] #fetches first element in the run
      if count > 0: #if username is already in table
        print("Username already exists. Please change your username.")
      else:
        values = (usernameCreds, passwordCreds) #creates tuple of credentials
        sql = """INSERT OR IGNORE INTO tblAccountInfo
                 (Username, Password, CurrentLevel, DoubleJump, IncreasedJump, IncreasedSpeed, Coins)
                  VALUES (?, ?, 1, 0, 0, 0, 0)""" #inserts into table, other values as is new account
        cursor.execute(sql, values)
        db.commit() #updates database
        print("Credentials successfully added!")
        breakWindow() #closes window
                
def addTimeData(usernameCreds): #function adds information to time table
    with sqlite3.connect("AccountInfo.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM tblAccountTimes WHERE Username = ?", (usernameCreds,)) #counts if the inputted username is already in the table
        count = cursor.fetchone()[0] #fetches first element
        if count > 0:
            pass
        else:
            sql = """INSERT OR IGNORE INTO tblAccountTimes
                     (Username, TotalTime, Level1, Level2, Level3, Level4, Level5)
                      VALUES (?, 0, 0, 0, 0, 0, 0)"""
            values = (usernameCreds,) 
            cursor.execute(sql, values) #adds username with corresponding level times to database
            db.commit()

def loginUser(usernameCreds,passwordCreds): #function logs user into their account in database
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    userCheck = (usernameCreds,passwordCreds) #creates tuple of user info
    sql = """SELECT * FROM tblAccountInfo
             WHERE
             Username = ? AND Password = ?;""" #finds an account with corresponding username and password
    cursor.execute(sql, userCheck)
    results = cursor.fetchall() #retrieves all instances where the username and password are in database
    if len(results) == 0: #username + password combination not found in database
      print("No matching credentials - Login unsuccessful")
    else: #username and password combination found in database
      print("Login Successful")
      openLevelSelector() #calls function to open level selector

def deleteFromDatabase(usernameCreds,passwordCreds): #function to delete credentials from database
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    userValues = (usernameCreds,passwordCreds)
    sql = """SELECT * FROM tblAccountInfo
             WHERE Username = ? AND Password = ?""" #finds an account with corresponding username and password
    cursor.execute(sql,userValues)
    result = cursor.fetchall()
    if len(result) == 0: #username + password combination not found in database, cannot delete
      print("Those credentials were not found") 
    else:
      userValues = (usernameCreds,)
      sql = """DELETE FROM tblAccountInfo
               WHERE Username = ?"""
      cursor.execute(sql,userValues) #deletes information where username is equal to the inputted username
      db.commit()
      print("Account successfully deleted")
      breakWindow() #closes window

def updateData(usernameCreds,passwordCreds,newPasswordCreds): #function to update password in the database
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    userValues = (usernameCreds,passwordCreds)
    sql = """SELECT * FROM tblAccountInfo
             WHERE Username = ? AND Password = ?""" #finds an account with corresponding username and password
    cursor.execute(sql,userValues)
    result = cursor.fetchall()
    if len(result) == 0: #username + password combination not found in database, cannot update
      print("That username/password was not found.")
    else:
      if len(newPasswordCreds) < 6: #validates new password
        print("That password is too short!")
      else:  
        userValues = (newPasswordCreds, usernameCreds)
        sql = """UPDATE tblAccountInfo
                 SET Password = ?
                 WHERE Username = ?""" #sets password to updates password credentials for the user
        cursor.execute(sql, userValues)
        db.commit()
        print("Your password has been updated successfully!")

def incrementLevel(usernameCreds): #function to increment user level
    with sqlite3.connect("AccountInfo.db") as db:
        cursor = db.cursor()
        sql = """UPDATE tblAccountInfo
                 SET CurrentLevel = CurrentLevel + 1
                 WHERE Username = ?""" #increases level by one for username
        cursor.execute(sql, (usernameCreds,))
        db.commit()

def getData(level): #gets user information from database
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    if level == 0:
      sql = """SELECT t1.Username, t1.TotalTime, t2.CurrentLevel
               FROM tblAccountTimes t1
               JOIN tblAccountInfo t2 ON t1.Username = t2.Username
               WHERE t1.TotalTime > 0
               ORDER BY t1.TotalTime""" #finds total time for each player and sorts it
    elif level == 1:
      sql = """SELECT t1.Username, t1.Level1, t2.CurrentLevel
               FROM tblAccountTimes t1
               JOIN tblAccountInfo t2 ON t1.Username = t2.Username
               WHERE t1.Level1 > 0
               ORDER BY t1.Level1""" #finds level 1 time for each player and sorts it
    elif level == 2:
      sql = """SELECT t1.Username, t1.Level2, t2.CurrentLevel
               FROM tblAccountTimes t1
               JOIN tblAccountInfo t2 ON t1.Username = t2.Username
               WHERE t1.Level2 > 0
               ORDER BY t1.Level2""" #finds level 2 time for each player and sorts it
    elif level == 3:
      sql = """SELECT t1.Username, t1.Level3, t2.CurrentLevel
               FROM tblAccountTimes t1
               JOIN tblAccountInfo t2 ON t1.Username = t2.Username
               WHERE t1.Level3 > 0
               ORDER BY t1.Level3""" #finds level 3 time for each player and sorts it
    elif level == 4:
      sql = """SELECT t1.Username, t1.Level4, t2.CurrentLevel
               FROM tblAccountTimes t1
               JOIN tblAccountInfo t2 ON t1.Username = t2.Username
               WHERE t1.Level4 > 0
               ORDER BY t1.Level4""" #finds level 4 time for each player and sorts it
    else:
      sql = """SELECT t1.Username, t1.Level5, t2.CurrentLevel
               FROM tblAccountTimes t1
               JOIN tblAccountInfo t2 ON t1.Username = t2.Username
               WHERE t1.Level5 > 0
               ORDER BY t1.Level5""" #finds level 5 time for each player and sorts it
    cursor.execute(sql)
    times = cursor.fetchall()
    return times #returns all times for the players in a variable

def updatePowerup(usernameCreds, dJump, jHeight, mSpeed): #function called when user buys a powerup
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    if dJump:
      sql = """UPDATE tblAccountInfo
               SET DoubleJump = 1
               WHERE Username = ?"""
    elif jHeight:
      sql = """UPDATE tblAccountInfo
               SET IncreasedJump = 1
               WHERE Username = ?"""
    elif mSpeed:
      sql = """UPDATE tblAccountInfo
               SET IncreasedSpeed = 1
               WHERE Username = ?""" #sets powerup to 1 dependant on which powerup is called
    cursor.execute(sql, (usernameCreds,))
    db.commit()

def addCoin(usernameCreds): #function to add coins to user
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    sql = """UPDATE tblAccountInfo
             SET Coins = Coins + 1
             WHERE Username = ? AND Coins <= 15""" #increments coin amount
    cursor.execute(sql, (usernameCreds,))
    db.commit()

def removeCoins(usernameCreds, amount): #function to remove coins from user
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    sql = """UPDATE tblAccountInfo
             SET Coins = Coins - ?
             WHERE Username = ?""" #increments coin amount
    cursor.execute(sql, (amount, usernameCreds))
    db.commit()

def findCoinAmount(usernameCreds): #function to find users coin amount
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    sql = """SELECT Coins
             FROM tblAccountInfo
             WHERE Username = ?""" #finds coin amount
    cursor.execute(sql, (usernameCreds,))
    coins = cursor.fetchall()
    return coins #returns coin amount in variable

def findPowerups(usernameCreds): #function to find users powerups
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    sql = """SELECT DoubleJump, IncreasedJump, IncreasedSpeed
             FROM tblAccountInfo
             WHERE Username = ?""" #finds whether user has unlocked powerups 
    cursor.execute(sql, (usernameCreds,))
    powerups = cursor.fetchall()
    return powerups #returns powerups in tuple

def findCurrentLevel(usernameCreds): #function to find furthest level user has reached
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    sql = """SELECT CurrentLevel
             FROM tblAccountInfo
             WHERE Username = ?""" #finds what level the user has unlocked 
    cursor.execute(sql, (usernameCreds,))
    level = cursor.fetchall()
    return level #returns level in variable

def logScore(usernameCreds, previouslyCompleted): #function to log total score into database
  time = stopwatch.getTime() #finds the current time elapsed
  formattedTime = "{:.2f}".format(time) #formats to 2dp
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    if previouslyCompleted == False:
      sql = """UPDATE tblAccountTimes
               SET TotalTime = TotalTime + ?
               WHERE Username = ?""" #adds to total time
      cursor.execute(sql, (formattedTime, usernameCreds))
    else:
      oldTime = "{:.2f}".format(previouslyCompleted) #formats to 2dp
      sql = """UPDATE tblAccountTimes
               SET TotalTime = TotalTime - ?
               WHERE Username = ?""" #minuses from total time      
      cursor.execute(sql, (oldTime, usernameCreds,))
    db.commit()

def logLevelScore(usernameCreds, level): #function to log individual level scores
  time = stopwatch.getTime() #finds the current time elapsed
  formattedTime = "{:.2f}".format(time) #formats to 2dp
  levelNo = "Level" + str(level)
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    sql = """UPDATE tblAccountTimes
             SET {} = ?
             WHERE Username = ?""".format(levelNo) #sets specific level to time
    cursor.execute(sql, (formattedTime, usernameCreds))
    db.commit()

def findTimes(usernameCreds): #function to find level times from database
  with sqlite3.connect("AccountInfo.db") as db:
    cursor = db.cursor()
    sql = """SELECT Level1, Level2, Level3, Level4, Level5, TotalTime
             FROM tblAccountTimes
             WHERE Username = ?""" #finds whether user has unlocked powerups 
    cursor.execute(sql, (usernameCreds,))
    times = cursor.fetchall()
    return times #returns powerups in tuple

#Creating tkinter windows

createWindow(window, "Platforming Paradise") #creates tkinter window using createWindow function
entryText = tk.Label(window,
                     text="Platforming Paradise",
                     font=("Courier", 30, "bold"),
                     width=40,
                     fg="white",
                     bg="#202020") #creates label with text Platforming Paradise
entryText.pack() #packs tkinter label onto the screen

def breakWindow(): #function to break the window
  global currentwindow
  sfx("Click") #plays click sound effect
  if currentwindow == "Settings":
    global settingsWindow
    checkVolume()
    settingsWindow.withdraw() #destroys window
    returnButton.destroy() #destroys back button
    window.deiconify() #reopens main menu window
  if currentwindow == "Login":
    global loginWindow
    loginWindow.withdraw()
    returnButton.destroy()
    window.deiconify() #reopens main menu window
  if currentwindow == "Create Account":
    global accountWindow
    accountWindow.withdraw()
    returnButton.destroy()
    loginWindow.deiconify() #reopens login window
    currentwindow = "Login" #changes current value to the reopened login window
  if currentwindow == "Delete Account":
    global deleteWindow
    deleteWindow.withdraw()
    returnButton.destroy()
    loginWindow.deiconify() #reopens login window
    currentwindow = "Login" #changes current value to the reopened login window
  if currentwindow == "Reset Password":
    global resetWindow
    resetWindow.withdraw()
    returnButton.destroy()
    loginWindow.deiconify() #reopens login window
    currentwindow = "Login" #changes current value to the reopened login window

def sfx(name): #allows for sound effects to be played
  path = join("assets", "SFX", name + ".mp3") #finds audio file in folder
  pygame.mixer.music.load(path) #loads sound effect using path
  pygame.mixer.music.play(loops=0) #sfx does not loop
  pygame.mixer.music.set_volume(volume*0.2) #changes volume of music dependant on settings, 0.2 as 5 is default

def createBackButton(window, bWidth, bHeight, bPadx, bPady, bX, bY): #parameters to create button
  global returnButton
  returnButton = tk.Button(window,
                           text="Back",
                           font=("Courier", 30, "bold"),
                           width=bWidth,
                           height=bHeight,
                           bg="black",
                           fg="white",
                           padx=bPadx,
                           pady=bPady,
                           command=breakWindow) #creates button with parameters which breaks window when clicked
  returnButton.place(x=bX, y=bY) #places in specified x and y
                           
def backButton(): #this function creates back buttons for each window using specified parameters
  if currentwindow == "Settings":
    createBackButton(settingsWindow, 10, 1, 0, 0, 400, 265)
  if currentwindow == "Login":
    createBackButton(loginWindow, 8, 1, 5, 0, 445, 265)
  if currentwindow == "Create Account":
    createBackButton(accountWindow, 8, 2, 5, 0, 445, 225)
  if currentwindow == "Delete Account":
    createBackButton(deleteWindow, 8, 2, 5, 0, 445, 225)
  if currentwindow == "Reset Password":
    createBackButton(resetWindow, 8, 1, 5, 9, 445, 265)

def openLogin(): #this function creates the login window
  global loginWindow
  global currentwindow
  global inputUsername 
  global inputPassword #global variables for use elsewhere
  sfx("Click") #plays click sound effect
  window.withdraw() #hides main menu window
  loginWindow = tk.Toplevel(window) #creates new window associated to the main window
  createWindow(loginWindow, "Login") #uses create window function to create login window
  currentwindow = "Login" #changes current window to login
    
  loginButtons(loginWindow, "Login") #uses loginButtons function to create buttons for login windwo
  
  usernameEntry.place(x=360,y=115)
  passwordEntry.place(x=360,y=165) #places username and password entry boxes

  loginButton = tk.Button(loginWindow, #creates button for user to press after inputting username and password
                          text="Press to Log in",
                          bg="red",
                          fg="white",
                          font=("Courier", 30, "bold"),
                          height=1,
                          width=16,
                          command=showResults) #calls showResults command
  loginButton.grid(column=0, row=2, padx=10, pady=5, columnspan=4, sticky="ew") #places button in grid filling east to west
  loginButton.place(x=50,y=265) #places button in x and y locations

  usernameLabel.place(x=50,y=115)
  passwordLabel.place(x=50,y=165) #places label buttons

  createAccountButton = tk.Button(loginWindow,
                          text="Create Account", 
                          bg="black",
                          fg="white",
                          font=("Courier", 16, "bold"),
                          height=1,
                          width=14,
                          command=createAccount) #button to send user to create account window
  createAccountButton.place(x=50,y=215) #places button in x and y location

  resetPasswordButton = tk.Button(loginWindow,
                          text="Reset Password",
                          bg="black",
                          fg="white",
                          font=("Courier", 16, "bold"),
                          height=1,
                          width=14,
                          command=resetPassword) #button to send user to reset password window
  resetPasswordButton.place(x=256,y=215) #places button in x and y location

  deleteAccountButton = tk.Button(loginWindow,
                          text="Delete Account",
                          bg="black",
                          fg="white",
                          font=("Courier", 16, "bold"),
                          height=1,
                          width=14,
                          command=deleteAccount) #button to send user to delete account window
  deleteAccountButton.place(x=463,y=215) #places button in x and y location
  
  backButton() #creates back button

def loginButtons(buttonsWindow, name): #function to create buttons for the login windows
  global usernameEntry
  global passwordEntry
  global usernameLabel
  global passwordLabel
  global inputUsernameLogin 
  global inputPasswordLogin 
  global inputUsernameDelete 
  global inputPasswordDelete 
  global inputUsernameCreate
  global inputPasswordCreate 
  global inputUsernameReset 
  global inputPasswordReset #global variables for use elsewhere in the code

  usernameEntry = tk.Entry(buttonsWindow,
                           bg="white",
                           font=("Courier", 22, "bold")) #uses tk.Entry to create a box where users can enter their username
  usernameEntry.grid(column=0, row=0, padx=20, pady=20)
  usernameEntry.configure(width = 17) #allows a maximum of 17 characters to be inputted
  usernameEntry.place(x=360,y=120) #places button in window

  passwordEntry = tk.Entry(buttonsWindow,
                           bg="white",
                           font=("Courier",22, "bold"),
                           show="*") #creates entry button where the user inputs are hidden using * as the user is inputting a password
  passwordEntry.grid(column=0, row=1, padx=20, pady=20)
  passwordEntry.configure(width=17) #allows a maximum of 17 characters to be inputted
  passwordEntry.place(x=360,y=170) #places password entry in window

  if name == "Login":  
    inputUsernameLogin = usernameEntry
    inputPasswordLogin = passwordEntry 
  elif name == "Create":
    inputUsernameCreate = usernameEntry
    inputPasswordCreate = passwordEntry 
  elif name == "Delete":
    inputUsernameDelete = usernameEntry
    inputPasswordDelete = passwordEntry
  elif name == "Reset":
    inputUsernameReset = usernameEntry
    inputPasswordReset = passwordEntry #different values for each for validation purposes

  accountHeading = Label(buttonsWindow, text = "Platforming Paradise") #creates label button with game name
  accountHeading.configure(bg = "red",
                           fg = "white",
                           font = ("Courier", 24, "bold"),
                           height = 2,
                           width = 24)
  accountHeading.place(x=100,y=25) #places button 
    
  usernameLabel = Label(buttonsWindow, text = "Enter Username:") #creates label to direct user where to input username 
  usernameLabel.configure(bg = "white",
                          font = ("Courier", 16, "bold"),
                          height = 1,
                          width = 22,
                          pady=5)
  usernameLabel.place(x=50,y=120) #places button 

  passwordLabel = Label(buttonsWindow, text = "Enter Password:") #creates label to direct user where to input password 
  passwordLabel.configure(bg = "white",
                          font = ("Courier", 16, "bold"),
                          height = 1,
                          width = 22,
                          pady = 5)
  passwordLabel.place(x=50,y=170) #places button 

def createAccount(): #function to create "createAccount" window
  global accountWindow
  global currentwindow #global variables for use elsewhere in the code
  sfx("Click") #plays click sound effect
  loginWindow.withdraw() #closes login window
  accountWindow = tk.Toplevel(window) #creates new window associated to the main window
  createWindow(accountWindow, "Create Account") #creates window called accountWindow
  currentwindow = "Create Account" #changes currentwindow
    
  accountButton = tk.Button(accountWindow,
                          text="Press to \nCreate Account",
                          bg="red",
                          fg="white",
                          font=("Courier", 30, "bold"),
                          height=2,
                          width=16,
                          command=createUser) #button which creates user when pressed
  accountButton.grid(column=0, row=2, padx=10, columnspan=4, sticky="ew") #fills button east to west 
  accountButton.place(x=50,y=225) #places button

  loginButtons(accountWindow, "Create") #calls to create other login buttons
  backButton() #creates back button

def resetPassword(): #function to create window for user to reset password
  global resetWindow
  global currentwindow
  global inputNewPassword #global variables for use elsewhere in the code
  sfx("Click") #plays click sound effect
  loginWindow.withdraw() #closes login window
  resetWindow = tk.Toplevel(window) #creates new window associated to the main window
  createWindow(resetWindow, "Reset Password") #creates window called resetWindow
  currentwindow = "Reset Password" #changes currentwindow

  loginButtons(resetWindow, "Reset") #calls to create other login buttons

  changeLabel = tk.Label(resetWindow, text = "Enter New Password:") #creates a new label as user needs another place to input
  changeLabel.configure(bg = "white", font = ("Courier", 16, "bold"),
                          height = 1, width = 22, pady=5)
  changeLabel.place(x=50,y=215) #places button

  usernameLabel.place(x=50,y=115)
  passwordLabel.place(x=50,y=165)
  usernameEntry.place(x=360,y=115)
  passwordEntry.place(x=360,y=165) #updates placement of login buttons as there are more buttons in this window

  changeEntry = tk.Entry(resetWindow,
                           bg="white",
                           font=("Courier",22, "bold"),
                           show="*") #creates a entry button for users to enter their updated password, which is hidden using *
  changeEntry.grid(column=0, row=1, padx=20, pady=20)
  changeEntry.configure(width=17) #max 17 characters
  changeEntry.place(x=360,y=215) #places button
      
  resetButton = tk.Button(resetWindow,
                          text="Press to \nReset Password",
                          bg="red",
                          fg="white",
                          font=("Courier", 30, "bold"),
                          height=1,
                          width=16,
                          pady=9,
                          command=resetUser) #button which resets password when clicked
  resetButton.grid(column=0, row=2, padx=10, columnspan=4, sticky="ew") #fills button east to west
  resetButton.place(x=50,y=265) #places button

  inputNewPassword = changeEntry #creates new variable for database purposes

  backButton() #creates back button

def deleteAccount(): #function to create window to delete account
  global deleteWindow
  global currentwindow #global variables
  sfx("Click") #plays click sound effect
  loginWindow.withdraw() #closes login window
  deleteWindow = tk.Toplevel(window) #creates new window associated to the main window
  createWindow(deleteWindow, "Delete Account") #creates window called deleteWindow
  currentwindow = "Delete Account" #updates currentwindow

  deleteButton = tk.Button(deleteWindow,
                          text="Press to \nDelete Account",
                          bg="red",
                          fg="white",
                          font=("Courier", 30, "bold"),
                          height=2,
                          width=16,
                          command=deleteUser) #creates button which calls function to delete user when clicked
  deleteButton.grid(column=0, row=2, padx=10, columnspan=4, sticky="ew") #fills button east to west
  deleteButton.place(x=50,y=225) #places button

  loginButtons(deleteWindow, "Delete") #creates other login buttons in window
  backButton() #creates back button

def deleteUser():
  sfx("Click") #plays click sound effect
  username = inputUsernameDelete.get()
  password = inputPasswordDelete.get() #gets inputted username and password from the tkinter window
  deleteFromDatabase(username,password) #calls function to delete information from database

def showResults():
  global username
  sfx("Click") #plays click sound effect
  username = inputUsernameLogin.get()
  password = inputPasswordLogin.get() #gets inputted username and password from the tkinter window
  loginUser(username,password) #calls function to login user from database

def createUser():
  sfx("Click") #plays click sound effect
  username = inputUsernameCreate.get()
  password = inputPasswordCreate.get() #gets inputted username and password from the tkinter window
  addData(username,password) #calls function to add information to database
  addTimeData(username) #creates time data for the new user

def resetUser():
  sfx("Click") #plays click sound effect
  username = inputUsernameReset.get()
  password = inputPasswordReset.get() 
  newpassword = inputNewPassword.get() #gets inputted username, old password and new password from the tkinter window
  updateData(username,password,newpassword) #calls function to update information in database

def openSettings(): #function to open and create buttons for the settings window
  global settingsWindow
  global currentwindow
  global slider
  global tips
  global volume #global variables for use elsewhere in the code
  sfx("Click") #plays click sound effect
  window.withdraw() #hides main window 
  settingsWindow = tk.Toplevel(window) #creates new window associated to the main window
  createWindow(settingsWindow, "Settings") #creates new window called settingsWindow
  currentwindow = "Settings" #updates currentwindow
  
  settingsText = tk.Label(settingsWindow,
                          text="Settings",
                          font=("Courier", 30, "bold"),
                          width=40,
                          fg="white",
                          bg="#202020") #creates label button with text "Settings"
  settingsText.pack() #packs button into window
  
  slider = tk.Scale(settingsWindow,
                    from_=1, to=10,
                    length=350,
                    font=("Courier", 22, "bold"),
                    fg="white",
                    bg="#202020",
                    orient=HORIZONTAL) #creates slider for sound effect volume
  slider.place(x=335,y=70)

  sliderLabel = tk.Label(settingsWindow, text = "Sound Effect Volume:") #creates label stating meaning of slider
  sliderLabel.configure(bg = "white", font = ("Courier", 16, "bold"),
                          height = 2, width = 22, pady=5)
  sliderLabel.place(x=25,y=70) #places button

  volume = slider.get() #gets value of slider
  
  tipsLabel = tk.Label(settingsWindow, text = "Tips: On/Off") #creates label for the tips
  tipsLabel.configure(bg = "white", font = ("Courier", 16, "bold"),
                          height = 2, width = 22, pady=5)
  tipsLabel.place(x=25,y=160) #places button

  audioButton = tk.Button(settingsWindow,
                             text="Test Audio", 
                             font=("Courier", 30, "bold"),
                             width=10,
                             height=1,
                             bg="Red",
                             fg="white",
                             command=checkVolume)  #calls check volume function
  audioButton.place(x=75, y=265) #places buttons

  backButton() #creates back button
  
  if tips:
    imageFile = "assets/Menu/Settings/on.png" #loads on button
  else:
    imageFile = "assets/Menu/Settings/off.png" #loads off button
  image = tk.PhotoImage(file=imageFile).subsample(1,2) #creates tkinter button of image with half height

  toggleButton = tk.Button(settingsWindow, image=image, bd=0, command=changeStatus) #creates button of image
  toggleButton.image = image #reference to button to hold it in memory
  toggleButton.place(x=335, y=160)

def changeStatus(): #changes value of tips boolean
  global tips
  tips = not tips #changes boolean
  settingsWindow.withdraw()
  openSettings() #reopens window
  
def checkVolume(): #checks volume from slider
  global volume
  volume = slider.get() #checks volume from slider
  sfx("Click") #plays click sound effect
    
settingsButton = tk.Button(text="Settings", #uses main window
                           font=("Courier", 30, "bold"),
                           width=10,
                           height=2,
                           bg="black",
                           fg="white",
                           command=openSettings) #main menu buttons called as soon as the function is run
settingsButton.place(x=400, y=200) #places buttons

loginButton = tk.Button(text="Login",
                        font=("Courier", 30, "bold"),
                        width=10,
                        height=2,
                        bg="black",
                        fg="white",
                        command=openLogin) #creates label button which calls to open login
loginButton.place(x=60, y=200) #places button

#Pygame windows setup

def createLevelButton(number, placement, levelWindow, buttonId, unlocked): #function which creates multiple level buttons
    BLACK = (0, 0, 0)
    GREY = (105, 105, 105)
    WHITE = (255, 255, 255) #constants with rbg colours for black and white
                             #x         #y  
    buttonRect = pygame.Rect(placement, 75, 160, 80) #creates button rect for collision purposes
    if unlocked:
      buttonColour = WHITE #sets colour of the button to white
    else:
      buttonColour = GREY
    buttonText = f"Level {number}" #f string using number parameter to create a string
    textColour = BLACK #sets colour of text to black

    pygame.draw.rect(levelWindow, buttonColour, buttonRect) #draws rect onto the pygame level window

    text = font.render(buttonText, True, textColour) #renders text with anti-aliasing for appearance
    textRect = text.get_rect() #creates a rect object representing the text
    textRect.center = buttonRect.center #centres the text on the button

    levelWindow.blit(text, textRect) #draws the text and its rect onto the level window
    return buttonRect, buttonColour, buttonText, font, textColour, text, textRect, buttonId #returns button and text information

def selectorSetup(): #function to create pygame level selector
    BG_COLOR = (26,26,26) #colour of tkinter background converted from hex to rbg
    levelWindow.fill(BG_COLOR) #fills window with the background colour
    xplacement = 50 #x value of the buttons
    buttonRects = []  #creates list of buttons
    currentLevel = findCurrentLevel(username)
    for i in range(currentLevel[0][0]): #creates for 5 buttons
        buttonRect, buttonColour, buttonText, font, textColour, text, textRect, buttonId = createLevelButton((i + 1), xplacement, levelWindow, i + 1, True)
        #return value from createlevelbutton unpacked to variables
        xplacement += 180 #increases xplacement for next button
        buttonRects.append((buttonRect, buttonId)) #adds new button to the list#
    lockedButtons = 5 - currentLevel[0][0]
    if lockedButtons != 0:
      for i in range(lockedButtons): #creates for 5 buttons
        buttonRect, buttonColour, buttonText, font, textColour, text, textRect, buttonId = createLevelButton((i + currentLevel[0][0] + 1), xplacement, levelWindow, i + currentLevel[0][0] + 1, False)
        #return value from createlevelbutton unpacked to variables
        padlock = loadButton("Menu", "Numbers", "Lock.png", xplacement + 75, 115, 70, 70)
        xplacement += 180 #increases xplacement for next button
        buttonRects.append((buttonRect, buttonId)) #adds new button to the list
    return buttonRects #returns list of buttons

def openLevelSelector(): #function to open pygame level selector
    global currentLevelNumber
    global currentwindow #constants for use elsewhere in the code
    loginWindow.withdraw() #hides tkinter login window
    currentLevelNumber = 1 #sets current level number to 1
    currentwindow = "Selector" #sets currentwindow to Selector

    pygame.init() #intialises pygame

    levelWindow = pygame.display.set_mode((WIDTH, HEIGHT)) #sets pygame window to be the size of the constants in beginning of code
    buttonRects = selectorSetup() #retrieves return value from selector setup
    main(levelWindow, buttonRects) #calls main function to begin pygame level

#Main game code
  
def flip(sprites): #function to flip sprites
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites] #True = x, False = Y (only need to flip in x direction)

def loadSprites(dir1, dir2, width, height, direction=False): #loads sprites from computer
    path = join("assets", dir1, dir2) #uses join from os.path with the directories outlined in the parameters
    images = [file for file in listdir(path) if isfile(join(path, file))] #uses list directory previously imported from os, iterates through items in path

    allSprites = {} #creates empty directory to hold sprites

    for image in images: #iterates through each image in images list
        spriteSheet = pygame.image.load(join(path, image)).convert_alpha() #loads image using join with convert alpha to maintain transparency + increase performance

        sprites = [] #creates empty list of sprites
        for i in range(spriteSheet.get_width() // width): #iterates through number of frames in row
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) #creates pygame surface with with and hight outlined in parameters
            rect = pygame.Rect(i * width, 0, width, height) #represents area to be blitted from sprite sheet
            surface.blit(spriteSheet, (0, 0), rect) #specified part of spritesheet blitted onto surface
            sprites.append(surface) #surface added to sprites list

        if direction: #if the sprite can have a direction
            allSprites[image.replace(".png", "") + "_right"] = sprites #creates entry for sprite facing right
            allSprites[image.replace(".png", "") + "_left"] = flip(sprites) #uses flip to create entry for sprite facing left
        else:
            allSprites[image.replace(".png", "")] = sprites #else create entry with image name

    return allSprites #returns allsprites directory
    
def getBlock(width, height): #function to get block from sprite sheet
    path = join("assets", "Terrain", "Test.png") #uses join to get the location of the image
    image = pygame.image.load(path).convert_alpha() #loads image with with convert alpha to maintain transparency + increase performance
    surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) #creates pygame surface with specified width and height
    if colour == "Brown":
      rect = pygame.Rect(622, 236, width, height)
    elif colour == "LightBlue":
      rect = pygame.Rect(622, 313, width, height)      
    elif colour == "Pink":
      rect = pygame.Rect(622, 390, width, height)
    elif colour == "Green":
      rect = pygame.Rect(622, 467, width, height)
    elif colour == "Red":
      rect = pygame.Rect(622, 544, width, height)
    elif colour == "Yellow":
      rect = pygame.Rect(622, 621, width, height)
    elif colour == "DarkBlue":
      rect = pygame.Rect(622, 698, width, height)
    elif colour == "Grey":
      rect = pygame.Rect(622, 775, width, height)      
    elif colour == "FallingBrown":
      rect = pygame.Rect(10, 236, width, height)
    elif colour == "FallingLightBlue":
      rect = pygame.Rect(10, 313, width, height)
    elif colour == "FallingPink":
      rect = pygame.Rect(10, 390, width, height)
    elif colour == "FallingGreen":
      rect = pygame.Rect(10, 467, width, height)
    elif colour == "FallingRed":
      rect = pygame.Rect(10, 544, width, height)
    elif colour == "FallingYellow":
      rect = pygame.Rect(10, 621, width, height)
    elif colour == "FallingDarkBlue":
      rect = pygame.Rect(10, 698, width, height)
    else:
      rect = pygame.Rect(10, 775, width, height) #these lines all access the sprite sheet, using the colour variable to differentiate what part of the image to use     
    surface.blit(image, (0, 0), rect) #blits image and rect to surface
    return pygame.transform.scale2x(surface) #returns surface with size doubled

class Player(pygame.sprite.Sprite): #creates player class inheriting from the sprite
    GRAVITY = 1 #creates value of gravity for player movement
    SPRITES = loadSprites("MainCharacters", "MainCharacter", 32, 32, True) #calls loadsprites function to create the sprite for the player

    def __init__(self, x, y, width, height): #takes in x, y, width, and height as parameters
        super().__init__() #initalises superclass
        self.rect = pygame.Rect(x, y, width, height) #creates rect with the parameters
        self.xVel = 0
        self.yVel = 0 #velocity
        self.mask = None #allows for collision
        self.direction = "left" #direction of player set to left by default
        self.animationCount = 0
        self.fallCount = 0
        self.jumpCount = 0 #constants
        self.jumping = False
        self.hit = False 
        self.hitCount = 0 #detects whether the player has been hit
        self.deaths = 0 #increments when player dies for leaderboard purposes
        self.dead = False #allows for respawns
        self.complete = False #means that levels will end when touching flag
        self.canJump = False #if user can jump
        self.canDoubleJump = False #if user can doublejump

    def jump(self):
        if self.canJump:  #checks if the player is jumping already
          sfx("Jump") #plays jump sound effect
          self.canJump = False #can no longer jump
          if increasedJump: #checks if increased jump is unlocked
            self.yVel = -self.GRAVITY * 6 #negative velocity moves player up
          else:
            self.yVel = -self.GRAVITY * 5 #negative velocity moves player up
          self.jumpCount = 1
          self.fallCount = 0
          self.jumping = True #changes variable to indicate jumping
          spriteSheet = "jump" #updates sprite sheet
        elif self.canDoubleJump:
          sfx("Jump") #plays jump sound effect
          self.canDoubleJump = False
          spriteSheet = "double_jump"
          if increasedJump: #checks if increased jump is unlocked
            selfyVel = -self.GRAVITY * 8 #negative velocity moves player up
          else:
            self.yVel = -self.GRAVITY * 6.5 #negative velocity moves player up
          self.jumpCount = 2
          self.jumping = True #changes variable to indicate jumping
                
    def move(self, xmovement, ymovement): #function to allow player to move
      if not increasedSpeed: #if increased speed powerup not unlocked
        self.rect.x = self.rect.x + xmovement #movement of player added to the x placement
      else: #if powerup is unlocked
        self.rect.x = self.rect.x + (1.2 * xmovement) #movement speed of player doubled        
      self.rect.y = self .rect.y + ymovement #movement of player added to the y placement 

    def makeHit(self): #function to show the player has been hit
        self.hit = True #changes boolean value to true

    def completeLevel(self): #function to show the player has completed a level
        self.complete = True #changes boolean value to true

    def moveLeft(self, vel): #allows left movement
        self.xVel = -vel #negative velocity for left movement
        if self.direction != "left": 
            self.direction = "left" #changes player direction to be facing left
            self.animationCount = 0 #resets animation count

    def moveRight(self, vel): #allows right movement
        self.xVel = vel #positive velocity for right movement
        if self.direction != "right":
            self.direction = "right" #changes player direction to be facing right
            self.animationCount = 0 #resets animation count

    def loop(self, fps): #loop which updates at the frame rate
        global flashCollisions
        global fallingCollisions
        self.yVel = self.yVel + ((self.fallCount/fps)*self.GRAVITY) #updates vertical velocity based on the effect of gravity
        self.move(self.xVel, self.yVel) #moves player by x and y velocity

        self.rect.y += 1  #moves the player slightly to check for collisions
        collisions = pygame.sprite.spritecollide(player, objects, False) #list of normal blocks player collides with
        self.rect.y -= 1  #moves the player back

        if flashing: #if level has flashing blocks
          self.rect.y += 1  #moves the player slightly to check for collisions
          flashCollisions = pygame.sprite.spritecollide(player, flashObjects, False) #list of flashing blocks player collides with
          self.rect.y -= 1  #moves the player back
        if falling: #if level has falling blocks
          self.rect.y += 1  #moves the player slightly to check for collisions
          fallingCollisions = pygame.sprite.spritecollide(player, fallingObjects, False) #list of falling blocks player collides with
          self.rect.y -= 1  #moves the player back
        if collisions: #if colliding with a normal block
          self.canJump = True #player can jump
          if doubleJump: #if user has unlocked doublejump
            self.canDoubleJump = True #can also doublejump
        elif flashCollisions: #if colliding with a flashing block
          if not hidden: #block is showing
            self.canJump = True #player can jump
            if doubleJump: #if user has unlocked doublejump
              self.canDoubleJump = True #can also doublejump        
        elif fallingCollisions: #if colliding with a falling block
          self.canJump = True #player can jump
          if doubleJump: #if user has unlocked doublejump
            self.canDoubleJump = True #can also doublejump    
        else:
          self.canJump = False #cannot jump
          if self.jumping and self.jumpCount != 2 and doubleJump: #if user can double jump
            self.canDoubleJump = True #allow double jump
          else:
            self.canDoubleJump = False #else dont allow
            
        if self.hit:
            self.hitCount += 1
        if self.hitCount > fps:
            self.hit = False
            self.hitCount = 0 #resets if exceeds frame count

        self.fallCount = self.fallCount + 1 #increasing y velocity
        self.updateSprite() #updates sprite

    def landed(self): #function when player lands
        self.yVel = 0 
        self.fallCount = 0
        self.jumpCount = 0 #variables reset
        self.canJump = True
        self.jumping = False
        if doubleJump:
          self.canDoubleJump = True

    def hitHead(self): #function when player hits the bottom of an object
        self.animationCount = 0 #resets count
        self.yVel = self.yVel * -1 #changes y velocity to make the player move downwards

    def respawn(self,respawnX,respawnY): #function to respawn player
        self.deaths += 1 #increments deaths
        player.rect.x = respawnX
        player.rect.y = respawnY #sets new values where user respawns
        self.dead = True #changes boolean value to indicate the player has died

    def updateSprite(self): #function to update player information
        global spriteSheet
        if spriteSheet != "double_jump":
          spriteSheet = "idle" #default spritesheet
        if self.hit:
            spriteSheet = "hit" #changes the spritesheet to one indicating the player has been hit
            if currentLevelNumber == 1:
              self.respawn(0, 200)
            elif currentLevelNumber == 2:
              self.respawn(0, 300)
            elif currentLevelNumber == 3:
              self.respawn(0, 290)
            elif currentLevelNumber == 4:
              self.respawn(0, 280)
            elif currentLevelNumber == 5:
              self.respawn(0, 300) #different respawn places dependant on the level
        elif self.yVel > self.GRAVITY * 2: #checks if the player is falling
            spriteSheet = "fall" #changes sprite sheet to fall
        elif self.xVel != 0: #indicates the player is moving
            spriteSheet = "run" #changes sprite sheet to run

        spriteSheetName = spriteSheet + "_" + self.direction #sets sprite sheet name
        sprites = self.SPRITES[spriteSheetName] #retrieves list of sprites with spritesheetname
        spriteIndex = (self.animationCount // 3) % len(sprites) #calculates index of sprite to be used
        self.sprite = sprites[spriteIndex] #sets sprite attribute to sprite determined by the index
        self.animationCount += 1 #increments animation count
        self.update() #updates player

    def update(self): #function to update player
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y)) #updates rect using topleft to ensure position is still the same
        self.mask = pygame.mask.from_surface(self.sprite) #updates mask for collision

    def draw(self, window): #function to draw to window
        window.blit(self.sprite, (self.rect.x, self.rect.y)) #draws sprites and its position to window

class Object(pygame.sprite.Sprite): #object so collision is uniform
    def __init__(self, x, y, width, height, name=None): 
        super().__init__() #initialises superclass
        self.rect = pygame.Rect(x, y, width, height) #creates rect with variables indicated in parameters
        self.image = pygame.Surface((width, height), pygame.SRCALPHA) #creates pygame surface with opacity and indicated with and height
        self.name = name #sets to name if present
        self.width = width 
        self.height = height

    def draw(self, window): #function to draw object
      if self.image is not None:
        window.blit(self.image, (self.rect.x,self.rect.y)) #draws to window

class Block(Object): #class creates blocks inheriting from object class
  global width
  global height #global variables for use elsewhere
  def __init__(self, x, y, width, height):
      super().__init__(x, y, width, height) #initalises superclass
      block = getBlock(width,height) #uses getblock function to create block
      self.image.blit(block, (0, 0)) #blits block to image
      self.x = x
      self.y = y
      self.originalX = self.x #holds original x position
      self.originalY = self.y #holds original y position
      self.mask = pygame.mask.from_surface(self.image) #allows collision for the image
      self.hidden = True #hidden set to true by default for flashing blocks
      self.timer = 0 #for use in flashing block
      self.speed = 2 #for use in falling block
        
  def flash(self): #function to flash the block
      self.timer += 1 #increments timer
      if self.timer < 50:
        levelWindow.blit(self.image, (5000,5000)) #draw off screen - hidden
      elif self.timer >= 50:
        self.hidden = False #set block to be showing
        if self.timer == 100: 
          self.timer = 0 #reset timer every 50 ticks
          self.hidden = True #hide block again

  def falling(self, spriteGroup): #function to allow the block to fall, sprite group as parameter
    global fallingCollision
    if self.y < HEIGHT: #checks y is less than the height
      self.y += self.speed #moves block downwards
      self.rect.center = (self.x + 30, round(self.y + 35)) #sets centre of rect to new position
    else:
      self.x = self.originalX  #resets x
      self.y = self.originalY  #resets y
      self.rect.center = (self.originalX + 30, self.originalY + 35) #updates block position
      levelWindow.blit(self.image, (self.originalX, self.originalY)) #redraws to screen
      fallingCollision = False #block no longer falls
      pygame.display.update()
                          
class Stopwatch: #class for the stopwatch
  def __init__(self):
    self.startTime = None
    self.elapsedTime = 0
    self.running = False #false by default as stopwatch does not immediately start

  def start(self): #function to start stopwatch
    if self.running:
      return #no effect if already running
    self.startTime = time.time() - self.elapsedTime #uses time module to find start time
    self.running = True #sets stopwatch to running

  def stop(self): #function to stop stopwatch
    if not self.running:
        return #no effect if already stopped
    self.elapsedTime = time.time() - self.startTime #elapsed time calculation
    self.running = False #running set to false as level finished

  def reset(self): #function to reset stopwatch
    self.elapsedTime = 0
    self.running = False #resets values to default

  def logTime(self): #loop function to log time elapsed
    global minutes,seconds,tenths
    minutes = int(self.elapsedTime // 60)
    seconds = int(self.elapsedTime % 60)
    tenths = int((self.elapsedTime % 1) * 10) #calculations to find minutes, seconds and tenths from elapsed time
    if self.running:
      self.currentTime = time.time() #current time = time module
      self.elapsedTime = self.currentTime - self.startTime #minuses start time to find time elapsed on level
    self.totalTime = self.elapsedTime #total time set the elapsed time

  def getTime(self): #gets time from database
    return float(self.elapsedTime)
        
def getBackground(name): #function to get background
    image = pygame.image.load(join("assets", "Background", name)) #loads image using join and the name outlined in parameter
    _, _, width, height = image.get_rect() #width and height from rect unpacked, underscores represent unneeded values
    tiles = [] #empty list

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1): #iterates positions based on width and height of window
            pos = (i * width, j * height) #tuple represents top left corner of tile
            tiles.append(pos) #tuple added to list

    return tiles, image #returns tiles list and loaded image

def loadButton(dir1, dir2, name, x, y, width, height): #takes in many parameters holding the image information
  image = pygame.image.load(join("assets", dir1, dir2, name)).convert_alpha() #loads image using join, name outlined in parameter and convert alpha to maintain transparency + increase performance
  image = pygame.transform.scale(image, (width, height))  #scales image based off the width and height
  imageRect = image.get_rect(center=(x, y)) #creates rect at centre of image
  levelWindow.blit(image, imageRect) #draws image to screen
  return imageRect
    
def getText(horizontal, vertical, increase): #renders text from image
  path = join("assets", "Menu", "Text", "Text.png") #uses join to get the location of the image
  image = pygame.image.load(path).convert_alpha() #loads image with with convert alpha to maintain transparency + increase performance
  baseWidth, baseHeight = 30, 40 #base size of text
  surface = pygame.Surface((baseWidth, baseHeight), pygame.SRCALPHA, 32) #creates pygame surface with specified width and height
  xPos = 5 + (vertical - 1) * 40 #base number of pixels from the left, + vertical column * number of pixels between text
  yPos = 5 + (horizontal - 1) * 50 #base number of pixels from the top, + horizontal row * number of pixels between text
  rect = pygame.Rect(xPos, yPos, baseWidth, baseHeight) #creates rect of text
  surface.blit(image, (0, 0), rect) #blits image and rect to surface
  if increase == False: 
    return surface #returns text
  elif increase == True: #scale by 2
    return pygame.transform.scale2x(surface) #returns surface with size doubled

def loadText(text, colour, x, y): #function loads text using custom font
  img = font.render(text, True, colour) #renders text as image with anti aliasing
  levelWindow.blit(img, (x, y)) #draws to screen
  
def getLeaderboardImage(info, level): #function to get the background of the leaderboard
  BLACK = (0, 0, 0)
  YELLOW = (255, 255, 0)
  image = pygame.image.load(join("assets", "Menu", "Leaderboard", "LeaderboardBackground.png")) #image directory
  levelWindow.blit(image, (0,0)) #draws to window from the top left of the screen
  if level != 0:
    info = getData(leaderboardNo) #gets general scores information from database

  nameText = font.render("Username", True, YELLOW) #renders text
  levelWindow.blit(nameText, (172, 81)) #draws to window
  if level == 0:
    totalTimeText = font.render("Total", True, YELLOW) #renders text
    levelWindow.blit(totalTimeText, (558, 81)) #draws to window
  else:
    levelNo = "Level" + str(level) #gets level number
    levelText = font.render(levelNo, True, YELLOW) #renders text
    levelWindow.blit(levelText, (558, 81)) #draws to window
  currentLevelText = font.render("Level", True, YELLOW) #renders text
  levelWindow.blit(currentLevelText, (799, 81)) #draws to window
  for rank in range(0,7): #7 spaces on the background image
    rankNum = font.render(str(rank + 1), True, BLACK) #renders numbers 1-7
    levelWindow.blit(rankNum, (80, 133 + (48 * rank + 1))) #draws to window
  for name in range(0,7): #first 7 users in database
    for value in range(0,2): #cycles through values in info
      userInfo = font.render(str(info[name][value]),True,BLACK) #user information from database
      levelWindow.blit(userInfo, (110 + (405 * value), 133 + (48 * name + 1))) #draws to screen
    userInfo = font.render(str(info[name][2]), True, BLACK) #outside the for loop for greater distance
    levelWindow.blit(userInfo, (743, 133 + (48 * name + 1))) #draws to screen
    
  pygame.display.update() #updates window

def getShopImage(doubleJumpB, increasedJumpB, increasedSpeedB): #function to create the shop buttons
  image = pygame.image.load(join("assets", "Menu", "Shop", "ShopBackground.png")) #image directory
  image = pygame.transform.scale(image, (WIDTH, HEIGHT)) #resizes image to size of screen
  levelWindow.blit(image, (0,0)) #draws to window from the top left of the screen
  
  coinAmount = findCoinAmount(username)[0][0] #finds amount of coins the user has
  
  if coinAmount <= 10: #coin amount cannot be more than 10 (2 * max levels)
    if coinAmount < 10: #requires 1 digit rendered
      num1 = getText(4, (coinAmount + 1), False) #finds number
      image.blit(num1, (190,21))
    else:
      num1 = getText(4, 2, False) #renders 1
      coinAmount -= 10 #removes to to find second digit
      num2 = getText(4, (coinAmount + 1), False) #finds number
      image.blit(num1, (160,21))
      image.blit(num2, (190,21)) #draws numbers to image
    levelWindow.blit(image, (0,0)) #draws to screen
  loadButton("Menu", "Buttons", "Coins.png", 270, 38, 80, 80) #loads coins button
  powerupInfo = findPowerups(username) #finds powerups from database
  
  if doubleJumpB or powerupInfo[0][0] == 1: #powerup already unlocked
    doubleJumpButton = loadButton("Menu", "Buttons", "DoubleJumpUnlocked.png", 269, 240, 80, 80) 
  else:
    doubleJumpButton = loadButton("Menu", "Buttons", "DoubleJump.png", 269, 240, 80, 80)   
  if increasedJumpB or powerupInfo[0][1] == 1: #powerup already unlocked
    increasedJumpButton = loadButton("Menu", "Buttons", "IncreasedJumpUnlocked.png", 424, 240, 80, 80)
  else:
    increasedJumpButton = loadButton("Menu", "Buttons", "IncreasedJump.png", 424, 240, 80, 80)   
  if increasedSpeedB or powerupInfo[0][2] == 1: #powerup already unlocked
    increasedSpeedButton = loadButton("Menu", "Buttons", "IncreasedSpeedUnlocked.png", 572, 240, 100, 100)  
  else:
    increasedSpeedButton = loadButton("Menu", "Buttons", "IncreasedSpeed.png", 572, 240, 100, 100) #draws buttons
    
  shopButtons = [doubleJumpButton, increasedJumpButton, increasedSpeedButton]
  pygame.display.update() #updates window
  return shopButtons #returns rects of buttons

#draw function maintained outside of the while loop to reduce lag and flickering
def draw(window, background, bg_image, player, objects, stopwatch, text, flash, flashObj, falling, fallingObj): #function to draw objects
    for tile in background:
        window.blit(bg_image, tile) #draws each tile to background image

    for obj in objects: #iterates through objects
        obj.draw(window) #draws to window

    if flash: #flash parameter is boolean
      for obj in flashObjects: #iterates through objects
        obj.flash() #calls flash function for each object
        if not obj.hidden:
          obj.draw(levelWindow)
          pygame.display.update() #draw if obj is showing

    if falling:
      for obj in fallingObj: #iterates through objects
          obj.draw(levelWindow) #draws object to window
          if fallingCollision: 
            obj.falling(fallingObj) #if user collides with object call falling function

    window.blit(textSurface, textRect) #draws text and rect to window
    
    if currentLevelNumber == 1:
      loadText(text[0], (0,0,0), 12,12)
      loadText(text[1], (0,0,0), 740,170)
      loadText(text[2], (0,0,0), 740,210) #draws text in position
    elif currentLevelNumber == 2:
      loadText(text[0], (0,0,0), 450,190)
      loadText(text[1], (0,0,0), 450,230) #draws text in position
    elif currentLevelNumber == 4:
      loadText(text[0], (0,0,0), 350,50) #draws text in position
    elif currentLevelNumber == 5:
      loadText(text[0], (0,0,0), 300,10) #draws text in position
    player.draw(window) #draws player to window
    
    pygame.display.update() #updates window

def verticalCollision(player, objects, ymovement): #function handles vertical collision
    global fallingCollision #global variable for use elsewhere in the code
    global collide
    collidedObjects = [] #empty list
    for obj in objects: #iterates through objects
        if pygame.sprite.collide_mask(player, obj): #if player and object collides
          if obj.name != "Coin": #not relevant when colliding with coin
              if ymovement > 0:  #moving down, colliding with top
                if obj.name == "FallingBlock": 
                  fallingCollision = True #changes boolean value to make block fall
                player.rect.bottom = obj.rect.top  #place player just below the object
                player.landed() #calls function as player has landed
              elif ymovement < 0:  #moving up, colliding with bottom
                player.rect.top = obj.rect.bottom #places player at the bottom of the object
                player.hitHead() #calls function as player has hit head

          collidedObjects.append(obj) #adds obj to collidedobjects list

    return collidedObjects #returns list

def horizontalCollision(player, objects, xmovement): #function handles horizontal collision
    player.move(xmovement, 0) #checking if they hit a block if moving
    player.update() #update before cheking for collision
    collidedObject = None #no collided object
    for obj in objects: #iterates through objects
        if pygame.sprite.collide_mask(player, obj): #if player and object collide
          if obj and obj.name == "Coin": #coin does not need collision
            break #end function
          collidedObject = obj #update
          break #end function

    player.move(-xmovement, 0) #move back
    player.update() #update new position
    return collidedObject #returns object player collided with

class Lava(Object): #lava class takes in object as parent class
    ANIMATION_DELAY = 2 #constant to delay animations
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Lava") #initialises superclass
        self.lava = loadSprites("Objects", "Lava", width, height) #loads lava sprite
        self.animationName = "Lava 1" #animation begins at 1
        self.image =self.lava[self.animationName][0] #first image in lava directory
        self.mask = pygame.mask.from_surface(self.image) #allows for collision
        self.animationCount = 0
        self.hidden = False

    def loop(self): #loop called in while function
        if self.animationName in self.lava: #checks if name is present
            sprites = self.lava[self.animationName]
            spriteIndex = (self.animationCount // self.ANIMATION_DELAY) % len(sprites) #calculates image to use
            self.image = sprites[spriteIndex] #updates self image to be image from spriteindex
            self.animationCount += 1 #increments animation count

            if self.animationCount // self.ANIMATION_DELAY >= 6: #6 images in directory
                animationNumber = int(self.animationName.split()[-1]) #extracts current animation number
                animationNumber = (animationNumber % 6) + 1 # calculates animation number
                self.animationName = f"Lava {animationNumber}" #updates animation name
                self.animationCount = 0 #updates animation count

            self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) #creates rect of lava
            self.mask = pygame.mask.from_surface(self.image) #masks image for collision
        else: #if number increments outside of directory
             self.animationCount = 0 #reset animation count

class Finish(Object): #class for finish line using object as a parent class
    ANIMATION_DELAY = 1 #constant to delay animations
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Finish") #initialises superclass
        self.finish = loadSprites("Completion", "Finish", width, height) #loads finish sprite
        self.animationName = "Finish 1" #animation begins at 1
        self.image = self.finish[self.animationName][0] #first image in finish directory 
        self.mask = pygame.mask.from_surface(self.image)# allows for collision
        self.animationCount = 0
        self.hidden = False

    def loop(self):
        if self.animationName in self.finish:
            sprites = self.finish[self.animationName]
            spriteIndex = (self.animationCount // self.ANIMATION_DELAY) % len(sprites) #calculates image to use
            self.image = sprites[spriteIndex] #updates self image to be image from spriteindex
            self.animationCount += 1 #increments animation count

            if self.animationCount // self.ANIMATION_DELAY >= 10: #10 images in directory
                animationNumber = int(self.animationName.split()[-1]) #splits animationnumber into substrings and finds last in list
                animationNumber = (animationNumber % 10) + 1 #calculates animation number
                self.animationName = f"Finish {animationNumber}" #updates animation name
                self.animationCount = 0 #updates animation count

            self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) #creates finish rect
            self.mask = pygame.mask.from_surface(self.image) #masks image for collision
        else: #if number increments outside of directory
            self.animationCount = 0 #reset animation count

class Coins(Object): #class for coins using object as a parent class
    ANIMATION_DELAY = 2 #constant to delay animations
    def __init__(self, x, y, width, height):
      super().__init__(x, y, width, height, "Coin") #initialises superclass
      self.coin = loadSprites("Objects", "Coins", width, height) #loads coin sprite
      self.animationName = "Coin 1" #animation begins at 1
      self.image = self.coin[self.animationName][0] #first image in coin directory 
      self.mask = pygame.mask.from_surface(self.image)# allows for collision
      self.animationCount = 0
      self.collected = False #checks whether the coin has been collected by the user
      self.hidden = False

    def loop(self):
        if self.animationName in self.coin:
            sprites = self.coin[self.animationName]
            spriteIndex = (self.animationCount // self.ANIMATION_DELAY) % len(sprites) #calculates image to use
            self.image = sprites[spriteIndex] #updates self image to be image from spriteindex
            self.animationCount += 1 #increments animation count

            if self.animationCount // self.ANIMATION_DELAY >= 6: #6 images in directory
                animationNumber = int(self.animationName.split()[-1]) #splits animationnumber into substrings and finds last in list
                animationNumber = (animationNumber % 6) + 1 #calculates animation number
                self.animationName = f"Coin {animationNumber}" #updates animation name
                self.animationCount = 0 #updates animation count

            self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y)) #creates finish rect
            self.mask = pygame.mask.from_surface(self.image) #masks image for collision
        else: #if number increments outside of directory
            self.animationCount = 0 #reset animation count

    def removeCoin(self):
      self.collected = True #sets coin to collected
      self.coin = None
      self.image = None #deletes image
      self.mask = pygame.mask.Mask((0,0)) #clears mask
      pygame.display.update() #updates screen

def fade(starting): #function to fade between screens
  global currentwindow #global variable for use elsewhere
  fade = pygame.Surface((WIDTH,HEIGHT)) #creates a surface which is the size of the window
  fade.fill((0,0,0)) #fills surface with black
  for alpha in range(0,300): #loops through alpha values
    fade.set_alpha(alpha) #iterates 300 times through alpha settings
    if starting == False: #if ending a level
      currentwindow = "Selector" #changes window to selector window
    else: #if starting a level
      currentwindow = "Level" #changes window to level window
    levelWindow.blit(fade, (0,0)) #draws fade to window
    pygame.display.update() #updates window
    pygame.time.delay(2) #delays by two ticks so that the window fades slowly
    
def handleHorizontalMove(player, objects): #function to handle horizontal movement
  keys = pygame.key.get_pressed() #notes keys pressed by user

  player.xVel = 0
  collideLeft = horizontalCollision(player,objects, -PLAYER_VEL * 2) #introduces distance
  collideRight = horizontalCollision(player,objects, PLAYER_VEL * 2)

  if keys[pygame.K_LEFT] and not collideLeft: #means user is free to move
    if not (player.rect.x < 0): #prevents player from running off the left side of the screen
      player.moveLeft(PLAYER_VEL)
  elif keys[pygame.K_a] and not collideLeft: #means user is free to move
    if not (player.rect.x < 0): #prevents player from running off the left side of the screen
      player.moveLeft(PLAYER_VEL)
  if keys[pygame.K_RIGHT] and not collideRight: #means user is free to move
    if (player.rect.x) < (WIDTH-20): #prevents player from running off the right side of the screen
      player.moveRight(PLAYER_VEL)
  elif keys[pygame.K_d] and not collideRight: #means user is free to move
    if (player.rect.x) < (WIDTH-20): #prevents player from running off the right side of the screen
      player.moveRight(PLAYER_VEL)

def handleVerticalMove(player, objects): #function to handle vertical movement
  global checkCollision #global variable for use elsewhere
  verticalCollide = verticalCollision(player, objects, player.yVel)
  checkCollision = [*verticalCollide] #unpacks vertical collide 

def handleMove(player, objects, flash=False, falling=False): #function to handle movement
    if not flash: #no flashing blocks in level
      handleHorizontalMove(player, objects)
      handleVerticalMove(player, objects)
      if not falling: #no falling blocks in level
        for obj in checkCollision: #iterates through list
          if obj and obj.name == "Lava":
            player.makeHit() #make hit when colliding with lava
          if obj and obj.name == "Finish":
            sfx("Finish") #plays finish sound effect
            player.completeLevel() #complete level when colliding with flag
          if obj and obj.name == "Coin":
            sfx("Coin") #plays coin sound effect
            obj.removeCoin() #removes coin from screen
            addCoin(username) #increments users coin count
            objects.remove(obj) #removes object from list of objects
      else:
        for obj in checkCollision: #iterates through list
          if obj and obj.name == "FallingObject":
            handleHorizontalMove(player, objects)
            handleVerticalMove(player, objects) #handle movement if block is a falling block
    else: #flashing block in level
      if not falling: #no falling block
        handleHorizontalMove(player, objects)
        handleVerticalMove(player, objects) #handles movement
        
def main(window, buttonRects): #main game function
  global player
  global new
  global currentwindow
  global colour
  global run
  global flashObjects
  global fallingObjects
  global flashing
  global falling
  global textSurface
  global textRect
  global doubleJump
  global objects
  global hidden
  global doubleJumpClicked
  global increasedJumpClicked
  global increasedSpeedClicked
  global powerupInfo
  global increasedSpeed
  global increasedJump
  global stopwatch
  global leaderboardNo
  global currentLevelNumber #global variables for use elsewhere in the code
  clock = pygame.time.Clock() #creates clock
  flashing = False
  falling = False #boolean values for checking if level has any special blocks
  hidden = True #variable used to see if flashing objects are hidden or not
  text = None
  text2 = None
  text3 = None #variables needed if there are less than 3 tips on screen
  while currentwindow == "Selector":
    fallingCollision = False #resets falling collision when going back to selector
    run = True
    BG_COLOR = (26,26,26) #background colour used elsewhere
    levelWindow.fill(BG_COLOR) #fills background
    userLevel = findCurrentLevel(username) #finds current level user has unlocked
    while run: #constant loop
        clock.tick(FPS) #clock ticks at 60fps for performance reasons
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False #closes program
                break
            elif event.type == pygame.MOUSEBUTTONDOWN:
              if event.button == 1: #left mouse button
                if leaderboard.collidepoint(event.pos): #if button clicked
                  sfx("Click") #plays click sound effect
                  currentwindow = "Leaderboard" #switch to leaderboard
                  run = False
                if shop.collidepoint(event.pos): #if button clicked
                  sfx("Click") #plays click sound effect
                  currentwindow = "Shop" #switch to shop
                  run = False
            for buttonRect, buttonId in buttonRects: #iterates through buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                  if event.button == 1: #left mouse button
                    if buttonRect.collidepoint(event.pos): #if button clicked
                      if userLevel[0][0] >= buttonId:
                        sfx("Click") #plays click sound effect
                        currentwindow = "Level" #change current window
                        currentLevelNumber = buttonId #update current level number
                        run = False
                      else: #level not unlocked
                        sfx("Error") #error sound effect
        selectorSetup() #creates selector
        leaderboard = loadButton("Menu", "Buttons", "Leaderboard.png", 945, 450, 128, 128) #creates leaderboard button
        shop = loadButton("Menu", "Buttons", "Shop.png", 128, 450, 128, 128) #creates shop button
        pygame.display.update() #updates window
        
  if currentwindow == "Leaderboard":
    info = getData(leaderboardNo) #gets general scores information from database
    run = True
    getLeaderboardImage(info, leaderboardNo) #creates leaderboard screen
    back = loadButton("Menu", "Buttons", "Back.png", 945, 450, 128, 128) #creates back button
    if leaderboardNo != 5: #5 levels
      number =  str(leaderboardNo + 1) + ".png"
      numberButton = loadButton("Menu", "Numbers", number, 945, 55, 128, 128) #creates leaderboard button
    else:
      numberButton = loadButton("Menu", "Buttons", "Leaderboard.png", 945, 55, 128, 128) #creates level button
    while run:
      clock.tick(FPS) #clock ticks at 60fps for performance reasons
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          run = False #closes program
          break
        elif event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 1: #left mouse button
            if back.collidepoint(event.pos): #if button clicked
              sfx("Click") #plays click sound effect
              currentwindow = "Selector" #switch to selector
              run = False
              main(levelWindow, buttonRects) #recalls main function recursively to return to level selector
            if numberButton.collidepoint(event.pos):
              sfx("Click") #plays click sound effect
              if leaderboardNo == 5: #if last level
                leaderboardNo = 0 #resets variable
              else:
                leaderboardNo += 1 #increments
              run = False
              main(levelWindow, buttonRects) #recalls main function recursively to return to level selector
      pygame.display.update() #updates window

  if currentwindow == "Shop":
    run = True
    while run:
      if doubleJumpClicked:
        if increasedJumpClicked:
          if increasedSpeedClicked:
            shopButtons = getShopImage(True, True, True)
          else:
            shopButtons = getShopImage(True, True, False)
        else:
          if increasedSpeedClicked:
            shopButtons = getShopImage(True, False, True)
          else:
            shopButtons = getShopImage(True, False, False)
      elif increasedJumpClicked:
        if increasedSpeedClicked:
          shopButtons = getShopImage(False, True, True)
        else:
          shopButtons = getShopImage(False, True, False)
      elif increasedSpeedClicked:
        shopButtons = getShopImage(False, False, True)
      else:
        shopButtons = getShopImage(False, False, False) #checks all possible combinations of buttons and removes if needed
      back = loadButton("Menu", "Buttons", "Back.png", 945, 450, 128, 128) #creates back button
      clock.tick(FPS) #clock ticks at 60fps for performance reasons
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          run = False #closes program
          break
        elif event.type == pygame.MOUSEBUTTONDOWN:
          if event.button == 1: #left mouse button
            if back.collidepoint(event.pos): #if button clicked
              sfx("Click") #plays click sound effect
              currentwindow = "Selector" #switch to selector
              run = False
              main(levelWindow, buttonRects) #recalls main function recursively to return to level selector
            if shopButtons[0] is not None and shopButtons[0].collidepoint(event.pos):  #double jump button
              coinAmount = findCoinAmount(username)[0][0] #finds amount of coins the user has
              if coinAmount < 5: #coin price
                sfx("Error") #plays error sound effect
                print("You do not have enough coins")
              else: 
                if not doubleJumpClicked: #if powerup is not already unlocked
                  sfx("Click") #plays click sound effect
                  updatePowerup(username, True, False, False) #updates database
                  removeCoins(username, 5) #removes 5 coins from user
                  doubleJump = True
                  doubleJumpClicked = True #updates boolean variables
                else:
                  sfx("Error") #plays error sound effect
                  print("You have already unlocked this powerup")
            elif shopButtons[1] is not None and shopButtons[1].collidepoint(event.pos): #increased jump button
              coinAmount = findCoinAmount(username)[0][0] #finds amount of coins the user has
              if coinAmount < 5:
                sfx("Error") #plays error sound effect
                print("You do not have enough coins")
              else: 
                if not increasedJumpClicked: #if powerup is not already unlocked
                  sfx("Click") #plays click sound effect
                  updatePowerup(username, False, True, False) #updates database
                  removeCoins(username, 5) #removes 5 coins from user
                  increasedJump = True
                  increasedJumpClicked = True #updates boolean variables
                else:
                  sfx("Error") #plays error sound effect
                  print("You have already unlocked this powerup")
            elif shopButtons[2] is not None and shopButtons[2].collidepoint(event.pos): #increased speed button
              coinAmount = findCoinAmount(username)[0][0] #finds amount of coins the user has
              if coinAmount < 5:
                sfx("Error") #plays error sound effect
                print("You do not have enough coins")
              else: 
                if not increasedSpeedClicked: #if powerup is not already unlocked
                  sfx("Click") #plays click sound effect
                  updatePowerup(username, False, False, True) #updates database
                  removeCoins(username, 5) #removes 5 coins from user
                  increasedSpeed = True
                  increasedSpeedClicked = True #updates boolean variables
                else:
                  sfx("Error") #plays error sound effect
                  print("You have already unlocked this powerup")
      pygame.display.update() #updates window
        
  if currentwindow == "Level":
    background, bg_image = getBackground("MainBackground.png") #creates background
    
    stopwatch = Stopwatch()
    lava = Lava(0, HEIGHT - 64, 1000, 64) #creates lava + stopwatch constant for all levels

    blockSize = 70 #constant holding the default block size
    run = True

    stopwatch.reset() #resets stopwatch
    
    powerupInfo = findPowerups(username) #finds what powerups user has unlocked
    if powerupInfo[0][0] == 1: #if doubleJump is unlocked
      doubleJump = True #allow double jump
    if powerupInfo[0][1] == 1: #if increasedJump is unlocked
      increasedJump = True #allow increased jump
    if powerupInfo[0][2] == 1: #if increasedSpeed is unlocked
      increasedSpeed = True #allow increased speed
      
    if currentLevelNumber == 1:
        player = Player(0, 200, 50, 50)
        finish = Finish(890,355 - blockSize,64,64)
        coinList = [Coins(375,111,64,64),  
                    Coins(375,261,64,64)] #coins in list as there are multiple
        colour = "Brown" #block colour
        objects = [Block(0, 250, blockSize * 3 + 3, blockSize),
                   Block(300, 175, blockSize * 3 + 3, blockSize),                  
                   Block(300, 325, blockSize * 3 + 3, blockSize),
                   Block(670, 350, blockSize * 4 + 5, blockSize),
                   lava,
                   finish] #creates actual geometry of the level
        objects.extend(coinList) #adds coins to list
        flashing = False #no flashing block
        if tips: #if tips are on
          text = "Use WASD/Arrow Keys" #tips for level
          text2 = "Hit the top"
          text3 = "of the flag!"

    if currentLevelNumber == 2:
        player = Player(0, 300, 50, 50)
        finish = Finish(925,345 - blockSize,64,64)
        coinList = [Coins(302,308,64,64),  
                    Coins(848,278,64,64)] #coins in list as there are multiple
        colour = "LightBlue" #block colour
        objects = [Block(0, 370, blockSize, blockSize),
                   Block(150, 290, blockSize, blockSize),
                   Block(300, 240, blockSize, blockSize),
                   Block(300, 370, blockSize, blockSize),
                   Block(150, 180, blockSize, blockSize),
                   Block(0, 115, blockSize, blockSize),
                   Block(150, 40, blockSize * 5 + 5, blockSize),
                   Block(775, 340, blockSize * 3 + 3, blockSize),
                   lava,
                   finish] #creates actual geometry of the level
        objects.extend(coinList) #adds coins to list
        flashing = False #no flashing block
        if tips: #if tips are on
          text = "Collect coins to" #tips for level
          text2 = "buy powerups!"

    if currentLevelNumber == 3:
        player = Player(0, 290, 50, 50)
        finish = Finish(882,360 - blockSize,64,64)
        coinList = [Coins(813,18,64,64),  
                    Coins(3,98,64,64)] #coins in list as there are multiple
        colour = "Pink" #block colour
        objects = [Block(0, 350, blockSize, blockSize),
                   Block(0, 160, blockSize, blockSize),
                   Block(270, 350, blockSize, blockSize),
                   Block(400, 280, blockSize, blockSize),
                   Block(250, 220, blockSize, blockSize),
                   Block(120, 160, blockSize, blockSize),
                   Block(220, 80, blockSize * 5 + 5, blockSize),
                   Block(810, 80, blockSize, blockSize),
                   Block(810, 80 + blockSize, blockSize, blockSize),
                   Block(810, 80 + blockSize * 2, blockSize, blockSize),
                   Block(810, 110 + blockSize * 3 + 35, blockSize * 2, blockSize),
                   lava,
                   finish] #creates actual geometry of the level
        objects.extend(coinList) #adds coins to list
        flashing = False #no flashing block

    if currentLevelNumber == 4:
        player = Player(0, 280, 50, 50)
        finish = Finish(930,225 - blockSize,64,64)
        coinList = [Coins(452,137,64,64),  
                    Coins(817,297,64,64)] #coins in list as there are multiple
        colour = "Green" #block colour
        objects = [Block(0, 330, blockSize * 2 + 2, blockSize),
                   Block(450, 200, blockSize, blockSize),
                   Block(815, 360, blockSize, blockSize),
                   Block(850, 220, blockSize * 2 + 2, blockSize),
                   lava, 
                   finish] #creates actual geometry of the level
        objects.extend(coinList) #adds coins to list
        flashObjects = [Block(340, 280, blockSize * 5 + 5, blockSize)] #flashing block
        flashing = True #boolean set to true as level has a flashing block
        if tips: #if tips are on
          text = "Time your jump!" #tips for level
        
    if currentLevelNumber == 5:
        player = Player(0, 300, 50, 50)
        finish = Finish(70, 0, 64, 64)
        coinList = [Coins(802,48,64,64),  
                    Coins(400,68,64,64)] #coins in list as there are multiple
        colour = "Red" #block colour
        objects = [Block(0, 350, blockSize * 2 + 2, blockSize),
                   Block(70, 64, blockSize, blockSize),
                   Block(360, 220, blockSize, blockSize),
                   Block(360, 130, blockSize * 3 + 3, blockSize),
                   Block(660, 340, blockSize * 2 + 2, blockSize),
                   Block(660, 200, blockSize, blockSize),
                   Block(880, 270, blockSize, blockSize),
                   Block(800, 110, blockSize, blockSize),
                   Block(930, 190, blockSize, blockSize),
                   lava,
                   finish] #creates actual geometry of the level
        objects.extend(coinList) #adds coins to list
        flashObjects = [Block(360, 350, blockSize, blockSize)] #flashing block
        colour = "FallingRed" #colour of falling block
        fallingObjects = [Block(296, 130, blockSize, blockSize)] #falling block
        flashing = True #boolean set to true as level has a flashing block
        falling = True #boolean set to true as level has a falling block
        if tips: #if tips are on
          text = "Caution: Unstable!" #tips for level
        
    while run: #while loop running while the game is running
      clock.tick(FPS) #clock ticks at 60fps for performance reasons
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              run = False #closes program
              break 
          if event.type == pygame.KEYDOWN:
            stopwatch.start() #starts stopwatch when user presses a key
            if event.key == pygame.K_SPACE:
              player.jump() #calls function to jump
            elif event.key == pygame.K_UP:
              player.jump() #calls function to jump

      player.loop(FPS)
      lava.loop()
      finish.loop()
      stopwatch.logTime() #loops instances of the class to update them each frame
      for coin in coinList:
        if not coin.collected: #ensures coin has not been collected
          coin.loop() #updates coins

      timeText = f"{minutes:02}:{seconds:02}.{tenths}" #stopwatch text
      textSurface = font.render(timeText, True, (0, 0, 0)) #renders text
      textRect = textSurface.get_rect(topleft=(stopwatchX, stopwatchY)) #creates a rect of the stopwatch

      if player.dead:
        player.dead = False #player has been respawned so is now alive

      if player.complete:
        times = findTimes(username) #finds individual level times
        levelTime = stopwatch.getTime() #finds current time of level
        if times[0][currentLevelNumber - 1] == 0.0: #current level
          logScore(username, False) #logs player score in the database
          logLevelScore(username, currentLevelNumber) #logs current level number
        else: #score level has score logged
          if times[0][currentLevelNumber - 1] > levelTime: #if level time beats current best
            timeDifference = times[0][currentLevelNumber - 1] - levelTime #finds difference 
            logScore(username, timeDifference) #logs player score in the database
            logLevelScore(username, currentLevelNumber) #logs current level number
        if userLevel[0][0] == currentLevelNumber: #if furthest level reached is current level
          if currentLevelNumber != 5: #total number of levels
            incrementLevel(username) #increases user level when compelete
        fade(False) #fades level
        main(levelWindow,buttonRects) #recalls main function recursively to return to level selector

      if flashing:
        if falling:
          draw(window, background, bg_image, player, objects, stopwatch, (text, text2, text3), True, flashObjects, True, fallingObjects) #draw both flashing and falling objects
        else:
          draw(window, background, bg_image, player, objects, stopwatch, (text, text2, text3), True, flashObjects, False, None) #draw flashing objects
      else:
        if falling:
          draw(window, background, bg_image, player, objects, stopwatch, (text, text2, text3), False, None, True, fallingObjects) #draw falling objects
        else:
          draw(window, background, bg_image, player, objects, stopwatch, (text, text2, text3), False, None, False, None) #draw objects

      handleMove(player, objects)
      if flashing:
        if falling:
          for obj in fallingObjects: #iterates through blocks
            obj.name = "FallingBlock" #changes object name to falling block to distinguish between the other blocks
          handleMove(player,fallingObjects, falling=True) #handles movement with falling blocks
          for obj in flashObjects: #iterates through blocks
            if obj.hidden == False:
              hidden = False
              handleMove(player,flashObjects, flash=True) #handles movement with flashing blocks only if they are not hidden
            else:
              hidden = True
          else:
            handleMove(player,objects) #else handle movement with other blocks
        else:
          for obj in flashObjects: #iterates through blocks
            if obj.hidden == False:
              hidden = False
              handleMove(player,flashObjects, flash=True) #handles movement with flashing blocks only if they are not hidden
            else:
              hidden = True
          else:
            handleMove(player,objects) #else handle movement with other blocks
      else:
        if falling:
          for obj in fallingObjects: #iterates through blocks
            obj.name = "FallingBlock" #changes object name to falling block to distinguish between the other blocks
          handleMove(player, fallingObjects, falling=True) #handles movement with falling blocks

  pygame.quit() #quits pygame when out of the while loop
  sys.exit() #exits system
      
window.mainloop() #loop running for pygame window throughout the code

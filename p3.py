# Import libraries
import RPi.GPIO as GPIO
import random
import ES2EEPROMUtils
import os
import time

# some global variables that need to change as we run the program
end_of_game = None  # set if the user wins or ends the game

# DEFINE THE PINS USED HERE
LED_value = [11, 13, 15]
LED_accuracy = 32
btn_submit = 16
btn_increase = 18
buzzer = 33
eeprom = ES2EEPROMUtils.ES2EEPROM()
current_guess = 0
value = 0
number_of_guesses = 0
pwm = None
pwm_buzzer = None

# Print the game banner
def welcome():
    os.system('clear')
    print("  _   _                 _                  _____ _            __  __ _")
    print("| \ | |               | |                / ____| |          / _|/ _| |")
    print("|  \| |_   _ _ __ ___ | |__   ___ _ __  | (___ | |__  _   _| |_| |_| | ___ ")
    print("| . ` | | | | '_ ` _ \| '_ \ / _ \ '__|  \___ \| '_ \| | | |  _|  _| |/ _ \\")
    print("| |\  | |_| | | | | | | |_) |  __/ |     ____) | | | | |_| | | | | | |  __/")
    print("|_| \_|\__,_|_| |_| |_|_.__/ \___|_|    |_____/|_| |_|\__,_|_| |_| |_|\___|")
    print("")
    print("Guess the number and immortalise your name in the High Score Hall of Fame!")

# Print the game menu
def menu():
    global end_of_game, value
    option = input("Select an option:   H - View High Scores     P - Play Game       Q - Quit\n")
    option = option.upper()
    if option == "H":
        os.system('clear')
        print("HIGH SCORES!!")
        s_count, ss = fetch_scores()
        display_scores(s_count, ss)
    elif option == "P":
        os.system('clear')
        print("Starting a new round!")
        print("Use the buttons on the Pi to make and submit your guess!")
        print("Press and hold the guess button to cancel your game")
        value = generate_number()
        print(value)
        while not end_of_game:
            pass
    elif option == "Q":
        print("Come back soon!")
        exit()
    else:
        print("Invalid option. Please select a valid one!")


def display_scores(count, raw_data):
    # print the scores to the screen in the expected format
    print("There are",eeprom.read_byte(0),"scores. Here are the top 3!")
    num = eeprom.read_byte(0)
    for i in range(1,num):
        if i > 3:
            break
        data = eeprom.read_block(i,4)
        print(chr(data[0]),chr(data[1]),chr(data[2])," took ",data[3]," guesses ",sep="")
    #print("There are {} scores. Here are the top 3!".format(count))
    # print out the scores in the required format
    pass


# Setup Pins
def setup():
    global pwm, pwm_buzzer
    GPIO.setmode(GPIO.BOARD) # Setup board mode
    # Setup regular GPIO
    GPIO.setup(LED_value[0],GPIO.OUT)
    GPIO.output(LED_value[0],0)
    GPIO.setup(LED_value[1], GPIO.OUT)
    GPIO.output(LED_value[1],0)
    GPIO.setup(LED_value[2], GPIO.OUT)
    GPIO.output(LED_value[2],0)
    GPIO.setup(LED_accuracy,GPIO.OUT)
    GPIO.output(LED_accuracy,0)
    GPIO.setup(btn_increase,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    GPIO.setup(btn_submit,GPIO.IN,pull_up_down = GPIO.PUD_UP)
    #setting up buzzer 
    GPIO.setup(buzzer,GPIO.OUT)
    # Setup PWM channels
    pwm = GPIO.PWM(LED_accuracy,1000)
    pwm.start(0)
    pwm_buzzer = GPIO.PWM(buzzer, 1)
    pwm_buzzer.start(0)

#    pwm_buzzer.ChangeDutyCycle(10)
    # Setup debouncing and callbacks
    GPIO.add_event_detect(btn_increase, GPIO.RISING,callback=btn_increase_pressed,bouncetime=300)
    GPIO.add_event_detect(btn_submit, GPIO.FALLING,callback=btn_guess_pressed,bouncetime=300)
    pass


# Load high scores
def fetch_scores():
    # get however many scores there are
    score_count = eeprom.read_byte(0)
    # Get the scores
    scores = []
    for i in range(1,score_count):
        scores.append(eeprom.read_block(i,4))
    # convert the codes back to ascii
    
    # return back the results
    return score_count, scores


# Save high scores
def save_scores():
    # fetch scores
    # include new score
    # sort
    # update total amount of scores
    # write new scores
    pass


# Generate guess number
def generate_number():
    return random.randint(0, pow(2, 3)-1)


# Increase button pressed
def btn_increase_pressed(channel):
    global current_guess
    # Increase the value shown on the LEDs
    # You can choose to have a global variable store the user's current guess, 
    # or just pull the value off the LEDs when a user makes a guess
    if current_guess == 7:
        current_guess = 0
    else:
        current_guess = current_guess+1
    update_leds()
    pass

def update_leds():
    global current_guess
    led_out = [0,0,0]
    print(current_guess)
    if current_guess == 1:
        led_out[0] = 1
    elif current_guess == 2:
        led_out[1] = 1
    elif current_guess == 3:
        led_out[0] = 1
        led_out[1] = 1
    elif current_guess == 4:
        led_out[2] = 1
    elif current_guess == 5:
        led_out[0] = 1
        led_out[2] = 1
    elif current_guess == 6:
        led_out[2] = 1
        led_out[1] = 1
    elif current_guess == 7:
        led_out[0] = 1
        led_out[1] = 1
        led_out[2] = 1
    else:
        current_guess = 0
	        
    
    GPIO.output(LED_value[0],led_out[0])
    GPIO.output(LED_value[1],led_out[1])
    GPIO.output(LED_value[2],led_out[2])

# Guess button
def btn_guess_pressed(channel):
    global current_guess, value,number_of_guesses, pwm
    # If they've pressed and held the button, clear up the GPIO and take them back to the menu screen
    # Compare the actual value with the user value displayed on the LEDs
    if current_guess == value:
        GPIO.output(buzzer,0)
        pwm_buzzer.ChangeDutyCycle(0)
        GPIO.output(LED_accuracy,0)
        current_guess= 0
        update_leds()
        print("Guess corrent!!")
        name = input("Please enter your name \n")
        #getting the block to start from
        start_block = eeprom.read_byte(0)
        block = start_block
        if (start_block == 0):
            block = 1
        eeprom.write_block(block,[ord(name[0]),ord(name[1]),ord(name[2]),number_of_guesses])
        #increment start block
        eeprom.write_byte(0,start_block+1)
        #sorting
        score_tupple = []
        for i in range (1,start_block+1):
            score_tupple.append(eeprom.read_block(i,4))
        score_sorted = sorted(score_tupple,key = lambda score: score[3])
        for i in range(len(score_sorted)):
            eeprom.write_block(i+1,score_sorted[i])
        GPIO.cleanup()
        menu()
    else:
        trigger_buzzer()
        pwm.ChangeDutyCycle(accuracy_leds())
        GPIO.output(LED_accuracy,1)
        number_of_guesses = number_of_guesses + 1
        print("Guess wrong, please try again.")
    # Change the PWM LED
    # if it's close enough, adjust the buzzer
    # if it's an exact guess:
    # - Disable LEDs and Buzzer
    # - tell the user and prompt them for a name
    # - fetch all the scores
    # - add the new score
    # - sort the scores
    # - Store the scores back to the EEPROM, being sure to update the score count
    pass


# LED Brightness
def accuracy_leds():
    global value, current_guess
    accuracy = abs(((value - current_guess)/(value+1)*100))
    if accuracy > 100:
        accuracy = 95
    return 100 - accuracy
    # Set the brightness of the LED based on how close the guess is to the answer
    # - The % brightness should be directly proportional to the % "closeness"
    # - For example if the answer is 6 and a user guesses 4, the brightness should be at 4/6*100 = 66%
    # - If they guessed 7, the brightness would be at ((8-7)/(8-6)*100 = 50%
   

# Sound Buzzer
def trigger_buzzer():
    # The buzzer operates differently from the LED
    # While we want the brightness of the LED to change(duty cycle), we want the frequency of the buzzer to change
    # The buzzer duty cycle should be left at 50%
    # If the user is off by an absolute value of 3, the buzzer should sound once every second
    # If the user is off by an absolute value of 2, the buzzer should sound twice every second
    # If the user is off by an absolute value of 1, the buzzer should sound 4 times a second
    if (abs(value - current_guess == 3)):
        pwm_buzzer.ChangeFrequency(1)
    elif (abs(value - current_guess == 2)):
        pwm_buzzer.ChangeFrequency(2)
    elif (abs(value - current_guess == 1)):
        pwm_buzzer.ChangeFrequency(4)
    else:
        return
    pwm_buzzer.ChangeDutyCycle(50)
    time.sleep(0.5)
    GPIO.output(buzzer,1)
    pass


if __name__ == "__main__":
    try:
        # Call setup function
        setup()
        welcome()
        while True:
            menu()
            pass
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()

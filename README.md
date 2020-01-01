# Integrating physical devices with IOTA — Car-IOTA Part 2

## The 13th part in a series of beginner tutorials on integrating physical devices with the IOTA protocol

![img](https://miro.medium.com/max/2448/1*ymph4TDuy-_VBX1Zw_c-yA.jpeg)

------

## Introduction

This is the 13th part in a series of beginner tutorials where we explore integrating physical devices with the IOTA protocol. If you have been following the IOTA project for some time you may have heard about strange ideas such as “cars having there own wallets” or “cars paying for there own services”. While this may sound intangible and futuristic, it’s basically the idea we will be taking on in this tutorial.

------

## The use case

As you may remember, we ended the [previous tutorial](https://medium.com/coinmonks/integrating-physical-devices-with-iota-car-iota-part-1-f63ed0a0ea1d) by pointing out some problems related to the centralized nature of the ALPR approach, where a centralized entity (aka, the hotel-owner) would have to have control over the seeds used when performing the payment transactions. The great thing about this approach is that the car itself does not require any new electronics, (as the infrastructure (parking facility) takes care all the payment transactions). While this might be acceptable for some local use-cases, it would not be very practical if we wanted to implement our parking payment system on a truly decentralized and global scale.

In this tutorial we will try and deal with this problem by simply turning everything up-side down. Instead of having the parking facility manage the payment transaction, the car itself will do all the work. This way the IOTA seed never leaves the car (seed) owner.

------

## Data exchange

The first thing we need to deal with when taking on this problem is that we need some type of data exchange between the infrastructure (parking facility) and the car, so that the car knows what payment address to use when sending the payment transaction. I’m guessing there are multiple wireless data protocols and technologies that could be used for this purpose (radio, blue-tooth, RFID etc.) but I felt they all had some disadvantages that was not optimal for this particular use-case. After puzzling over this problem for a while i decided to go with a simple, yet familiar technology that you probably use every day when sitting in front of your television, namely *Infrared communication*, or IR for short.

------

## About IR and IR communication

IR communication is based on light pulses being sent from an IR transmitter to an IR receiver. To prevent interference from “normal” light, IR uses light in the infrared light spectrum, hens the name *Infrared*. As the technology suggest, IR is a binary communication protocol where the length in time between each individual light-pulse determines if the data being sent is a 0 or 1. Different implementations of IR communication uses different logic with respect to pulse length, time between pulses, the number of pulses in a data packet etc. In this tutorial we will be using a particular IR protocol called [NEC](https://techdocs.altium.com/display/FPGA/NEC+Infrared+Transmission+Protocol). The NEC protocol is a 32 bit protocol that allows us to send 32 bits of data (0 and 1) in one data packet. As it takes 8 bits to define a byte, the NEC protocol allows us to transfer 4 bytes of data in each data packet. As the typical IOTA address consist of 90 bytes (including the checksum), it would then take 23 NEC data packets to transfer the complete IOTA address.

------

## The components

The main components used in this tutorial is the IR transmitter and IR receiver. For my project I’m using the popular NE555 IR modules. They often come in a pair and you should be able to get them both of ebay for a couple bucks.

![img](https://miro.medium.com/max/300/0*uma9UXmBCcZ17njm.jpg)

Beside the IR modules them selves, we also need to hook up each module to a micro-controller that will take care of the logic with respect to sending and receiving data.

**The receiver controller**
As the receiver micro-controller for this project i decided to use my Raspberry PI together with the PyOTA library. The main reason being that the receiver will not only be used to manage IR communication, it will also have to take care of any interaction with the IOTA tangle.

*Note!
There is now an* [*IOTA C client library*](https://github.com/iotaledger/iota.c) *available, capable of communicating with the IOTA tangle, if you prefer using a different micro-controller as the receiver controller, such as the ESP32.*

**The transmitter controller**
The IR transmitter controller is basically just telling the IR transmitter module what data to send and requires no network or IOTA capabilities. For this reason i used the cheapest and simplest micro-controller I had laying around. My trusted **Arduino UNO**.

![img](https://miro.medium.com/max/458/0*NOrBZiNhtHHMzGd1.jpg)

------

## Wiring

Now, let’s take a look at how each module is connected to its respective controller.

Here is how the IR receiver module is hooked up to the Raspberry PI board

![img](https://miro.medium.com/max/975/1*k2NWAE0y58nYnQ2cDejPgw.png)

And here is how the IR transmitter module is hooked up to the Arduino UNO board.

![img](https://miro.medium.com/max/1659/0*g5mZQEMlM4vT3lE9.png)

------

## How it works

Before moving on to the code used for this project, lets take a step back and look at the general idea behind the concept proposed in this tutorial and how it woks.

Imagine the receiver part of the project (IR receiver module and controller) is placed inside the car, constantly monitoring for incoming IR data from its surroundings. At the same time, imagine the IR transmitter placed at the entrance of a parking facility constantly publishing its IOTA payment address.

As the car approaches the parking facility, it starts picking up the IR signals from the transmitter. As soon as the receiver (car) has validated the received data as a valid IOTA payment address, it automatically executes the payment as it enters the facility.

*Note!*
*In a real life scenario, some type of approval from the driver would probably be required before the the payment is being executed.*

*Note!*
*Additional data besides the IOTA payment address itself could be added to the data transmission to include metadata such as the name of the parking facility etc.*

------

## The Code

Next, let’s have a look at the code use for this project.

**Transmitter side**
Let’s start with the Arduino code being run on the transmitter side.

First thing you should notice is that we are using an external Arduino library called **IRemote** when sending data from the IR transmitter module. You can download the IRemote library as a zip file [here](https://www.arduinolibraries.info/libraries/i-rremote). To install the IRemote library, select **Sketch->Include Library->Add .ZIP Library** inside the Arduino IDE

Secondly, we need to specify the IOTA address that are to be published by the transmitter. This data is stored in the msgArray[] variable where each element in the array consist of four bytes.

Notice that the irsend() function requires the data to be specified in a hexadecimal format, so when setting up msgArray[] variable, we first need to convert our IOTA address to a hexadecimal format.

*Note!I made a simple Python script to help converting an existing IOTA address to a format acceptable by our Arduino sketch, you will find a link to this script* [*here*](https://gist.github.com/huggre/991259a162c3c3941daa577a8a24c276)*.*

Notice that before we start sending the actual iota address data, we start by sending a 0x30303030 message to let the receiver know where the address data sequence begins (and ends)

Finally, there is a variable (delay_time) that can be used to control the time between each individual IR message being sent. A smaller delay_time leads to faster data transfer.

*Note!I tested using a delay_time as low as 50 milliseconds with success. This would give us a total transfer time for the complete IOTA address to 50x23=1,1150 milliseconds.*

And here is our transmitter Arduino code:

```c++
// Include the IRemote library
#include <IRremote.h>
IRsend irsend;

// A hexadecimal representation of the IOTA payment address
// where each element in the array consist of four characters
const int long msgArray[] = {0x47545a55,0x48515350,0x52415143,0x54535142,0x5a45454d,0x4c5a5051,0x55504141,0x394c504c,0x4757434b,0x464e4556,0x4b42494e,0x5845585a,0x52414356,0x4b4b4b43,0x59505750,0x4b483941,0x574c474a,0x48504c4f,0x5a5a4f59,0x54414c41,0x574f5653,0x494a4959,0x565a};

// Defines the delay in milliseconds between each IR message
const int delay_time = 500;
                             
void setup()  
{  
}  
                               
void loop()  
{  

  // Send start sequence message...
  irsend.sendNEC(0x30303030, 32);

  delay(delay_time);

  // Loop message elements
  for (int i=0; i<sizeof msgArray/sizeof msgArray[0]; i++) {

    // Send IR message element
    irsend.sendNEC(msgArray[i], 32);

    delay(delay_time);
    
  }

} 
```


The source code can be downloaded from [here](https://gist.github.com/huggre/8b00b5cc3681078aa8dba9367293f19c)

**Receiver side**
Now lets move on to the Python code being run on the receiver side.

I’m not going into details here as the code itself is pretty well documented. However, i will give you a broad overview of whats going on.

First, we start listening for binary data is they come in through the IR receiver module. As we know the sender follows the NEC protocol (ref. irsend.sendNEC() from our Arduino sketch), we analyze the data stream by measuring time between each individual pulse to determine if the data is a 0 or 1. Notice that the NEC protocol also specifies the beginning and end of each message. Next, we convert the binary data to hexadecimal, before again converting it to bytes. If the received byte data equals 0000, we know a new sequence of IOTA address data is coming. As new address data is coming in we simply append the new byte string to the previous byte string until the next 0000 message comes. We then check the complete string to see if it is a valid IOTA address. If yes, we execute the IOTA value transaction.

And here is our receiver Python code:

```python
#Import some libraries
import RPi.GPIO as GPIO
from datetime import datetime

# Import the PyOTA library
import iota
from iota import Address

# Input pin used by IR reciever 
pin = 12

# Set up GPIO board
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN)

# Attribute used to store IOTA reciever address
addr = ''

# Price of the parking service (10 IOTA)
price = 10

# IOTA seed used for payment transaction
# Replace with your own seed
seed = b"YOUR9SEED9GOES9HERE......"

# Car plate number stored as tag in the IOTA payment transaction  
plate_id = 'PN 12345'

# URL to IOTA fullnode used when interacting with the Tangle
iotaNode = "https://nodes.thetangle.org:443"

# Function to recieve binary data from IR transmitter
def getBinary():
	# Internal vars
	num1s = 0 # Number of consecutive 1s read
	binary = 1 # The bianry value
	command = [] # The list to store pulse times in
	previousValue = 0 # The last value
	value = GPIO.input(pin) # The current value
	
	# Waits for the sensor to pull pin low
	while value:
		value = GPIO.input(pin)
		
	# Records start time
	startTime = datetime.now()
	
	while True:
		# If change detected in value
		if previousValue != value:
			now = datetime.now()
			pulseTime = now - startTime # Calculate the time of pulse
			startTime = now # Reset start time
			command.append((previousValue, pulseTime.microseconds)) # Store recorded data
			
		# Updates consecutive 1s variable
		if value:
			num1s += 1
		else:
			num1s = 0
		
		# Breaks program when the amount of 1s surpasses 10000
		if num1s > 10000:
			break
			
		# Re-reads pin
		previousValue = value
		value = GPIO.input(pin)
		
	# Converts times to binary
	for (typ, tme) in command:
		if typ == 1: # If looking at rest period
			if tme > 1000: # If pulse greater than 1000us
				binary = binary *10 +1 # Must be 1
			else:
				binary *= 10 # Must be 0
			
	if len(str(binary)) > 34: #Sometimes, there is some stray characters
		binary = int(str(binary)[:34])
		
	return binary
	
# Function to convert binary value to hex
def convertHex(binaryValue):
	tmpB2 = int(str(binaryValue),2) # Tempary propper base 2
	return hex(tmpB2)[3:-1] # Remove "0x3" and "L" from string
    
# Function to check that the recieved address is a valid IOTA address
def check_addr(str_addr):
    
    # Remove unwanted ascii characters from string
    str_addr = filter(str.isalnum, str_addr)

    # Print the address to be checked
    print('Address to check: ' + str_addr)
    
    # Try and convert the string to bytestring
    try:
        byte_addr = str_addr.encode()
    except:
        print('Error encoding address to bytestring')
        return False
    
    # Check if address is correct length
    if len(byte_addr) != 90:
        print('Not correct length')
        return False
    
    # Check if address is a valid IOTA address
    try:
        Adr2 = iota.Address(byte_addr)
    except:
        print('Not valid IOTA address')
        return False       
    
    # Check if address has a correct checksum
    result = Adr2.is_checksum_valid()

    if result == False:
        print('Invalid checksum')
        return False
    else:
        return byte_addr
    
       
# Function for sending the IOTA value transaction
def send_transaction(hotel_address, price, seed, plate_id):
    
    # Define api object
    api = iota.Iota(iotaNode, seed=seed)

    # Create transaction object
    tx1 = iota.ProposedTransaction( address = iota.Address(hotel_address), message = None, tag = iota.Tag(iota.TryteString.from_unicode(plate_id)), value = price)

    # Send transaction to tangle
    print("\nSending transaction... Please wait...")
    SentBundle = api.send_transfer(depth=3,transfers=[tx1], inputs=None, change_address=None, min_weight_magnitude=14)       

    # Display transaction sent confirmation message
    print("\nTransaction sent...")



# Get incoming IR data 
while True:
        try:
            inData = convertHex(getBinary())
            print('Recieving data ' + inData.decode("hex"))
            if inData.decode("hex") == '0000':
                byte_addr = check_addr(addr)
                if check_addr(addr) != False:
                    print('Address OK, sending transaction...')
                    send_transaction(byte_addr, price, seed, plate_id)
                addr=''
                print('Start sequence...')
            else:
                addr = addr + inData.decode("hex")
           
        except (KeyboardInterrupt, SystemExit):
            raise

        except:
            print("An exception occurred")

```


The source code can be downloaded from [here](https://gist.github.com/huggre/262f61c829c5e890c2ba7dd2caf0648a)

## Running the project

To run the project you should start by connecting your IR transmitter module to your Arduino UNO. Then upload the Aduino sketch from the previous section to the board using the [Arduino IDE](https://www.arduino.cc/en/main/software).

*Note!*
*Make sure you have installed the IRemote library before compiling and uploading the code.*

If you have connected the IR receiver module to your Raspberry PI you should now see a small LED start blinking on the module every 500 millisecond. This indicates that your transmitter is working properly.

Next, download the Python script from the previous section and save it on your Raspberry PI as **car-iota-p2.py**

To execute the Python script, simply start a new terminal window on your Raspberry PI, navigate to the folder where you saved the script and type:

**python car-iota-p2.py**

You should now see the Python code being executed in the terminal window, displaying data as it is received from the transmitter.

*Note!
Remember to update the* **car-iota-p2.py** *file with a valid seed (with a positive balance) to be used when publishing value transactions to the IOTA tangle.*

------

## Donations

If you like this tutorial and want me to continue making others, feel free to make a small donation to the IOTA address shown below.

![img](https://miro.medium.com/max/400/0*_V4-ghDTlSeP469e.png)

> *GTZUHQSPRAQCTSQBZEEMLZPQUPAA9LPLGWCKFNEVKBINXEXZRACVKKKCYPWPKH9AWLGJHPLOZZOYTALAWOVSIJIYVZ*

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


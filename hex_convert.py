# Imports the textrwap library
from textwrap import wrap

# Replace with your own IOTA payment address
sample = 'GTZUHQSPRAQCTSQBZEEMLZPQUPAA9LPLGWCKFNEVKBINXEXZRACVKKKCYPWPKH9AWLGJHPLOZZOYTALAWOVSIJIYVZ'

# Create a list with 4 characters in each element
mylist = wrap(sample,4)

result = ''

# Convert each element in the list to hex separated by ,
for i in mylist:
    result=result + '0x' + i.encode("utf-8").hex() + ','

# Remove last , from string
result=result[:-1]

# Append the curly brackets 
result = '{' + result + '}'

# Print the resulting string
print(result)
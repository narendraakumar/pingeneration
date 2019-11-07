# from pinterest import Pinterest
import json

from pinterest import Pinterest

with open("creds.json" ,"r") as f:
    j_obj = json.load(f)

pinterest = Pinterest(username_or_email=j_obj['username_or_email'], password=j_obj['password'])
# Login to pinterest site, if 'ok' return True otherwise return False
logged_in = pinterest.login()
print(logged_in)

# Get all boards of logged in user
boards = pinterest.boards()

# Create new board, it also return new board data if creation was successful
pinterest.create_board(name='Board name', description='Description')

# Follow a board
pinterest.follow_board(board_id='657384945546806337', board_url='/cvhautt/animal/')

# Follow a user
pinterest.follow_user(user_id='657385014266199005', username='cvhautt')

# Create pin from an image url
pin = pinterest.pin(
    board_id='657384945546806337',
    image_url='your_image_url',
    description='your_description (*optional)',
    link='your_link (*optional)')

# Create pin by uploading an image from your computer
uploaded_pin = pinterest.upload_pin(
    board_id='657384945546806337',
    image_file='full_path_to_your_image',
    description='your_description (*optional)')

# Save a pin to your board (known as Save button on Pinterest site)
pinterest.repin(board_id='657385014266199005', pin_id='pin_id')

# Delete a pin
pinterest.delete_pin(pin_id='your_pin_id')

# Comment on a pin
cmt = pinterest.comment(pin_id='your_pin_id', text='your_comment_text')

# Delete a comment from pin
pinterest.delete_comment(pin_id='your_pin_id', comment_id='your_comment_id')

# Invite a person to join to your board
pinterest.invite(board_id='your_board_id', board_url='your_board_url', user_id='user_id')

# Search data on Pinterest site
boards = pinterest.search_boards(query='Some query')
pins = pinterest.search_pins(query='Some query')
users = pinterest.search_users(query='Some query')

# You can also get next page from search result by passing next_page=True to search operations above.
# Exp:
boards = pinterest.search_boards(query='Some query', next_page=True)
pins = pinterest.search_pins(query='Some query',next_page=True)
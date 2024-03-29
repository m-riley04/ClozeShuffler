from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from aqt.qt import *
import random

def shuffleTaggedInDeck(card):
    """
    Description:
        A command that attaches to the "Tagged In Deck" menu option for the shuffler. Does a sequence of actions:\\
            1. Accesses the current deck and cards\\
            2. Accesses the front and back fields of each cards\\
            3. Shuffles the accessed fields (if any Cloze fields exist)\\
    
    Arguments:
        None
    
    Returns:
        None
    """
    # Get a list of the current cards
    ids = get_current_deck_tagged_cards()
    
    # Call on the helper function to do the work
    cardCount = _shuffleHelper(ids)
        
    # Tell the user the process is finished
    if (mw.state != "review"):
        message = "Shuffled " + str(cardCount) + " 'shuffle' tagged cards in the current deck!"
        showInfo(message)

def shuffleTaggedEverywhere(card):
    """
    Description:
        A command that attaches to the "Tagged Everywhere" menu option for the shuffler. Does a sequence of actions:\\
            1. Accesses the current deck and cards\\
            2. Accesses the front and back fields of each cards\\
            3. Shuffles the accessed fields (if any Cloze fields exist)\\
    
    Arguments:
        None
    
    Returns:
        None
    """
    # Get a list of the current cards
    ids = get_tagged_cards()
    
    # Call on the helper function to do the work
    cardCount = _shuffleHelper(ids)
        
    # Tell the user the process is finished
    if (mw.state != "review"):
        message = "Shuffled " + str(cardCount) + " 'shuffle' tagged cards!"
        showInfo(message)

def shuffleInDeck(card):
    """
    Description:
        A command that attaches to the "In Deck" menu option for the shuffler.  Does a sequence of actions:\\
            1. Accesses the current deck and cards\\
            2. Accesses the front and back fields of each cards\\
            3. Shuffles the accessed fields (if any Cloze fields exist)\\
    
    Arguments:
        None
    
    Returns:
        None
    """
    # Get a list of the current cards
    ids = get_current_cards()
    
    # Call on the helper function to do the work
    cardCount = _shuffleHelper(ids)
        
    # Tell the user the process is finished
    if (mw.state != "review"):
        message = "Shuffled " + str(cardCount) + " cards in the current deck!"
        showInfo(message)
    
def shuffleEverywhere(card):
    """
    WARNING: Quite expensive (O^2)
        
    Description:
        A command that attaches to the "Everywhere" menu option for the shuffler. Does a sequence of actions:\\
            1. Accesses the current deck and cards\\
            2. Accesses the front and back fields of each cards\\
            3. Shuffles the accessed fields (if any Cloze fields exist)
        
    Arguments:
        None
    
    Returns:
        None
    """
    # Get a list of all the deck names
    decks = mw.col.decks.all_names()
    
    # Iterate through all the decks
    cardCount = 0
    for deck in decks:
        
        ids = get_deck_cards(deck)
        
        # Call on the helper function to do the work
        cardCount += _shuffleHelper(ids)
        
    # Tell the user the process is finished
    if (mw.state != "review"):
        message = "Shuffled " + str(cardCount) + " cards!"
        showInfo(message)

def _shuffleHelper(ids:list) -> int:
    """
    Description:
        The helper class for shuffling. Takes a list of Card ids and shuffles the Cloze within them.
    
    Arguments:
        ids (list): a list of cards
    
    Returns:
        int: the number of cards shuffled
    """
    # Iterate through the card IDs
    counter = 0
    for id in ids:
        # Initialize the card object
        card = mw.col.get_card(id)
        
        # Get the front and back text
        front = card.note().fields[0]
        back = card.note().fields[1]

        # Shuffle the card
        newFront = _shuffle(front)
        
        # Show the user the shuffled card (DEBUG)
        #showInfo(newFront, None, None, "info", "Anki", "plain")
        
        # Write the data to the card
        card.note().fields[0] = newFront
        mw.col.update_note(card.note())
        
        # Increment the counter
        counter += 1
        
    # Return the shuffled card count
    return counter

def _shuffle(text:str) -> str:
    """
    Definition: 
        Shuffles the Cloze answers of a card in a random order.
        Determines what lines to shuffle based on whether it finds Cloze formatting in the line.
        If the first line does not have Cloze formatting, it will stay the first line. After that,
        if any Cloze lines are detected, the following lines will be shuffled with it. 
    
    Args:
        text (str): The field/card text to shuffle
    
    Returns: 
        str: The original card text, but with shuffled Cloze lines
    """
    #=== Add temporary line breaks to certain HTML elements (ul, li, and br)
    replacedText = insert_into_string_at_query(text, "\n", "<ul>")
    replacedText = insert_into_string_at_query(replacedText, "\n", "</ul>")
    replacedText = insert_into_string_at_query(replacedText, "\n", "</li>")
    replacedText = insert_into_string_at_query(replacedText, "\n", "<br>")
    
    # Break the text into lines
    lines = lines_from_string(replacedText, "\n")
    
    # Construct the final string piece by piece in 3 parts
    firstLines = []
    ClozeLines = []
    lastLines = []
    atCloze = False
    pastCloze = False
    for line in lines:
        # Check for </ul>
        if ("</ul>" in line):
            pastCloze = True
            
        # If the Cloze part is done, append the rest to the last part
        if (pastCloze):
            lastLines.append(line)
            continue
        
        # Check for first lines of text
        if (not atCloze and not isCloze(line)):
            # If there's no Cloze formatting and Cloze hasn't been found already, append the text to the final lines 
            firstLines.append(line)
            continue
        atCloze = True
        
        # Append the line to the list of ClozeLines
        ClozeLines.append(line)
        
    # Randomize the Cloze lines
    random.seed()
    random.shuffle(ClozeLines)
    
    # Connect the 3 line parts together
    firstLines += ClozeLines
    firstLines += lastLines
    
    # Reconnect the lines back into a string
    finalString = "".join(firstLines)
    
    return finalString

def isCloze(text:str) -> bool:
    """
    Description:
        Checks whether or not a card face has Cloze text formatting.
    
    Args:
        text (str): The text to check for any Cloze formatting
    
    Returns: 
        - bool
    """
    if ("{{c" in text and "}}" in text):
        return True
    return False

def insert_into_string(string:str, substr:str, index:int):
    """
    Description:
        Inserts a given string into another string at a given index.

    Args:
        string (str): String to modify
        substr (str): String to insert
        index (int): Index of where to insert

    Returns:
        str: A new string with the inserted text within
    """
    return string[:index] + substr + string[index:]
    
def insert_into_string_at_query(string:str, substr:str, query:str):
    """
    Description:
        Inserts a given string into another string after a given text query, possibly multiple times

    Arguments:
        string (str): String to modify
        substr (str): Text to insert
        query (str): What piece of text to insert after

    Returns:
        str: A new string with the inserted text within
    """
    # Initialize local variables
    _index = 0
    _string = string
    _loops = string.count(query)
    
    # Loop through counting the number of times the query is found
    for i in range(_loops):
        # Find the index of the next list element ending
        _index = _string.find(query, _index+1)
        
        # Check for error
        if (_index == -1):
            # Send message to user
            msg = "ERROR: There was an error when inserting at the query '" + query + "'."
            showInfo(msg)
            
            # Return original, untouched string
            return string
        
        # Insert the delimeter into the temporary string
        _string = insert_into_string(_string, substr, _index+len(query))
    return _string
    
def lines_from_string(string:str, delimeter:str="\n") -> list[str]:
    """
    Description:
        Gets a list of strings that represent the lines of the inputted string. 
        Lines are determined by line breaks, or an optional 'delimeter' parameter.
    
    Arguments:
        string (str): The string to take the lines from
        delimeter (str): The separator that defines what a "line" is
    
    Returns: 
        list[str]: A list of strings that represent each line of the given text string
    """
    return string.split(delimeter)

def get_deck_cards(deckName:str) -> list:
    """
    Description:
        Gets all the cards within a deck
    
    Arguments:
        deckName (str): The deck's name
        
    Returns:
        list: A list of the cards within the deck of name [deckName] 
    """
    # Form the search tag for cards without spaces
    searchTag = "deck:" + deckName
    searchTag = searchTag.replace(" ", "_")
    
    # Get a list of card IDs
    return mw.col.find_cards(searchTag)

def get_current_cards() -> list:
    """
    Description:
        Gets all the cards within the currently selected/studying deck
    
    Arguments:
        None
        
    Returns:
        list: A list of the cards within the current deck
    """
    # Get the current deck and name
    deck = mw.col.decks.current()
    deckName = deck.get("name")
    
    # Return the list of cards from helper function
    return get_deck_cards(deckName)

def get_current_deck_tagged_cards() -> list:
    """
    Description:
        Gets all the cards tagged with "shuffle" within the current deck
    
    Arguments:
        None
        
    Returns:
        list: A list of the cards with a tag "shuffle" from the current deck
    """
    # Get the current deck and name
    deck = mw.col.decks.current()
    deckName = deck.get("name")
    
    query = "tag:shuffle, deck:" + deckName
    return mw.col.find_cards("tag:shuffle")    

def get_tagged_cards() -> list:
    """
    Description:
        Gets all the cards tagged with "shuffle"
    
    Arguments:
        None
        
    Returns:
        list: A list of the cards with a tag "shuffle"
    """
    return mw.col.find_cards("tag:shuffle")
    
def toggled_autoshuffle():
    """
    Description:
        The command for when the "Autoshuffle" action button is toggled
    
    Arguments:
        None
        
    Returns:
        None
    """
    if (not action_autoshuffle.isChecked()):
        config["autoshuffle"] = False
        autoshuffle = False
        gui_hooks.reviewer_did_show_answer.remove(shuffleMethods[autoshuffle_method])
    else:
        config["autoshuffle"] = True
        autoshuffle = True
        gui_hooks.reviewer_did_show_answer.append(shuffleMethods[autoshuffle_method])
        
    mw.addonManager.writeConfig(__name__, config)
    
# Initialize variables
shuffleMethods = [shuffleTaggedInDeck, shuffleTaggedEverywhere, shuffleInDeck, shuffleEverywhere]

# Fetch the config
config = mw.addonManager.getConfig(__name__)
autoshuffle = config["autoshuffle"]
autoshuffle_method = config["autoshuffle_method"]
    
# Create the menu action for the plugin
group                   = QMenu("ClozeShuffler")
group_methods           = QMenu("Shuffle")
action_taggedDeck       = QAction("Tagged In Deck", mw)
action_taggedEverywhere = QAction("Tagged Everywhere", mw)
action_deck             = QAction("In Deck", mw)
action_everywhere       = QAction("Everywhere", mw)
action_autoshuffle      = QAction("Autoshuffle", mw, checkable=True)

# Set up autoshuffling
if (autoshuffle):
    gui_hooks.reviewer_did_show_answer.append(shuffleMethods[autoshuffle_method])
action_autoshuffle.setChecked(autoshuffle)

# Add all the menu actions to the new menu
group_methods.addAction(action_taggedDeck)
group_methods.addAction(action_taggedEverywhere)
group_methods.addAction(action_deck)
group_methods.addAction(action_everywhere)
group.addMenu(group_methods)

# Connect the signal of "triggered" to the "run" function
qconnect(action_taggedDeck.triggered, shuffleTaggedInDeck)
qconnect(action_taggedEverywhere.triggered, shuffleTaggedEverywhere)
qconnect(action_deck.triggered, shuffleInDeck)
qconnect(action_everywhere.triggered, shuffleEverywhere)
qconnect(action_autoshuffle.triggered, toggled_autoshuffle)

# Add the "Shuffle" group to the tools dropdown menu
#mw.form.menuTools.addSection("ClozeShuffler")
#mw.form.menubar.addSection("ClozeShuffler")
group.addAction(action_autoshuffle)
mw.form.menubar.addMenu(group)
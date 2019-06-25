import requests


"""
send message
    https://core.telegram.org/bots/api/#sendmessage
keyboard
    Field       Type                                Description
    keyboard 	Array of Array of KeyboardButton 	Array of button rows, each represented by an Array of KeyboardButton objects
    
    keyboard buttons
        Field               Type        Description
        text 	            String 	    Text of the button. If none of the optional fields are used, it will be sent as a message when the button is pressed
        request_contact 	Boolean 	Optional. If True, the user's phone number will be sent as a contact when the button is pressed. Available in private chats only
        request_location 	Boolean 	Optional. If True, the user's current location will be sent when the button is pressed. Available in private chats only
        
    
inline keyboard markup
    
    Field               Type                                        Description
    inline_keyboard 	Array of Array of InlineKeyboardButton 	    Array of button rows, each represented by an Array
                                                                    of InlineKeyboardButton objects

    inline keyboard buttons
    
        Field               Type            Description
        text 	                String  	Label text on the button
        
        url 	                String 	    Optional. HTTP or tg:// url to be opened when button is pressed
        
        login_url 	            LoginUrl 	Optional. An HTTP URL used to automatically authorize the user. 
                                            Can be used as a replacement for the Telegram Login Widget.
                                            
        callback_data 	        String 	    Optional. Data to be sent in a callback query to the bot when 
                                            button is pressed, 1-64 bytes
                                            
        switch_inline_query 	String 	    Optional. If set, pressing the button will prompt the user to 
                                            select one of their chats, open that chat and insert the bot‘s 
                                            username and the specified inline query in the input field. Can be
                                            empty, in which case just the bot’s username will be inserted.
    
    
    
callback buttons(in fact the same thing like above)
"""
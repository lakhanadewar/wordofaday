import requests
import json

def get_random_word():
    # This API doesn't have a direct 'random word' endpoint.
    # A common workaround is to pick a random letter and search for words starting with it,
    # or use a different API for random words and then use dictionaryapi.dev for definitions.
    # For simplicity, let's start with a fixed word for now and then enhance it.
    # Or, we can use a word list and pick a random word from it.
    # Let's try to get a word from a public word list first.
    try:
        response = requests.get("https://random-word-api.herokuapp.com/word?number=1")
        response.raise_for_status() # Raise an exception for HTTP errors
        word = response.json()[0]
        return word
    except requests.exceptions.RequestException as e:
        print(f"Error fetching random word: {e}")
        return None

def get_word_details(word):
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # Raise an exception for HTTP errors
        data = response.json()
        
        if isinstance(data, dict) and data.get('title') == 'No Definitions Found':
            print(f"No definitions found for '{word}'.")
            return None

        # Extracting definition and example sentence
        definition = "N/A"
        example = "N/A"
        
        if data and isinstance(data, list) and len(data) > 0:
            meanings = data[0].get('meanings')
            if meanings:
                for meaning in meanings:
                    definitions = meaning.get('definitions')
                    if definitions:
                        definition = definitions[0].get('definition', 'N/A')
                        example = definitions[0].get('example', 'N/A')
                        break # Take the first definition and example found
        
        return {
            "word": word,
            "definition": definition,
            "example": example
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching word details for '{word}': {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON for '{word}'. Response was: {response.text}")
        return None

def draft_message(word_details):
    if not word_details:
        return "Could not retrieve word details."
    
    message = f"Word of the Day: {word_details['word']}\n"
    message += f"Meaning: {word_details['definition']}\n"
    message += f"Example: {word_details['example']}\n"
    return message

if __name__ == "__main__":
    word = None
    word_details = None
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        word = get_random_word()
        if word:
            word_details = get_word_details(word)
            if word_details and word_details['definition'] != 'N/A':
                break
            else:
                print(f"Retrying with a new word as no valid definition was found for '{word}'.")
        else:
            print("Failed to get a random word. Retrying...")
        attempts += 1

    if word_details and word_details['definition'] != 'N/A':
        message_content = draft_message(word_details)
        with open("message.txt", "w") as f:
            f.write(message_content)
        print("Message drafted and saved to message.txt")
    else:
        message_content = "Failed to retrieve a unique word and its details after multiple attempts."
        with open("message.txt", "w") as f:
            f.write(message_content)
        print(message_content)



import ebooklib
from ebooklib import epub
import openai
import os
from bs4 import BeautifulSoup

def convert_epub_to_html(input_file, output_file):
    try:
        # Load the epub file
        book = epub.read_epub(input_file)
    except epub.EpubException as e:
        print(f"Error loading EPUB file: {e}")
        return
    
    # Create a new HTML file
    with open(output_file, 'w', encoding='utf-8-sig') as html_file:  # Use 'utf-8-sig' to include BOM
        # Iterate through each item in the epub
        for item in book.get_items():
            # Check if the item is a document
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Get the content of the document
                content = item.get_body_content()
                
                # Decode the content to ensure proper character handling
                decoded_content = content.decode('utf-8', errors='replace')
                
                # Parse the content with BeautifulSoup
                soup = BeautifulSoup(decoded_content, 'html.parser')
                
                # Write the prettified HTML to the output file
                html_file.write(soup.prettify())


def read_epub(input_file,output_file):
      # Load the epub file
    book = epub.read_epub(input_file)
    
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            print(text)
            

def translate_epub(input_file, output_file):
    # Load the epub file
    book = epub.read_epub(input_file)
    
    # Set up OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_body_content()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()

            # Translate the text using OpenAI API with the latest model
            client = openai.OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY")  # This is the default and can be omitted
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "developer", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Translate the following text to Chinese:\n\n{text}"}
                ],
                model="gpt-4o-mini"
            )
            translated_text = chat_completion.choices[0].message.content.strip()
            
            print(translated_text)

            # Replace the original text with the translated text
            for tag in soup.find_all(text=True):
                tag.replace_with(translated_text)

            # Update the item content with translated text
            item.set_content(str(soup).encode('utf-8'))
            
    # Write the translated content to a new epub file
    epub.write_epub(output_file, book, {})





def epub_token_cost(total_tokens):
        # Calculate the cost for GPT-4
    # Assuming the cost is $2.50 per 1M input tokens, $1.25 per 1M cached input tokens, and $10.00 per 1M output tokens
    # cost_per_1M_input_tokens = 2.50
    # cost_per_1M_cached_input_tokens = 1.25
    # cost_per_1M_output_tokens = 10.00

    # 另外，gpt4o-mini的价格如下
    # Assuming the cost is $0.150 per 1M input tokens, $0.075 per 1M cached input tokens, and $0.600 per 1M output tokens
    cost_per_1M_input_tokens_gpt4o_mini = 0.150
    # cost_per_1M_cached_input_tokens_gpt4o_mini = 0.075
    # cost_per_1M_output_tokens_gpt4o_mini = 0.600


    # For simplicity, assume all tokens are input tokens
    total_cost = (total_tokens / 1_000_000) * cost_per_1M_input_tokens_gpt4o_mini
    # Assuming the cost is $0.150 per 1M input tokens, $0.075 per 1M cached input tokens, and $0.600 per 1M output tokens
    cost_per_1M_input_tokens_gpt4o_mini = 0.150
    # For simplicity, assume all tokens are input tokens
    total_cost = (total_tokens / 1_000_000) * cost_per_1M_input_tokens_gpt4o_mini
    return total_cost


def replace_epub_text(epub_file, output_file):
    # Read the epub file
    book = epub.read_epub(epub_file)

    # Initialize a counter for the placeholder
    placeholder_counter = 1

    # Iterate through all the items in the epub
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')

            # Replace text with numbered placeholders
            for tag in soup.find_all(text=True):
                if tag.strip():  # Only replace non-empty text
                    print(f"Original text {placeholder_counter}: <{tag.parent.name}>{tag.strip()}</{tag.parent.name}>")  # Print the original text wrapped in its parent tag
                    placeholder = f"【待翻译内容{placeholder_counter}】"
                    tag.replace_with(placeholder)
                    placeholder_counter += 1

            # Update the item content with placeholders
            item.set_content(str(soup).encode('utf-8'))

    # Write the modified content to a new epub file
    epub.write_epub(output_file, book, {})


if __name__ == "__main__":
    input_file = '/Users/solongoj/temp/ink.epub'
    output_file = '/Users/solongoj/temp/ink_replace.epub'
    # read_epub(input_file, output_file)
    # convert_epub_to_html(input_file,output_file)
    replace_epub_text(input_file,output_file)

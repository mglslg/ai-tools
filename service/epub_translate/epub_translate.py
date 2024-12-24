import ebooklib
from ebooklib import epub
import openai
import os
from bs4 import BeautifulSoup

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



if __name__ == "__main__":
    input_file = '/Users/solongoj/temp/oldman.epub'
    output_file = '/Users/solongoj/temp/oldman.epub'
    read_epub(input_file, output_file)

import logging
import requests

def scrape(url: str, output_path: str, doc_type: str):
    """
    Downloads a form from a given URL using the requests library.

    This functional implementation performs a real web request to fetch
    the content and save it to a local file.

    Args:
        url (str): The URL of the insurance form.
        output_path (str): The local path to save the downloaded file.
        doc_type (str): The type of the document ('pdf' or 'html'). This is
                        maintained for consistency but the download logic is generic.
    """
    logging.info(f"Downloading content from '{url}'...")

    # A user-agent header can help avoid being blocked by some websites.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)

        # Check if the request was successful
        response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)

        # Write the content to the output file.
        # It's important to use 'wb' (write binary) mode to correctly handle
        # all file types, including PDFs and images.
        with open(output_path, 'wb') as f:
            f.write(response.content)

        logging.info(f"Successfully downloaded and saved to '{output_path}'.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download from '{url}'. Error: {e}")
        # Re-raise the exception to be caught by the main pipeline loop
        raise
    except IOError as e:
        logging.error(f"Failed to write downloaded content to '{output_path}'. Error: {e}")
        raise

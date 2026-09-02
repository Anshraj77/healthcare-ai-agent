import requests
from bs4 import BeautifulSoup


def scrape_website(url):

    print(
        f"Scraping: {url}"
    )

    response = requests.get(
        url,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    # Remove unnecessary elements

    for element in soup(

        [
            "script",
            "style",
            "nav",
            "footer",
            "header"
        ]

    ):

        element.decompose()


    text = soup.get_text(
        separator="\n"
    )


    lines = []


    for line in text.splitlines():

        cleaned = line.strip()

        if cleaned:

            lines.append(
                cleaned
            )


    return "\n".join(lines)


def save_knowledge_base(text):

    file_path = (
        "knowledge_base/clinic_info.txt"
    )


    with open(

        file_path,

        "w",

        encoding="utf-8"

    ) as file:

        file.write(text)


    print(
        f"Knowledge base saved to {file_path}"
    )


if __name__ == "__main__":

    website_url = input(
        "Enter clinic website URL: "
    )


    try:

        website_text = scrape_website(
            website_url
        )


        save_knowledge_base(
            website_text
        )


        print(
            "Website ingestion completed successfully!"
        )


    except Exception as error:

        print(
            f"Error: {error}"
        )
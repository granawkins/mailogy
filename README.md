# Mailogy

Interact with your email records using natural language. You can say:

* “Give me every receipt in my inbox in CSV format, with the following columns: gmail link to the email, sender email, sender name, amount in the receipt.”
* “Give me every subscription in my inbox including cancelled subscriptions. ""
* “Tell me every service I’ve ever logged into or signed up for along with time of last login”

## How to Download Your Gmail as a .mbox File

To download your Gmail emails in `.mbox` format, follow these steps:

1. Go to your Google Account by navigating to https://myaccount.google.com/.
2. On the left navigation panel, click on `Data & privacy`.
3. Scroll down to the `Data from apps and services you use` section and click on `Download your data`.
4. You will be redirected to the Google Takeout page. By default, all data types are selected. Click on `Deselect all`.
5. Scroll down to `Mail` and check the box next to it.
6. You can choose to include all your email labels or select specific labels by clicking on `All mail data included`.
7. After making your selection, scroll down to the bottom of the list and click on `Next step`.
8. Choose your preferred file type, frequency, and destination for the data export. For `.mbox` files, you can leave the default settings.
9. Click on `Create export`. Google will then prepare your download, which may take some time depending on the amount of data.
10. Once the export is ready, Google will email you a link to download your `.mbox` file. Follow the instructions in the email to download the file to your computer.

## Usage Guide

To use Mailogy, follow these steps:

1. Ensure you have an OpenAI API key. You can set the `OPENAI_API_KEY` environment variable manually, or you will be prompted to enter it when you run the program for the first time.

2. Install the required dependencies by running `pip install -r requirements.txt` in your terminal.

3. To process your `.mbox` file, run the program using the following command:

   ```
   python -m mailogy path_to_your_mbox_file.mbox
   ```

   Replace `path_to_your_mbox_file.mbox` with the actual path to your `.mbox` file.

4. After your `.mbox` file has been processed, you can start mailogy without specifying the file:

    ```
    python -m mailogy
    ```

    If you do include a file, you'll be guided through the same workflow as #3.

5. Follow the on-screen prompts to interact with the program and process your email records using natural language commands.

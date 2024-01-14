# Mailogy

Interact with your email records using natural language. You can say:

* “Give me every receipt in my inbox in CSV format, with the following columns: gmail link to the email, sender email, sender name, amount in the receipt.”
* “Give me every subscription in my inbox including cancelled subscriptions. Tell me what my monthly subscription bill is” (you can probably get this out of the last one)
* “Tell me every service I’ve ever logged into or signed up for along with time of last login”
* “Identify everyone who is sending me messages that I don’t read, and unsubscribe from them.”
* “Identify the senders who are sending the highest ratio of emails in to emails replied to”
* “Identify the most important people in terms of the number of emails sent to them”

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

4. By default, the program processes a limited number of emails (100) to prevent excessive use of your OpenAI API key. If you wish to process more than 100 emails, you can manually set the limit by using the `--limit` or `-l` argument followed by the desired number:

   ```
   python -m mailogy path_to_your_mbox_file.mbox --limit 200
   ```

   **Note:** Be cautious when setting a high limit as it may result in higher costs due to API usage.

5. If you do not specify the `--limit` argument, the program will use the default limit of 100 emails. It is recommended to start with the default limit to get an understanding of the program's functionality and API usage.

6. Follow the on-screen prompts to interact with the program and process your email records using natural language commands.

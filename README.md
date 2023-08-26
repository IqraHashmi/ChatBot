# Chat Bot Automation

This repository contains scripts for executing and querying a chat bot through the terminal.

## Execution through Terminal

### Save Chat Bot

To save the chat bot, use the following command in the terminal:

```bash
python3 saveBotS3.py "<website's urls separated by commas>" "<email>" "<bot name>" "<manual text>" "<s3 bucket's pdf keys>" "<characters limit>"
```

Replace the placeholders with appropriate values:

`<website's urls separated by commas>`: Provide the URLs separated by commas.

`<email>`: Your email address.

`<bot name>`: Name of the chat bot.

`<manual text>`: Text for manual interaction.

`<s3 bucket's pdf keys>`: Keys for the S3 bucket's PDF separated by commas.

`<characters limit>`: Character limit for the chat bot.

### Query Chat Bot

To query the chat bot, use the following command in the terminal:

```bash
python3 botQueryS3.py "<query>" "<email>" "<bot name>"
```

Replace the placeholders with appropriate values:

`<query>`: Your query for the chat bot.

`<email>`: Your email address.

`<bot name>`: Name of the chat bot.


The query will be processed, and you'll receive the bot's response.

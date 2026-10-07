# Hindi Anime Auto Bot — Koyeb

For content you own, have permission to redistribute, or are otherwise authorized to distribute.

## Features
- FSub / join verification
- Deep links: `/start CODE`
- Authorized file storage using Telegram `file_id`
- Public-channel GET button
- Duplicate-safe database keys
- Koyeb Procfile

## Environment variables
`BOT_TOKEN` = BotFather token  
`FSUB_CHANNEL` = e.g. `@MyFsubChannel`  
`PUBLIC_CHANNEL` = e.g. `@MyPublicChannel`  
`ADMIN_ID` = your numeric Telegram ID

## Telegram permissions
1. Add the bot as admin to the FSub channel.
2. Add the bot as admin to the public channel with permission to post.
3. The bot must be able to receive the authorized files you save.

## Koyeb
GitHub repository -> Koyeb -> Create Web Service -> GitHub -> Buildpack.

Run command:
`python bot.py`

Add all environment variables, then deploy.

## Save an authorized file
Send the document to the bot as admin with:

`/save DEMO001`
`My Anime - Episode 01`

The bot replies with a deep link.

## Publish the saved item
Send to the bot:

`/post DEMO001`

The bot posts a GET button to `PUBLIC_CHANNEL`.

The repository intentionally does not scrape or redistribute copyrighted anime from third-party Telegram channels.

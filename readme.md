# Barcode Generator Bot

This is a Telegram bot that generates barcodes and merges them into a single PDF file. Users can specify the amount and length of barcodes they want to generate using the `/generate` command.

## Prerequisites

Before running the bot, you need to:

1. Create a Telegram bot using [@BotFather](https://t.me/BotFather) and obtain the bot token.
2. Install the required Python packages listed in `requirements.txt`.
3. Set up the environment variable `BOT_TOKEN` with your bot token.

## Usage

1. **Clone the Repository**: 
   ```bash
   git clone https://github.com/dozerokz/barcode-generator-bot.git
   ```

2. **Install Dependencies**:
   ```bash
   cd barcode-generator-bot
   pip install -r requirements.txt
   ```

3. **Set Environment Variable**:
   ```bash
   export BOT_TOKEN="your_bot_token_here"
   ```

4. **Run the Bot**:
   ```bash
   python3 main.py
   ```

## Bot Commands

- `/start`: Start the bot and get instructions on how to generate barcodes.
- `/generate AMOUNT LENGTH`: Generate barcodes. Replace `AMOUNT` with the number of barcodes to generate and `LENGTH` with the length of each barcode.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

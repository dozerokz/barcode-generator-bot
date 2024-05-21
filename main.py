import random
import string
import asyncio

from barcode import Code128
from barcode.writer import ImageWriter
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message, FSInputFile
from pypdf import PdfMerger

BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    logging.error("Bot token not found in environment variables")
    raise SystemExit("Bot token not found. Exiting...")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def record_barcode(barcode: str) -> None:
    """Record the generated barcode."""
    try:
        with open('recorded_barcodes.txt', 'a') as file:
            file.write(barcode + '\n')
    except Exception as e:
        logging.error(f"Error recording barcode: {e}")


async def clear_folder(folder_path: str) -> None:
    """Clear the contents of a folder."""
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    clear_folder(file_path)  # Recursively clear subdirectories
                    os.rmdir(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

        os.rmdir(folder_path)
    except Exception as e:
        logging.error(f"Error clearing folder: {e}")


async def generate_random_string(length: int, recorded_barcodes: set) -> str:
    """Generate a random alphanumeric string of given length."""
    letters_and_digits = string.ascii_uppercase + string.digits
    while True:
        random_string = ''.join(random.choice(letters_and_digits) for _ in range(length))
        if random_string not in recorded_barcodes:
            logging.info(f"Generated barcode: {random_string}")
            await record_barcode(random_string)
            return random_string


async def generate_barcode_pdf(amount: int, barcode_length: int, user_id: int) -> list[str]:
    """Generate specified amount of PDF barcodes with specified length."""
    barcodes = []
    recorded_barcodes = set()
    amount = min(amount, 200)

    try:
        # Load existing barcodes
        if os.path.exists('recorded_barcodes.txt'):
            with open('recorded_barcodes.txt', 'r') as file:
                recorded_barcodes.update(line.strip() for line in file)

        # Load existing barcodes for the user
        user_folder = f'barcodes{user_id}'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        for _ in range(amount):
            random_string = await generate_random_string(barcode_length, recorded_barcodes)
            code128 = Code128(random_string, writer=ImageWriter())
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                barcode_filename = tmp_file.name
                code128.write(barcode_filename)

            barcode_image = Image.open(barcode_filename)
            barcode_width, barcode_height = barcode_image.size

            # Save the barcode as a PDF file
            pdf_filename = f'{user_folder}/{random_string}.pdf'
            pdf = FPDF(unit='pt', format=[barcode_width, barcode_height])
            pdf.add_page()
            pdf.image(barcode_filename, x=0, y=0, w=barcode_width, h=barcode_height)
            pdf.output(pdf_filename)

            # Remove the temporary barcode image file
            os.remove(barcode_filename)
            logging.info(f'Barcode PDF saved as: {pdf_filename}')
            barcodes.append(random_string)

        return barcodes
    except Exception as e:
        logging.error(f"Error generating barcodes: {e}")


async def merge_pdfs(pdf_files: list[str], user_id: int) -> None:
    """Merge generated PDF barcodes into a single PDF."""

    try:
        merger = PdfMerger()

        # Load existing barcodes for the user
        user_folder = f'barcodes{user_id}'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        for pdf in pdf_files:
            merger.append(f'{user_folder}/{pdf}.pdf')
        merger.write(f"{user_folder}/barcodes.pdf")
        merger.close()
    except Exception as e:
        logging.error(f"Error merging PDF files: {e}")


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer("Hi! Use `/generate 'AMOUNT' 'LENGTH'`\n\nExample:\n`/generate 5 7`", parse_mode="Markdown")


@dp.message(Command("generate"))
async def generate(message: Message, command: CommandObject) -> None:
    """Generate barcodes."""
    if command.args is None:
        await message.answer("Error: You need to enter the amount and length of codes\nExample: `/generate 5 7`",
                             parse_mode="Markdown")
        return

    try:
        amount, length = map(int, command.args.split(" ", maxsplit=1))
    except ValueError:
        await message.answer("Error: Invalid input. Example usage: `/generate 5 7`",
                             parse_mode="Markdown")
        return

    user_id = message.from_user.id

    barcodes = await generate_barcode_pdf(amount, length, user_id)
    await merge_pdfs(barcodes, user_id)
    barcodes_pdf = FSInputFile(f"barcodes{user_id}/barcodes.pdf", filename="barcodes.pdf")
    await message.answer_document(barcodes_pdf)
    await message.answer('\n'.join(barcodes))

    await clear_folder(f'barcodes{user_id}')


async def main() -> None:
    """Main function to start the bot."""
    logging.info("Bot started")
    await dp.start_polling(bot)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Failed to start the bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())


import datetime
import os
import typer
import asyncio
from concurrent.futures import ProcessPoolExecutor

from gradio_app.inference import postprocess_inst_names
from gradio_app.inference import inference_patch
from gradio_app.convert import abc2xml, xml2, pdf2img



app = typer.Typer()


def convert_files(abc_content, period, composer, instrumentation):
	if not all([period, composer, instrumentation]):
		raise "Please complete a valid generation first before saving"

	timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	prompt_str = f"{period}_{composer}_{instrumentation}"
	filename_base = f"./opus/{timestamp}_{prompt_str}"

	abc_filename = f"{filename_base}.abc"
	with open(abc_filename, "w", encoding="utf-8") as f:
		f.write(abc_content)

	# instrumentation replacement
	postprocessed_inst_abc = postprocess_inst_names(abc_content)
	if postprocessed_inst_abc != abc_content:
		filename_base_postinst = f"{filename_base}_postinst"
		with open(filename_base_postinst + ".abc", "w", encoding="utf-8") as f:
			f.write(postprocessed_inst_abc)
	else:
		filename_base_postinst = None

	# Convert files
	file_paths = {'abc': abc_filename}
	try:
		# abc2xml
		abc2xml(filename_base)
		if filename_base_postinst is not None:
			abc2xml(filename_base_postinst)

		# xml2pdf
		print('to pdf...')
		xml2(filename_base, 'pdf')

		# xml2mid
		print('to mid...')
		xml2(filename_base, 'mid')
		if filename_base_postinst is not None:
			xml2(filename_base_postinst, 'mid')

		# xml2mp3
		print('to mp3...')
		xml2(filename_base, 'mp3')
		if filename_base_postinst is not None:
			xml2(filename_base_postinst, 'mp3')

		# PDF to images
		images = pdf2img(filename_base)
		for i, image in enumerate(images):
			image.save(f"{filename_base}_page_{i+1}.png", "PNG")

		filename_base_or_postinst = filename_base_postinst if filename_base_postinst else filename_base

		file_paths.update({
			'xml': f"{filename_base_or_postinst}.xml",
			'pdf': f"{filename_base}.pdf",
			'mid': f"{filename_base_or_postinst}.mid",
			'mp3': f"{filename_base_or_postinst}.mp3",
			'pages': len(images),
			'current_page': 0,
			'base': filename_base
		})

		print(chr(0x1f34e), file_paths['base'])

	except Exception as e:
		raise f"File processing failed: {str(e)}"

	return file_paths


async def run_in_process(pool, func, *args):
	loop = asyncio.get_running_loop()
	return await loop.run_in_executor(pool, func, *args)


async def async_main(period, composer, instrumentation, n):
	tasks = []
	with ProcessPoolExecutor() as pool:
		for i in range(n):
			print(f"\033[1;94mGenerating {i+1}/{n} piece...\033[0m")
			abc_content = inference_patch(period, composer, instrumentation)
			future = pool.submit(convert_files, abc_content, period, composer, instrumentation)
			task = asyncio.wrap_future(future)
			tasks.append(task)

	try:
		await asyncio.wait_for(asyncio.gather(*tasks), timeout=120)
	except asyncio.TimeoutError:
		print("Timeout reached. Exiting...")
		exit()


@app.command()
def main(
	period: str = typer.Argument(..., help="Period of the music"),
	composer: str = typer.Argument(..., help="Composer of the music"),
	instrumentation: str = typer.Argument(..., help="Instrumentation of the music"),
	n: int = typer.Option(1, help="Number of pieces to generate"),
):
	 asyncio.run(async_main(period, composer, instrumentation, n))

if __name__ == "__main__":
	app()

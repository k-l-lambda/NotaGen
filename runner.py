
import datetime
import os
import typer

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
	filename_base_postinst = f"{filename_base}_postinst"
	with open(filename_base_postinst + ".abc", "w", encoding="utf-8") as f:
		f.write(postprocessed_inst_abc)

	# Convert files
	file_paths = {'abc': abc_filename}
	try:
		# abc2xml
		abc2xml(filename_base)
		abc2xml(filename_base_postinst)
		print(f'{filename_base=}')
		print(f'{filename_base_postinst=}')

		# xml2pdf
		print('to pdf...')
		xml2(filename_base, 'pdf')

		# xml2mid
		print('to mid...')
		xml2(filename_base, 'mid')
		xml2(filename_base_postinst, 'mid')

		# xml2mp3
		print('to mp3...')
		xml2(filename_base, 'mp3')
		xml2(filename_base_postinst, 'mp3')

		# 将PDF转为图片
		images = pdf2img(filename_base)
		for i, image in enumerate(images):
			image.save(f"{filename_base}_page_{i+1}.png", "PNG")

		file_paths.update({
			'xml': f"{filename_base_postinst}.xml",
			'pdf': f"{filename_base}.pdf",
			'mid': f"{filename_base_postinst}.mid",
			'mp3': f"{filename_base_postinst}.mp3",
			'pages': len(images),
			'current_page': 0,
			'base': filename_base
		})

	except Exception as e:
		raise f"File processing failed: {str(e)}"

	return file_paths


@app.command()
def main(
	period: str = typer.Argument(..., help="Period of the music"),
	composer: str = typer.Argument(..., help="Composer of the music"),
	instrumentation: str = typer.Argument(..., help="Instrumentation of the music"),
	n: int = typer.Option(1, help="Number of pieces to generate"),
):
	for i in range(n):
		print(f"Generating {i+1}/{n} pieces...")
		abc_content = inference_patch(period, composer, instrumentation)
		file_paths = convert_files(abc_content, period, composer, instrumentation)
		print(chr(0x1f34e), file_paths['base'])


if __name__ == "__main__":
	app()

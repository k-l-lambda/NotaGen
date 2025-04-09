
import os
import typer
import random
import hashlib
import signal

from gradio_app.inference import postprocess_inst_names
from gradio_app.inference import inference_patch
from gradio_app.convert import abc2xml, xml2, pdf2img



app = typer.Typer()


@app.command()
def main(
	prompts: str = typer.Argument(..., help="A file path to the prompts list"),
	n: int = typer.Option(1, help="Number of pieces to generate"),
	target_dir: str = typer.Option('./opus/abc', help="Directory to save the generated pieces"),
):
	prompt_list = open(prompts, 'r').readlines()
	prompt_list = [line.strip().split('_') for line in prompt_list]
	assert all(len(args) == 3 for args in prompt_list)

	global to_quit
	to_quit = False

	def handle_sigint(sig, _):
		print(f"Signal {sig} received. Requesting safe shutdown...")
		global to_quit
		to_quit = True
	signal.signal(signal.SIGINT, handle_sigint)

	for i in range(n):
		period, composer, instrumentation = random.choice(prompt_list)
		print(f"\033[1;94mGenerating {i+1}/{n} piece...\033[0m")
		abc_content = inference_patch(period, composer, instrumentation)
		md5_hash = hashlib.md5(abc_content.encode('utf-8')).hexdigest()
		with open(f'{target_dir}/{md5_hash}.abc', 'w') as f:
			f.write(abc_content)

		if to_quit:
			print("Safe shutdown.")
			break

if __name__ == "__main__":
	app()

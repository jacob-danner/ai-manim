import dspy
import subprocess
from telemetry.config import setup_telemetry, shutdown_telemetry, get_telemetry_config


class Pipeline(dspy.Module):
    def __init__(self):
        self.diagram_describer = dspy.ChainOfThought(
            "diagram -> detailed_visual_description"
        )

        self.manim_generator = dspy.ChainOfThought(
            "detailed_visual_description -> manim_code"
        )

    def forward(self, diagram_image):
        description_result = self.diagram_describer(diagram=diagram_image)
        manim_result = self.manim_generator(
            detailed_visual_description=description_result.detailed_visual_description,
        )

        return dspy.Prediction(
            detailed_visual_description=description_result.detailed_visual_description,
            manim_code=manim_result.manim_code,
        )


def run_pipeline(source_diagram_file: str, output_file: str):
    pipeline = Pipeline()
    diagram_image = dspy.Image.from_file(source_diagram_file)
    result = pipeline(diagram_image)

    with open(output_file, "w") as f:
        f.write(f"'''\nDescription:\n{result.detailed_visual_description}\n'''\n\n")
        f.write(result.manim_code)

    subprocess.run(["manim", "-s", output_file], check=True)


if __name__ == "__main__":
    # Set up telemetry
    config = get_telemetry_config()
    tracer_provider = setup_telemetry(**config)

    try:
        lm = dspy.LM(
            model="openrouter/google/gemini-2.5-flash",
            max_tokens=20000,
        )
        dspy.configure(lm=lm)

        run_pipeline("./source_diagrams/1.png", "visualization.py")
    finally:
        # Clean up telemetry
        if tracer_provider:
            shutdown_telemetry()

import subprocess
import sys
from pathlib import Path

def convert_model():
    """
    Downloads and converts a Hugging Face model to the CTranslate2 format.
    """
    model_name = "Helsinki-NLP/opus-mt-en-id"
    output_dir = Path.home() / ".GameTranslator" / "models" / "enid_ctranslate2"

    # 1. Create the output directory if it doesn't exist
    try:
        print(f"Creating model directory at: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory: {e}")
        sys.exit(1)

    # 2. Construct the conversion command
    # We use the ctranslate2-transformers-converter tool provided by the ctranslate2 package.
    command = [
        "ct2-transformers-converter",
        "--model", model_name,
        "--output_dir", str(output_dir),
        "--force"  # Overwrite existing files if any
    ]

    print("\n--- Starting Model Conversion ---")
    print(f"Command: {' '.join(command)}")
    print("This will download the model from Hugging Face and convert it. This may take a few minutes...")

    # 3. Run the conversion process
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print("\n--- Conversion Successful ---")
        print(result.stdout)
    except FileNotFoundError:
        print("\n--- Conversion Failed ---")
        print("Error: `ct2-transformers-converter` command not found.")
        print("Please ensure ctranslate2 is installed correctly and the command is in your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("\n--- Conversion Failed ---")
        print(f"Error during model conversion (return code {e.returncode}):")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

    print(f"\nModel successfully converted and saved to {output_dir}")
    print("Listing created files:")
    for file_path in output_dir.iterdir():
        print(f"- {file_path.name}")


if __name__ == "__main__":
    convert_model()
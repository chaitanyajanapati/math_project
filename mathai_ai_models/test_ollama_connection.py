import subprocess

def test_ollama():
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        print("Ollama installed:", result.stdout.strip())
    except FileNotFoundError:
        print("❌ Ollama not found. Please install it using:")
        print("curl -fsSL https://ollama.com/install.sh | sh")

if __name__ == "__main__":
    test_ollama()

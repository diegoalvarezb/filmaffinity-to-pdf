# filmaffinity-to-pdf

Export your FilmAffinity votes to a PDF.

## Prerequisites

- Python 3.8 or higher
- Pipenv

## Environment Setup

1. First, ensure you have Python installed. You can check your Python version with:
   ```bash
   python --version
   ```

2. Install Pipenv if you haven't already:
   ```bash
   pip install pipenv
   ```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   pipenv install
   ```

## Usage

1. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

2. Run the script:
   ```bash
   python filmaffinity_exporter.py
   ```

## Project Structure

- `filmaffinity_exporter.py`: Main script that handles web scraping and PDF generation
- `Pipfile`: Dependencies and virtual environment configuration

## Dependencies

- `requests`: For making HTTP requests
- `beautifulsoup4`: For parsing HTML content
- `reportlab`: For PDF generation

## Notes

- Make sure you're always working within the Pipenv virtual environment
- The virtual environment helps isolate project dependencies from your global Python installation
- Pipenv automatically manages your project's dependencies through the Pipfile

## Contributing

Instructions for how to contribute to the project.

## License

This project is licensed under the MIT License.
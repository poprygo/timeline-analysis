# timeline-analysis

This project analyzes location data from Google Takeout, specifically focusing on distances traveled in a passenger vehicle. It processes data from ZIP archives containing JSON files of location history and generates visual summaries for each year, broken down by month.

## Getting Started

### Prerequisites

Ensure you have Python 3.6+ installed on your system. This project uses virtual environments to manage dependencies.

### Setup

Clone the repository and navigate into the project directory:

```bash
git clone <repository-url>
cd timeline-analysis
```

Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Running the Analysis

To run the analysis, you need a ZIP archive from Google Takeout containing your location history in JSON format. The command below demonstrates how to start the analysis, replacing `<path_to_zip_archive>` with the actual path to your ZIP file:

```bash
python main.py <path_to_zip_archive> --dates_to_skip YYYY-MM-DD YYYY-MM-DD
```

- `<path_to_zip_archive>`: Path to the ZIP archive containing the Takeout data.
- `--dates_to_skip` *(optional)*: Space-separated dates (in `'YYYY-MM-DD'` format) to exclude from the analysis.

### Output

The script generates PNG images with visual summaries of distances traveled in a passenger vehicle, broken down by year and month. These images are saved in the project directory.

## License

MIT
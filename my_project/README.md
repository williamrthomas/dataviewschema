# Metadata Knowledge Extraction

A Python tool for analyzing database schema metadata and generating visual documentation using LLM-powered analysis.

## Features

- Schema metadata processing from CSV files
- Domain analysis using LLM (via OpenRouter/OpenAI)
- Pattern and relationship analysis
- Visual documentation generation using Mermaid diagrams
- Activity logging

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_API_KEY=your-api-key
```

## Usage

1. Place schema metadata CSV files in `data/` directory:
   - schema_tables.csv
   - schema_columns.csv

2. Run the main script:
```bash
python src/main.py
```

3. Generated artifacts will be available in:
   - outputs/intermediate/ - JSON analysis results
   - outputs/final/ - Generated diagrams
   - outputs/logs/ - Activity logs

## Project Structure

```
my_project/
├── data/                  # Input CSV files
├── outputs/              
│   ├── final/            # Generated diagrams
│   ├── intermediate/     # Analysis results
│   └── logs/             # Activity logs
├── src/
│   ├── diagram_generator.py  # Mermaid diagram generation
│   ├── main.py              # Main execution script
│   ├── prompt_utils.py      # LLM interaction utilities
│   └── schema_loader.py     # CSV processing utilities
├── .env                  # Environment variables
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
└── requirements.txt     # Python dependencies
```

## Development

- Python 3.13+
- Uses OpenRouter API for LLM capabilities
- Mermaid for diagram generation
- Pandas for CSV processing

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

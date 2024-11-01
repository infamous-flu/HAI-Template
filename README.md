# Voice Chat Interface

A voice chat interface that uses OpenAI's APIs for speech-to-text, language processing, and text-to-speech conversion.

## Overview

Hold down the spacebar to talk with an AI assistant. Your voice will be:
1. Transcribed to text
2. Processed by GPT-4
3. Converted back to speech
4. Played through your speakers

The interface features an animated ASCII art display that changes colors based on the current state (standby, listening, processing, speaking).

## Setup

### Installation
1. Clone the repository:
```bash
git clone https://github.com/infamous-flu/HAI-Template.git
cd HAI-Template
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the backend server in a terminal window:
```bash
python main.py
```

2. Open a new terminal window and start the frontend server on port 3000
```bash
python -m http.server 3000
```

3. Open your browser of choice and navigate to:
```
http://localhost:3000
```

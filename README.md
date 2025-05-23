# WebRover

<div align="center">
  <!-- Backend -->
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Google-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/DeepSeek-4285F4?style=for-the-badge&logo=deepseek&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-FF6B6B?style=for-the-badge&logo=graph&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/Pillow-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  
  
  <!-- Frontend -->
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  

  <h3>Your AI Co-pilot for Web Navigation 🚀</h3>

  <p align="center">
    <b>Autonomous Web Agent | Task Automation | Information Retrieval</b>
  </p>
</div>


## Overview

WebRover is an autonomous AI agent designed to interpret user input and execute actions by interacting with web elements to accomplish tasks or answer questions. It leverages advanced language models and web automation tools to navigate the web, gather information, and provide structured responses based on the user's needs.

## Motivation

In today's digital landscape, users spend significant time performing repetitive web-based tasks like research, data gathering, and information synthesis. WebRover aims to automate these tasks by combining the power of large language models with web automation capabilities, allowing users to focus on higher-level decision making while the agent handles the manual browsing work.

## Demo

### Video Demo
https://github.com/user-attachments/assets/95ae9afb-3fdf-47f8-857e-f6a1a0d94df5
> Watch WebRover autonomously navigate websites and extract information in real-time.


## Features

- 🤖 **AI-Powered Navigation**: Uses GPT-4 to understand context and navigate websites intelligently
- 🎯 **Smart Element Detection**: Automatically identifies and interacts with relevant page elements
- 📸 **Visual Feedback**: Real-time visualization of the navigation process
- 🔄 **Autonomous Operation**: Self-correcting navigation with fallback strategies

### Core Components

1. **State Management**
   - Uses LangGraph for maintaining agent state
   - Handles complex navigation flows and decision making

2. **Browser Automation**
   - Playwright for reliable web interaction
   - Implements Microsoft's Set of Marks (SoM) for intelligent page annotation
   - Custom screenshot and element detection system

3. **Visual Processing**
    - Automated element detection and labeling
    - Bounding box generation around interactive elements
    - Numerical labeling system for LLM reference
    - Real-time page annotation for AI decision making

4. **AI Decision Making**
   - GPT-4 for understanding context and planning
   - LangChain for orchestrating AI workflows
   - Enhanced visual context through SoM annotations

5. **User Interface**
   - Real-time response display
   - Interactive query input
   - Visual feedback of navigation

### Agent Tools

The agent comes equipped with several tools to interact with web pages:

- **Click**: Simulates mouse clicks on web elements
- **Type**: Enters text into input fields
- **Scroll**: Navigates through pages (supports both regular pages and PDFs)
- **Wait**: Adds delays to ensure page loading
- **GoBack**: Returns to previous pages
- **GoToSearchEngine**: Redirects to Google for new searches

## Architecture

![Agent Architecture Diagram](https://github.com/naveenkrishnan840/Web-Rover-Chat-Bot/blob/main/backend/graph.png)


### How It Works

1. **Task Planning**: When given a task, the agent first creates a master plan using the LLM

2. **Page Analysis**: For each page, the agent:
   - Captures a screenshot
   - Identifies interactive elements
   - Creates bounding boxes around elements
   - Assigns numerical labels for reference

3. **Decision Making**: The agent:
   - Analyzes the current page state
   - Compares against the master plan
   - Decides on the next action
   - Executes the chosen tool

4. **Response Generation**: After gathering necessary information, generates a structured response with:
   - Steps taken to complete the task
   - Final answer or result

## Input Prompt:
  ### Google Flights – Find Cheapest Flight
    Go to Google Books and search for "Atomic Habits by James Clear". Extract book details like author, publisher, and summary.
    Go to Google Flights and search for the cheapest and fastest flights from Chennai (MAA) to Mumbai (BOM) on [DATE]. Extract airline names, ticket prices, layovers (if any), and flight durations.

  ### Google Translate – Translate Text
    Go to Google Translate and translate the following text from English to French: "Hello, how are you?". Extract the translated text.
  ### Google Maps – Find Directions
    Go to Google Maps and search for the fastest route from Kolkata, India to Darjeeling, India by car. Extract distance, estimated travel time, and suggested route details.
  ### Google Lens – Identify an Object
    Go to Google Lens and upload an image of the "Eiffel Tower". Identify the landmark, its location, and related information.
  ### YouTube – Find Trending Videos
    Go to YouTube and find the top 5 trending videos in India. Extract the video titles, URLs, and view counts.
  ### Google Search – Get Top News
    Go to Google Search and find the latest news about "AI advancements in 2025". Extract the top 3 news headlines with their URLs.
  ### Google Shopping – Find Cheapest Product
    Go to Google Shopping and search for "iPhone 15 Pro Max". Extract the lowest price, seller name, and product URL.
  ### Google Weather – Get Forecast
    Go to Google and search "weather in London today". Extract the temperature, humidity, and weather conditions.
  ### Google News – Get Breaking News
    Go to Google News and find the latest breaking news in "Technology". Extract the top 5 headlines with their URLs.
  ### Google Books – Find a Book
    Go to Google Books and search for "Atomic Habits by James Clear". Extract book details like author, publisher, and summary.


## Tech Stack

### Backend
- Python 3.12+
- LangChain for AI orchestration
- Playwright for browser automation
- Googale Gemini-2.0-flash & Deepseek deepseek/deepseek-r1-distill-llama-70b for decision making
- FastAPI for API endpoints

### Frontend
- React.js
- JavaScript
- Tailwind CSS
- Framer Motion for animations

## Backend Setup

1. Clone the repository
   ```bash
   git clone https://github.com/naveenkrishnan840/Web-Rover-Chat-Bot.git
   cd Web-Rover-Chat-Bot
   cd backend
   ```

2. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate (or .venv\Scripts\activate on Windows)
   ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables in `.env`:
    ```bash
    OPENAI_API_KEY="your_openai_api_key",
    LANGCHAIN_API_KEY="your_langchain_api_key",
    LANGCHAIN_TRACING_V2="true",
    LANGCHAIN_ENDPOINT="https://api.smith.langchain.com",
    LANGCHAIN_PROJECT="your_project_name"
    MODEL_NAME="Your_mode_name"
    OPENROUTER_BASE_URL="your_openrouter_url"
    ```

5. Run the backend:

   Make sure you are in the backend folder

    ```bash
    uvicorn app.main:app --reload --port 8000 
    ```

   For Windows User:

    ```bash
    uvicorn app.main:app --port 8000
    ```

6. Access the API at `http://localhost:8000`

## Frontend Setup

1. Open a new terminal and make sure you are in the WebRover folder
   ```bash
   cd frontend
   ```

2. Install dependencies:
    ```bash
    npm install
    ```

3. Run the frontend:
    ```bash
    npm run dev
    ```

4. Access the application at `http://localhost:3000`


## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by [@naveenkrishnan840](https://github.com/naveenkrishnan840)

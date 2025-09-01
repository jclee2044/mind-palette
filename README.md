# MindPalette - Synesthesia Color Association App

A desktop application for exploring and documenting synesthetic color associations using AI-powered analysis and visualization.

## 🌈 Features

### **Train Tab**
- Interactive color training interface with random color selection
- Association input and database storage with progress tracking
- Save colors for later without writing associations
- Real-time color count display

### **Summarize Tab**
- AI-generated summaries of your synesthetic associations
- Export summaries to text files
- Automatic categorization by color families and themes

### **Chat Tab**
- Interactive chat with AI about your synesthetic experiences
- Save and manage chat conversations with search functionality
- Export chat responses to text files
- View and delete saved chat history

### **Colors Tab**
- Browse and search XKCD color palette with real-time filtering
- View color associations in real-time with dynamic display
- Add new associations for any color with popup editor
- Color picker with hex code and name display
- Save colors for later viewing and management
- Clickable color squares in associations table to switch to Colors tab
- Dynamic dark/light mode support with appropriate text colors
- Scrollable association display for long descriptions

### **Associations Tab**
- Comprehensive table view of all associations with rainbow sorting
- Search and filter functionality across color names, hex codes, and associations
- Edit and delete associations with confirmation dialogs
- Export to Excel with color visualization and proper formatting
- Clickable color squares to switch to Colors tab and display that color

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Required Python packages (see requirements.txt)

### Setup
1. Clone the repository:
```bash
git clone <your-repo-url>
cd mind-palette
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
   - Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - The app will prompt you to add it on first use, or you can add it to your environment variables

4. Run the application:
```bash
python3 main.py
```

## 📁 Project Structure

```
mind-palette/
├── main.py                 # Main application entry point with dark mode support
├── utils.py                # Shared utilities, database functions, and theme detection
├── ui_modules/             # Modular UI components
│   ├── train.py            # Training tab functionality
│   ├── summarize.py        # Summary generation and display
│   ├── chat.py             # Chat interface with AI
│   ├── colors.py           # Color viewer with dynamic display and scrolling
│   ├── associations.py     # Association management with clickable colors
│   └── popups/             # Popup dialogs
│       ├── help_popup.py   # Help documentation
│       ├── about_popup.py  # About information
│       └── api_key_popup.py # API key setup
├── gemini_backend.py       # AI backend integration
├── key_bindings.py         # Keyboard shortcuts
├── requirements.txt        # Python dependencies
├── db/                     # Database and data files
│   ├── associations.json   # Main association database
│   ├── saved_for_later.json # Colors saved for later
│   ├── saved_chats.json    # Saved chat conversations
│   └── summary.txt         # Generated summaries
├── icons/                  # Application icons
└── README.md              # This file
```

## 🎨 Usage

### Getting Started
1. **Train**: Start with the Train tab to build your color association database
2. **Explore**: Use the Colors tab to browse and add associations
3. **Analyze**: Generate summaries in the Summarize tab
4. **Chat**: Have conversations about your synesthetic experiences
5. **Manage**: Use the Associations tab to view and edit all your data

## 🔧 Configuration

### Database
- Associations are stored in `db/associations.json`
- Colors saved for later in `db/saved_for_later.json`
- Automatic backups created every 5 entries
- Summary files saved to `db/summary.txt`

### AI Integration
- Uses Google's Gemini AI for summaries and chat
- Configure API key through the app's built-in setup
- Supports custom prompts and responses

### Theme Support
- **Automatic Detection**: Detects system appearance on macOS, Windows, and Linux
- **Dynamic Adaptation**: All UI elements automatically adjust to light/dark mode
- **Consistent Colors**: Links and text use appropriate colors for current theme

## 📊 Data Format

### Association Structure
```json
{
  "hex": "#ff0000",
  "xkcd_name": "red",
  "associations": "Your synesthetic description here"
}
```

### Database Files
- `db/associations.json`: Main association database
- `db/saved_for_later.json`: Colors saved for later viewing
- `db/saved_chats.json`: Saved chat conversations
- `db/summary.txt`: Generated summaries

## 🛠️ Development

### Adding New Features
The modular structure makes it easy to add new functionality:
- Each tab is a separate module in `ui_modules/`
- Shared utilities in `utils.py`
- Main application logic in `main.py`
- Dark mode support built into the utility functions

### Cross-Platform Compatibility
- Tested on macOS, Windows, and Linux
- Uses tkinter for consistent UI across platforms
- Platform-specific adjustments for scrolling and input handling
- Automatic theme detection for each platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms and themes
5. Submit a pull request

## 🙏 Acknowledgments

- XKCD color palette for comprehensive color data
- Google Gemini AI for intelligent analysis
- Tkinter community for cross-platform UI framework
- Synesthesia community for inspiration and feedback

## 🐛 Known Issues

- Scrolling behavior may vary slightly between platforms
- Some UI elements may appear slightly different across platforms
- Large databases may require optimization for performance

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ for the synesthesia community** 

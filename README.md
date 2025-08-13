# Mind Palette - Synesthesia Color Association App

A desktop application for exploring and documenting synesthetic color associations using AI-powered analysis and visualization.

## 🌈 Features

### **Train Tab**
- Interactive color training interface
- Random color selection from XKCD color palette
- Association input and database storage
- Progress tracking for color descriptions

### **Summarize Tab**
- AI-generated summaries of your synesthetic associations
- Export summaries to text files
- Beautiful ASCII art header
- Integration with Gemini AI backend

### **Chat Tab**
- Interactive chat with AI about your synesthetic experiences
- Save and manage chat conversations
- Export chat responses to text files
- View and delete saved chat history

### **Colors Tab**
- Browse and search XKCD color palette
- View color associations in real-time
- Add new associations for any color
- Color picker with hex code and name display

### **Associations Tab**
- Comprehensive table view of all associations
- Search and filter functionality
- Edit and delete associations
- Export to Excel with color visualization
- Rainbow-sorted color organization

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Required Python packages (see requirements.txt)

### Setup
1. Clone the repository:
```bash
git clone <your-repo-url>
cd synesthesia-summarizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Gemini API key:
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add it to your environment variables or modify `gemini_backend.py`

4. Run the application:
```bash
python3 main.py
```

## 📁 Project Structure

```
synesthesia summarizer/
├── main.py                 # Main application entry point
├── utils.py                # Shared utilities and database functions
├── ui_modules/             # Modular UI components
│   ├── train.py            # Training tab functionality
│   ├── summarize.py        # Summary generation and display
│   ├── chat.py             # Chat interface with AI
│   ├── colors.py           # Color viewer and browser
│   └── associations.py     # Association management
├── gemini_backend.py       # AI backend integration
├── key_bindings.py         # Keyboard shortcuts
├── requirements.txt        # Python dependencies
├── db/                     # Database and data files
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

### Keyboard Shortcuts
- **Enter**: Submit forms and generate responses
- **Ctrl/Cmd + C/V**: Copy and paste
- **Delete/Backspace**: Delete saved chats (in chat viewer)

## 🔧 Configuration

### Database
- Associations are stored in `db/associations.json`
- Automatic backups created every 5 entries
- Summary files saved to `db/summary.txt`

### AI Integration
- Uses Google's Gemini AI for summaries and chat
- Configure API key in `gemini_backend.py`
- Supports custom prompts and responses

## 🛠️ Development

### Adding New Features
The modular structure makes it easy to add new functionality:
- Each tab is a separate module in `ui_modules/`
- Shared utilities in `utils.py`
- Main application logic in `main.py`

### Cross-Platform Compatibility
- Tested on macOS and Windows
- Uses tkinter for consistent UI across platforms
- Platform-specific adjustments for scrolling and input handling

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
- `db/associations_backup.json`: Automatic backup
- `db/saved_chats.json`: Saved chat conversations
- `db/summary.txt`: Generated summaries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on multiple platforms
5. Submit a pull request

## 🙏 Acknowledgments

- XKCD color palette for comprehensive color data
- Google Gemini AI for intelligent analysis
- Tkinter community for cross-platform UI framework

## 🐛 Known Issues

- Scrolling behavior may vary between macOS and Windows
- Some UI elements may appear slightly different across platforms
- Large databases may require optimization for performance

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ for the synesthesia community** 

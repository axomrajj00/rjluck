# 🎙️ Advanced RJ Assistant - Complete AI Voice Assistant

**Advanced RJ** is your fully-featured personal AI assistant with **JARVIS-style GUI**, **JSON memory system**, **task management**, **timers**, and **Hindi-English (Hinglish)** voice commands.

## ✨ **New Advanced Features**

### 🖥️ **JARVIS-Style GUI Interface**
- **Animated AI face** with speaking indicators
- **Real-time console** with color-coded logs
- **Memory bank** display showing all stored memories
- **Task manager** with timer countdown
- **Control panel** with voice commands
- **Dark theme** with cyan accents

### 🧠 **JSON Memory System**
- **Persistent memory** stored in `rj_memory.json`
- **Smart categorization** (notes, Wikipedia, tasks)
- **Search and recall** any stored information
- **Memory removal** by keyword
- **Timestamped entries** with metadata

### 📋 **Advanced Task Management**
- **Task creation** with voice commands
- **Timer integration** (e.g., "30 minute task")
- **Completion tracking** with timestamps
- **Visual task list** in GUI
- **Automatic notifications** when timers complete
- **Task persistence** across sessions

### ⏰ **Smart Timer System**
- **Voice-activated timers** ("RJ timer laga 15 minutes")
- **Background monitoring** with notifications
- **Multiple concurrent timers**
- **Task-linked timers** 
- **Audio alerts** when complete

## 🚀 **Quick Start**

### 1. **Easy Setup**
```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Or use the launcher
python3 run_rj.py
```

### 2. **Start Advanced RJ**
```bash
# GUI Mode (Recommended)
python3 advanced_rj.py

# Console Mode
python3 advanced_rj.py --no-gui

# Or use launcher
python3 run_rj.py
```

## 🎤 **Advanced Voice Commands**

### 🧠 **Memory Commands**
- **"RJ yaad rakh meeting tomorrow 2 PM"** - Store memory
- **"RJ bhool ja password"** - Remove memory containing "password"
- **"RJ yaad hai WiFi password"** - Recall specific memory
- **"RJ batao memory"** - Show all memories

### 📋 **Task Management**
- **"RJ task add kar complete report 30 minutes"** - Add task with timer
- **"RJ new task call client"** - Add simple task
- **"RJ tasks dikhao"** - Show all tasks
- **"RJ task complete kar"** - Mark task as done

### ⏰ **Timer Commands**
- **"RJ timer laga 15 minutes"** - Set 15-minute timer
- **"RJ alarm laga 5 minutes workout"** - Named timer
- **"RJ timer band kar"** - Stop active timers

### 📚 **Knowledge & Search**
- **"RJ Wikipedia India"** - Search Wikipedia (stored in memory)
- **"RJ batao Python ke bare mein"** - Get information
- **"RJ kya hai artificial intelligence"** - Ask questions
- **"RJ Google par search kar best restaurants"** - Web search

### 🖥️ **System Control**
- **"RJ volume badhao"** - Increase volume
- **"RJ calculator kholo"** - Open applications
- **"RJ computer lock kar"** - Lock screen
- **"RJ shutdown kar"** - System shutdown

## 🖼️ **GUI Features**

### **Main Interface Components:**
1. **🎭 Animated AI Face** - Visual feedback with speaking animation
2. **🖥️ Console Output** - Real-time colored logs of all activities
3. **🧠 Memory Bank** - Display of all stored memories with timestamps
4. **📋 Task Manager** - Interactive task list with timers
5. **🎛️ Control Panel** - Voice control buttons and status

### **GUI Controls:**
- **🎤 Start/Stop Listening** - Control voice recognition
- **🧠 Clear Memory** - Reset all stored memories
- **📋 Export Logs** - Save console output to file
- **✅ Complete Task** - Mark selected task as done
- **🗑️ Remove Task** - Delete selected task

## 📁 **Project Structure**

```
├── advanced_rj.py          # 🎙️ Advanced RJ with all features
├── rj_gui.py              # 🖥️ JARVIS-style GUI interface  
├── rj_assistant.py        # 📱 Basic RJ assistant
├── text_editor.py         # 📝 Built-in text editor
├── run_rj.py             # 🚀 Easy launcher script
├── requirements.txt       # 📦 Dependencies
├── setup.sh              # ⚙️ Setup script
├── .env                  # 🔐 API configuration
├── rj_memory.json        # 🧠 Memory storage (auto-created)
├── demo_memory.json      # 📋 Demo memory structure
└── README.md            # 📖 This file
```

## 💾 **Memory JSON Structure**

```json
{
  "memories": [
    {
      "id": 1,
      "content": "Meeting tomorrow 3 PM",
      "type": "user_note",
      "timestamp": "2024-01-15 14:30:00",
      "created_at": "2024-01-15T14:30:00"
    }
  ],
  "tasks": [
    {
      "id": 1,
      "description": "Complete project",
      "completed": false,
      "timer_minutes": 30,
      "timer_end": 1705323000
    }
  ],
  "settings": {
    "preferred_language": "hinglish",
    "voice_model": 2
  }
}
```

## 🎯 **Advanced Usage Examples**

### **Memory Management**
```
"RJ yaad rakh WiFi password MyHome123"     → Stores in memory
"RJ yaad hai WiFi"                         → Recalls: "WiFi password MyHome123"
"RJ bhool ja WiFi"                         → Removes WiFi-related memories
```

### **Task Management with Timers**
```
"RJ task add kar exercise 45 minutes"      → Creates task with 45-min timer
"RJ new task buy groceries"                → Simple task without timer
"RJ timer laga 20 minutes study"           → 20-minute study timer
```

### **Intelligent Information Retrieval**
```
"RJ batao Taj Mahal ke bare mein"         → Wikipedia search + memory storage
"RJ kya hai machine learning"              → AI explanation + memory storage
"RJ yaad hai machine learning"             → Recalls from memory
```

### **GUI Interaction**
- Click **🎤 Start Listening** to activate voice recognition
- View real-time logs in the **Console Output**
- Monitor stored memories in the **Memory Bank**
- Track active tasks and timers in **Task Manager**
- Control everything with the **Control Panel**

## 🔧 **Technical Features**

### **🗣️ Voice Recognition**
- **Dual language** support (Hindi + English)
- **Voice model [2]** as requested
- **Noise cancellation** and audio calibration
- **Continuous listening** mode with GUI

### **🧠 AI Integration**
- **DeepSeek API** with your key
- **Context-aware** responses using memory
- **Conversation history** tracking
- **Hinglish personality** with natural responses

### **💾 Data Persistence**
- **JSON-based storage** for all data
- **Automatic backups** with timestamps
- **Import/Export** capabilities
- **Cross-session continuity**

### **⏰ Timer System**
- **Background monitoring** of all active timers
- **Multi-timer support** with individual notifications
- **Visual countdown** in GUI
- **Audio alerts** when complete

## 🛠️ **Installation & Setup**

### **Dependencies**
```bash
pip install openai speechrecognition pyttsx3 pyaudio psutil requests python-dotenv wikipedia matplotlib numpy pillow
```

### **Audio Setup (Linux)**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio espeak espeak-data libespeak1 libespeak-dev
```

### **Quick Setup**
```bash
chmod +x setup.sh
./setup.sh
python3 run_rj.py
```

## 🎮 **GUI Controls**

| Button | Function |
|--------|----------|
| 🎤 Start Listening | Activate voice recognition |
| 🔇 Stop Listening | Deactivate voice recognition |
| 🧠 Clear Memory | Remove all stored memories |
| 📋 Export Logs | Save console output to file |
| ✅ Complete Task | Mark selected task as done |
| 🗑️ Remove Task | Delete selected task |

## 🔒 **Security & Privacy**

- **Local storage** - All data stays on your machine
- **API key security** - Stored in environment file
- **Memory encryption** - Optional JSON encryption
- **Safe commands** - Confirmation for system operations

## 🎨 **Customization**

### **Voice Settings**
- Voice model selection (uses [2] as requested)
- Speech rate and volume control
- Language preference (Hindi/English/Hinglish)

### **GUI Themes**
- Dark JARVIS theme (default)
- Customizable colors and animations
- Resizable interface components

### **Memory Categories**
- user_note, wikipedia, voice_note, task
- Custom categories can be added
- Searchable and filterable

## 📱 **Available Assistants**

1. **🎙️ Advanced RJ** (advanced_rj.py) - Full featured with GUI
2. **📱 Basic RJ** (rj_assistant.py) - Simple voice assistant  
3. **🖥️ Console Mode** - Advanced features without GUI

## ❓ **Troubleshooting**

### **Voice Recognition Issues**
```bash
# Test microphone
arecord -l

# Check audio permissions
sudo usermod -a -G audio $USER

# Install additional codecs
sudo apt-get install ubuntu-restricted-extras
```

### **GUI Issues**
```bash
# Install tkinter if missing
sudo apt-get install python3-tk

# For display issues
export DISPLAY=:0
```

### **Memory File Issues**
- File created automatically on first run
- Located at `./rj_memory.json`
- Backup created on each update

---

## 🏃 **Quick Start Commands**

```bash
# Setup everything
./setup.sh

# Start with launcher (easiest)
python3 run_rj.py

# Direct start with GUI
python3 advanced_rj.py

# Console mode only
python3 advanced_rj.py --no-gui
```

**🎙️ "RJ ready hai! GUI mein sabkuch dikh raha hai. Boliye kya kaam hai?"**

---

**Made with ❤️ for advanced voice-controlled computing**

**Features:** JARVIS GUI • JSON Memory • Task Timers • Hinglish Voice • Wikipedia • AI Chat
#!/usr/bin/env python3
"""
Extra Features for RJ Assistant
Additional utilities and advanced capabilities
"""

import os
import json
import random
import requests
from datetime import datetime
import subprocess

class ExtraFeatures:
    def __init__(self):
        """Initialize extra features"""
        self.setup_features()

    def setup_features(self):
        """Setup all extra features"""
        self.motivational_quotes = [
            "Safalta wo hai jo tumhare iraade ko badhaye, na ki tumhari ego ko!",
            "Har mushkil ka samadhan ek nayi shururat mein chhupa hota hai.",
            "Sapne wo nahi jo aap sote waqt dekhte hain, sapne wo hain jo aapko sone nahi dete!",
            "Koshish karne walon ki kabhi haar nahi hoti!",
            "Kamiyabi ka raaz hai - kabhi haar na manna!",
            "Jo log sapne dekhte hain, sirf wahi log unhe hakiqat bana sakte hain.",
            "Mushkilat sirf tab tak mushkil hain jab tak aap unka samna nahi karte.",
            "Aapki thinking aapki life change kar sakti hai!"
        ]
        
        self.productivity_tips = [
            "25 minute kaam karo, 5 minute break lo - ye Pomodoro technique hai!",
            "Subah 5 baje uthna aapki productivity 200% badha sakta hai",
            "Daily 3 important tasks pick karo aur unhe first complete karo",
            "Phone ko silent mode mein rakh kar focus time banao",
            "Todo list paper pe likho, digital se zyada effective hai",
            "Deep work ke liye 2 hour ka continuous time block banao"
        ]
        
        self.health_tips = [
            "Har ghante mein 5 minute walk karo agar desk job hai",
            "20-20-20 rule: har 20 minute mein 20 feet door 20 second dekhiye",
            "Din mein 8-10 glass paani jaroor piyo",
            "Sone se 2 ghante pehle screen time band kar do",
            "Meditation sirf 5 minute daily bhi kaafi helpful hai",
            "Stairs use karo lift ki jagah jahan possible ho"
        ]

    def get_motivational_quote(self):
        """Get random motivational quote"""
        return random.choice(self.motivational_quotes)

    def get_productivity_tip(self):
        """Get productivity tip"""
        return random.choice(self.productivity_tips)

    def get_health_tip(self):
        """Get health tip"""
        return random.choice(self.health_tips)

    def get_system_info(self):
        """Get system information"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Battery (if available)
            try:
                battery = psutil.sensors_battery()
                battery_percent = battery.percent if battery else "N/A"
            except:
                battery_percent = "N/A"
            
            info = f"System Info: CPU {cpu_percent}%, RAM {memory_percent}%, Disk {disk_percent:.1f}%"
            if battery_percent != "N/A":
                info += f", Battery {battery_percent}%"
            
            return info
            
        except Exception as e:
            return f"System info nahi mil paya: {str(e)}"

    def get_network_info(self):
        """Get network connectivity info"""
        try:
            # Test internet connectivity
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                return "Internet connection: Active ✅"
            else:
                return "Internet connection: Issues detected ⚠️"
        except:
            return "Internet connection: Offline ❌"

    def create_qr_code(self, text: str, filename: str = "qr_code.png"):
        """Create QR code for text"""
        try:
            import qrcode
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filename)
            return f"QR code saved as {filename}"
        except ImportError:
            return "QR code library not installed. Install with: pip install qrcode[pil]"
        except Exception as e:
            return f"QR code create nahi kar paya: {str(e)}"

    def text_to_speech_file(self, text: str, filename: str = "speech.wav"):
        """Convert text to speech file"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text, filename)
            engine.runAndWait()
            return f"Speech file saved as {filename}"
        except Exception as e:
            return f"Speech file nahi bana paya: {str(e)}"

    def generate_password(self, length: int = 12):
        """Generate secure password"""
        import string
        import secrets
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return f"Generated password: {password}"

    def get_random_exercise(self):
        """Get random exercise suggestion"""
        exercises = [
            "10 Push-ups kar sakte ho abhi",
            "30 second plank hold karo",
            "20 Jumping jacks karo energy ke liye",
            "Neck rotation - 5 times clockwise, 5 times anti-clockwise",
            "Shoulder shrugs - 10 times karo tension release karne ke liye",
            "Deep breathing - 5 deep breaths lo stress kam karne ke liye",
            "Wall push-ups - 15 times karo office mein bhi kar sakte ho",
            "Calf raises - 20 times karo blood circulation ke liye"
        ]
        return random.choice(exercises)

    def get_brain_teaser(self):
        """Get brain teaser/riddle"""
        teasers = [
            "Main hoon har ghar mein, par koi mujhe dekh nahi sakta. Main raat ko aata hun, subah chala jata hun. Kaun hun main? (Answer: Andhera/Darkness)",
            "Ek cheez hai jo jitni lambi hoti hai, utni hi choti shadow banati hai. Kya hai wo? (Answer: Candle)",
            "Main wo hun jo sabke paas hai, par koi mujhe chhoo nahi sakta. Main time ke saath badta hun. Kaun hun main? (Answer: Age/Umar)",
            "Ek ladka apne baap ka beta hai, lekin uske baap ka beta nahi hai. Kaise? (Answer: Wo ladki hai)",
            "Kya cheez hai jo paani mein gir jaaye to sukh jaati hai? (Answer: Aag)"
        ]
        return random.choice(teasers)

    def get_coding_tip(self):
        """Get coding/programming tip"""
        tips = [
            "Code likhne se pehle plan karo - pseudocode likhna helpful hai",
            "Variable names meaningful rakho - 'x' ki jagah 'user_count' use karo",
            "Comments jaroor likho - future mein aap hi confuse ho jaoge",
            "Version control (Git) use karo - har project ke liye",
            "Code review karo - doosron ka code padhna skills improve karta hai",
            "Debugging skill develop karo - print statements aur breakpoints use karo",
            "Clean code likho - readable code is maintainable code",
            "Practice karo daily - LeetCode, HackerRank pe problems solve karo"
        ]
        return random.choice(tips)

    def get_current_trends(self):
        """Get current technology trends (mock data)"""
        trends = [
            "AI aur Machine Learning sabse hot topics hain abhi",
            "Cloud computing demand bahut high hai - AWS, Azure sikho",
            "Cybersecurity mein bahut opportunities hain",
            "Mobile app development still in demand - Flutter, React Native",
            "DevOps skills bahut valuable hain - Docker, Kubernetes sikho",
            "Data Science aur Analytics growing field hai",
            "Blockchain technology future mein important hoga",
            "IoT (Internet of Things) expanding rapidly hai"
        ]
        return random.choice(trends)

    def calculate_tip(self, bill_amount: float, tip_percentage: float = 15.0):
        """Calculate tip amount"""
        tip_amount = (bill_amount * tip_percentage) / 100
        total_amount = bill_amount + tip_amount
        return f"Bill: ₹{bill_amount}, Tip ({tip_percentage}%): ₹{tip_amount:.2f}, Total: ₹{total_amount:.2f}"

    def convert_currency(self, amount: float, from_currency: str = "USD", to_currency: str = "INR"):
        """Convert currency (mock rates)"""
        # Mock exchange rates
        rates = {
            "USD_TO_INR": 83.0,
            "EUR_TO_INR": 90.0,
            "GBP_TO_INR": 105.0,
            "INR_TO_USD": 0.012,
            "INR_TO_EUR": 0.011,
            "INR_TO_GBP": 0.0095
        }
        
        rate_key = f"{from_currency}_TO_{to_currency}"
        if rate_key in rates:
            converted = amount * rates[rate_key]
            return f"{amount} {from_currency} = {converted:.2f} {to_currency} (approximate)"
        else:
            return "Currency conversion rate not available"

    def get_word_of_the_day(self):
        """Get word of the day with meaning"""
        words = [
            {"word": "Perseverance", "meaning": "Mushkilon ke bawajood mehnat karta rehna", "hindi": "दृढ़ता"},
            {"word": "Resilience", "meaning": "Problems se jaldi recover hona", "hindi": "लचीलापन"},
            {"word": "Innovation", "meaning": "Naye ideas aur solutions dhundna", "hindi": "नवाचार"},
            {"word": "Efficiency", "meaning": "Kam time mein zyada kaam karna", "hindi": "दक्षता"},
            {"word": "Collaboration", "meaning": "Team work aur saath mein kaam karna", "hindi": "सहयोग"},
            {"word": "Optimism", "meaning": "Har situation mein positive thinking", "hindi": "आशावाद"}
        ]
        
        word_data = random.choice(words)
        return f"Word of the day: {word_data['word']} ({word_data['hindi']}) - {word_data['meaning']}"

# Initialize extra features
extra_features = ExtraFeatures()
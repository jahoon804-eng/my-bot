"""
ТВОЙ ЛИЧНЫЙ AI-МЕССЕНДЖЕР
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
import threading
import requests
from datetime import datetime

# НАСТРОЙКИ
LLAMA_API_URL = "http://localhost:8080/completion"
SYSTEM_PROMPT = "Ты верный друг и помощник. Общаешься на русском."

class MessageBubble(MDCard):
    def __init__(self, text, is_user=True, time_str=""):
        super().__init__()
        self.size_hint_x = None
        self.width = dp(280)
        self.padding = dp(12)
        self.radius = dp(18)
        self.elevation = 1
        
        if is_user:
            self.md_bg_color = get_color_from_hex("#6C63FF")
            self.pos_hint = {"right": 1}
            self.radius = [dp(18), dp(18), dp(4), dp(18)]
        else:
            self.md_bg_color = get_color_from_hex("#1E1E2E")
            self.pos_hint = {"right": 0}
            self.radius = [dp(18), dp(18), dp(18), dp(4)]
        
        label = MDLabel(
            text=text,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_size="15sp",
            size_hint_y=None,
            height=dp(40)
        )
        
        time_label = MDLabel(
            text=time_str,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.5),
            font_size="11sp",
            size_hint=(1, None),
            height=dp(16),
            halign="right"
        )
        
        layout = MDBoxLayout(orientation="vertical", spacing=dp(4))
        layout.add_widget(label)
        layout.add_widget(time_label)
        self.add_widget(layout)

class ChatScreen(MDScreen):
    def __init__(self):
        super().__init__()
        self.md_bg_color = get_color_from_hex("#0F0F1A")
        
        self.layout = MDBoxLayout(orientation="vertical")
        
        # Шапка
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=get_color_from_hex("#1A1A2E"),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(12)
        )
        
        avatar = MDIconButton(
            icon="robot",
            icon_size="24sp",
            theme_icon_color="Custom",
            icon_color=get_color_from_hex("#6C63FF")
        )
        
        info = MDBoxLayout(orientation="vertical", spacing=0)
        name = MDLabel(
            text="Мой ИИ",
            font_size="16sp",
            bold=True,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(22)
        )
        status = MDLabel(
            text="онлайн",
            font_size="12sp",
            theme_text_color="Custom",
            text_color=(0.3, 1, 0.3, 1),
            size_hint_y=None,
            height=dp(16)
        )
        info.add_widget(name)
        info.add_widget(status)
        
        clear_btn = MDIconButton(
            icon="delete-outline",
            icon_size="22sp",
            theme_icon_color="Custom",
            icon_color=(0.7, 0.7, 0.7, 1),
            on_release=lambda x: self.clear_chat()
        )
        
        header.add_widget(avatar)
        header.add_widget(info)
        header.add_widget(MDBoxLayout(size_hint_x=1))
        header.add_widget(clear_btn)
        
        self.layout.add_widget(header)
        
        # Сообщения
        self.scroll = MDScrollView(do_scroll_x=False)
        self.messages_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            adaptive_height=True
        )
        self.scroll.add_widget(self.messages_layout)
        self.layout.add_widget(self.scroll)
        
        # Поле ввода
        input_area = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=get_color_from_hex("#1A1A2E"),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(8)
        )
        
        self.text_input = MDTextField(
            hint_text="Сообщение...",
            mode="round",
            size_hint_x=0.85,
            font_size="15sp",
            text_color=(1, 1, 1, 1),
            fill_color=(0.12, 0.12, 0.2, 1)
        )
        
        send_btn = MDIconButton(
            icon="send",
            icon_size="24sp",
            theme_icon_color="Custom",
            icon_color=get_color_from_hex("#6C63FF"),
            on_release=lambda x: self.send_message()
        )
        
        input_area.add_widget(self.text_input)
        input_area.add_widget(send_btn)
        self.layout.add_widget(input_area)
        
        self.add_widget(self.layout)
        
        Clock.schedule_once(lambda dt: self.add_bot_message("Привет! Я твой ИИ. Спрашивай!"), 0.5)
    
    def add_user_message(self, text):
        now = datetime.now().strftime("%H:%M")
        bubble = MessageBubble(text=text, is_user=True, time_str=now)
        self.messages_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)
    
    def add_bot_message(self, text):
        now = datetime.now().strftime("%H:%M")
        bubble = MessageBubble(text=text, is_user=False, time_str=now)
        self.messages_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 0), 0.1)
    
    def send_message(self):
        text = self.text_input.text.strip()
        if not text:
            return
        
        self.add_user_message(text)
        self.text_input.text = ""
        
        typing = MessageBubble(text="...", is_user=False, time_str="")
        self.messages_layout.add_widget(typing)
        
        threading.Thread(target=self.query_llama, args=(text, typing), daemon=True).start()
    
    def query_llama(self, prompt, typing_bubble):
        try:
            full = f"{SYSTEM_PROMPT}\n\nПользователь: {prompt}\nАссистент:"
            
            response = requests.post(
                LLAMA_API_URL,
                json={"prompt": full, "temperature": 0.7, "max_tokens": 1000, "stop": ["Пользователь:"]},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("content", result.get("text", ""))
                answer = answer.replace(full, "").strip()
            else:
                answer = f"Ошибка: {response.status_code}"
                
        except Exception as e:
            answer = "Не могу подключиться. Проверь сервер."
        
        Clock.schedule_once(lambda dt: self.update_bot_message(answer, typing_bubble), 0)
    
    def update_bot_message(self, text, old_bubble):
        self.messages_layout.remove_widget(old_bubble)
        self.add_bot_message(text)
    
    def clear_chat(self):
        self.messages_layout.clear_widgets()
        self.add_bot_message("Чат очищен!")

class MyAIMessenger(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.title = "Мой ИИ"
        return ChatScreen()

if __name__ == "__main__":
    MyAIMessenger().run()

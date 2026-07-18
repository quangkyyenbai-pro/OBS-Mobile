import os
import sys
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from plyer import filechooser

# Đường dẫn đến file ffmpeg đã được đóng gói trong thư mục gốc của app
ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg')

class OBSMobileUI(BoxLayout):
    def __init__(self, **kwargs):
        # Tăng padding và spacing để giao diện thoáng hơn
        super().__init__(orientation='vertical', padding=30, spacing=15, **kwargs)
        
        self.process = None
        self.selected_path = None

        # 1. Nhập RTMP
        self.add_widget(Label(text="[b]Link RTMP:[/b]", markup=True, size_hint_y=None, height=40))
        self.rtmp_url = TextInput(hint_text='rtmp://...', multiline=False, size_hint_y=None, height=50)
        self.add_widget(self.rtmp_url)
        
        # 2. Chọn file
        self.add_widget(Widget(size_hint_y=None, height=10))
        self.btn_select = Button(text='Chọn Video/Nhạc nền', size_hint_y=None, height=50, background_color=(0.2, 0.6, 1, 1))
        self.btn_select.bind(on_press=self.select_file)
        self.add_widget(self.btn_select)
        
        # 3. Điều khiển âm lượng
        self.add_widget(Widget(size_hint_y=None, height=10))
        self.add_widget(Label(text="Âm lượng nhạc/video:", size_hint_y=None, height=30))
        self.vol_slider = Slider(min=0, max=100, value=50, size_hint_y=None, height=50)
        self.add_widget(self.vol_slider)
        
        # 4. Switch tắt tiếng
        ctrl_layout = BoxLayout(size_hint_y=None, height=50, spacing=20)
        ctrl_layout.add_widget(Label(text="Tắt tiếng Video gốc:"))
        self.mute_switch = Switch(active=False)
        ctrl_layout.add_widget(self.mute_switch)
        self.add_widget(ctrl_layout)
        
        # Khoảng đệm để đẩy nút bấm xuống dưới
        self.add_widget(Widget())
        
        # 5. Khu vực nút bấm
        btn_layout = BoxLayout(size_hint_y=None, height=70, spacing=20)
        self.btn_live = Button(text='Bắt đầu Live', background_color=(0, 0.8, 0, 1), on_press=self.start_live)
        self.btn_stop = Button(text='Dừng Live', background_color=(0.8, 0, 0, 1), on_press=self.stop_live, disabled=True)
        btn_layout.add_widget(self.btn_live)
        btn_layout.add_widget(self.btn_stop)
        self.add_widget(btn_layout)
        
        # 6. Trạng thái
        self.status_label = Label(text="Trạng thái: Sẵn sàng", size_hint_y=None, height=40)
        self.add_widget(self.status_label)

    def select_file(self, instance):
        filechooser.open_file(on_selection=self.on_file_selected)

    def on_file_selected(self, selection):
        if selection:
            self.selected_path = selection[0]
            self.status_label.text = "Đã chọn: " + os.path.basename(self.selected_path)

    def start_live(self, instance):
        if not self.rtmp_url.text:
            self.status_label.text = "Lỗi: Nhập RTMP trước!"
            return

        volume = self.vol_slider.value / 100.0
        # Lệnh ffmpeg
        cmd = [ffmpeg_path, "-f", "android_camera", "-i", "0"]
        
        if self.selected_path:
            cmd.extend(["-i", self.selected_path])
            cmd.extend(["-filter_complex", f"[1:a]volume={volume}[a1]", "-map", "0:v", "-map", "[a1]"])
        
        cmd.extend(["-c:v", "h264_mtk", "-b:v", "4000k", "-preset", "ultrafast", "-c:a", "aac", "-f", "flv", self.rtmp_url.text])
        
        try:
            self.process = subprocess.Popen(cmd)
            self.btn_live.disabled = True
            self.btn_stop.disabled = False
            self.status_label.text = "Đang Live..."
        except Exception as e:
            self.status_label.text = f"Lỗi: {str(e)}"

    def stop_live(self, instance):
        if self.process:
            self.process.terminate()
            self.process = None
            self.btn_live.disabled = False
            self.btn_stop.disabled = True
            self.status_label.text = "Đã dừng Live"

class MainApp(App):
    def build(self):
        return OBSMobileUI()

if __name__ == '__main__':
    MainApp().run()

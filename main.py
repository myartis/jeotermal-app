from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.slider import Slider
import numpy as np

class JeotermalApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Başlık
        self.root.add_widget(Label(
            text='🔥 JEOTERMAL HESAPLAYICI',
            font_size='24sp',
            bold=True,
            color=(0.1, 0.4, 0.7, 1),
            size_hint_y=None,
            height=60
        ))
        
        # Girdiler
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None, height=200)
        
        self.debi = self.ekle_input(grid, 'Debi (ton/s):', '300')
        self.sicaklik = self.ekle_input(grid, 'Sıcaklık (°C):', '150')
        self.basinç_giris = self.ekle_input(grid, 'Giriş Basınç (bar):', '6')
        self.basinç_flash = self.ekle_input(grid, 'Flash Basınç (bar):', '3')
        
        self.root.add_widget(grid)
        
        # Slider'lar
        self.root.add_widget(Label(text='Buhar Hızı (m/s):', color=(0.2,0.2,0.2,1)))
        self.buhar_slider = Slider(min=20, max=50, value=30)
        self.root.add_widget(self.buhar_slider)
        
        self.root.add_widget(Label(text='Brine Hızı (m/s):', color=(0.2,0.2,0.2,1)))
        self.brine_slider = Slider(min=1.5, max=4, value=2.5)
        self.root.add_widget(self.brine_slider)
        
        # Sonuç alanı
        self.sonuc = Label(
            text='HESAPLAMAK İÇİN\nBUTONA BASIN',
            font_size='16sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=150
        )
        self.root.add_widget(self.sonuc)
        
        # Hesapla butonu
        btn = Button(
            text='HESAPLA',
            size_hint_y=None,
            height=70,
            background_color=(0.2, 0.7, 0.3, 1),
            font_size='20sp',
            bold=True
        )
        btn.bind(on_press=self.hesapla)
        self.root.add_widget(btn)
        
        return self.root
    
    def ekle_input(self, grid, etiket, varsayilan):
        grid.add_widget(Label(text=etiket, color=(0.2, 0.2, 0.2, 1), font_size='14sp'))
        kutu = TextInput(text=varsayilan, multiline=False, input_filter='float', font_size='18sp', halign='center')
        grid.add_widget(kutu)
        return kutu
    
    def hesapla(self, instance):
        try:
            debi = float(self.debi.text)
            sicaklik = float(self.sicaklik.text)
            P_giris = float(self.basinç_giris.text)
            P_flash = float(self.basinç_flash.text)
            v_buhar = self.buhar_slider.value
            v_brine = self.brine_slider.value
            
            m_kg_s = debi * 1000 / 3600
            
            h_giris, h_sivi, h_buharlasma = 632.2, 561.4, 2163.2
            buhar_kesri = (h_giris - h_sivi) / h_buharlasma
            
            m_buhar = m_kg_s * buhar_kesri
            m_brine = m_kg_s * (1 - buhar_kesri)
            
            Q_buhar = m_buhar / 1.62
            Q_brine = m_brine / 943.0
            
            def boru_hesap(Q, hiz):
                A = Q / hiz
                D_hesap = ((4 * A) / 3.14159) ** 0.5 * 1000 / 25.4
                standartlar = [2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24]
                for s in standartlar:
                    if s >= D_hesap:
                        return s, D_hesap
                return 24, D_hesap
            
            buhar_boru, buhar_hesap = boru_hesap(Q_buhar, v_buhar)
            brine_boru, brine_hesap = boru_hesap(Q_brine, v_brine)
            
            V_akü = (Q_buhar + Q_brine) * 3 * 60
            D_akü = ((4 * V_akü) / (3.14159 * 2.5)) ** (1/3)
            L_akü = 2.5 * D_akü
            
            V_sep = Q_brine * 1.5 * 60
            D_sep = (V_sep / (0.625 * 3.14159)) ** (1/3)
            H_sep = 3.0 * D_sep
            
            sonuc_metni = f"""✅ SONUÇLAR:

📊 AKIŞLAR:
• Buhar Kesri: %{buhar_kesri*100:.2f}
• Buhar: {m_buhar*3.6:.1f} ton/saat
• Brine: {m_brine*3.6:.1f} ton/saat

🔧 BORULAR:
• Buhar: {buhar_boru}\" (hesap: {buhar_hesap:.1f}\")
• Brine: {brine_boru}\" (hesap: {brine_hesap:.1f}\")

🏭 EKİPMANLAR:
• Akümülatör: {L_akü:.2f}m × {D_akü:.2f}m
• Seperatör: {H_sep:.2f}m × {D_sep:.2f}m"""
            
            self.sonuc.text = sonuc_metni
            self.sonuc.color = (0.1, 0.5, 0.2, 1)
            self.sonuc.font_size = '14sp'
            
        except ValueError:
            self.sonuc.text = '❌ HATA:\nGeçerli sayılar girin!'
            self.sonuc.color = (0.8, 0.2, 0.2, 1)

if __name__ == '__main__':
    JeotermalApp().run()

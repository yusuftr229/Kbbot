import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime
import os
import tempfile
from typing import Optional, List

class QuizModal1(discord.ui.Modal, title='Soru Oluştur - 1/2'):
    def __init__(self):
        super().__init__()

    soru = discord.ui.TextInput(
        label='Soru',
        placeholder='Sorunuzu yazın...',
        required=True,
        max_length=500
    )
    
    secenek1 = discord.ui.TextInput(
        label='Seçenek 1',
        placeholder='İlk seçeneği yazın...',
        required=True,
        max_length=100
    )
    
    secenek2 = discord.ui.TextInput(
        label='Seçenek 2',
        placeholder='İkinci seçeneği yazın...',
        required=True,
        max_length=100
    )
    
    secenek3 = discord.ui.TextInput(
        label='Seçenek 3 (Opsiyonel)',
        placeholder='Üçüncü seçeneği yazın...',
        required=False,
        max_length=100
    )
    
    secenek4 = discord.ui.TextInput(
        label='Seçenek 4 (Opsiyonel)',
        placeholder='Dördüncü seçeneği yazın...',
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        seçenekler = [self.secenek1.value, self.secenek2.value]
        
        if self.secenek3.value:
            seçenekler.append(self.secenek3.value)
        if self.secenek4.value:
            seçenekler.append(self.secenek4.value)
            
        # İkinci modal için view oluştur
        view = ContinueView(self.soru.value, seçenekler)
        
        embed = discord.Embed(
            title="Daha Fazla Seçenek Eklemek İstiyor Musunuz?",
            description=f"**Soru:** {self.soru.value}\n\n" + 
                       "**Mevcut Seçenekler:**\n" +
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(seçenekler)]),
            color=0x0099ff
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class QuizModal2(discord.ui.Modal, title='Ek Seçenekler - 2/2'):
    def __init__(self, soru: str, mevcut_seçenekler: List[str]):
        super().__init__()
        self.soru = soru
        self.mevcut_seçenekler = mevcut_seçenekler

    secenek5 = discord.ui.TextInput(
        label='Seçenek 5 (Opsiyonel)',
        placeholder='Beşinci seçeneği yazın...',
        required=False,
        max_length=100
    )
    
    secenek6 = discord.ui.TextInput(
        label='Seçenek 6 (Opsiyonel)',
        placeholder='Altıncı seçeneği yazın...',
        required=False,
        max_length=100
    )
    
    secenek7 = discord.ui.TextInput(
        label='Seçenek 7 (Opsiyonel)',
        placeholder='Yedinci seçeneği yazın...',
        required=False,
        max_length=100
    )
    
    secenek8 = discord.ui.TextInput(
        label='Seçenek 8 (Opsiyonel)',
        placeholder='Sekizinci seçeneği yazın...',
        required=False,
        max_length=100
    )
    
    secenek9 = discord.ui.TextInput(
        label='Seçenek 9 (Opsiyonel)',
        placeholder='Dokuzuncu seçeneği yazın...',
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        seçenekler = self.mevcut_seçenekler.copy()
        
        ek_seçenekler = [
            self.secenek5.value, self.secenek6.value, self.secenek7.value,
            self.secenek8.value, self.secenek9.value
        ]
        
        for seçenek in ek_seçenekler:
            if seçenek:
                seçenekler.append(seçenek)
        
        view = ContinueView2(self.soru, seçenekler)
        
        embed = discord.Embed(
            title="Son Seçenekler Eklemek İstiyor Musunuz?",
            description=f"**Soru:** {self.soru}\n\n" + 
                       "**Mevcut Seçenekler:**\n" +
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(seçenekler)]),
            color=0x0099ff
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class QuizModal3(discord.ui.Modal, title='Son Seçenekler - 3/3'):
    def __init__(self, soru: str, mevcut_seçenekler: List[str]):
        super().__init__()
        self.soru = soru
        self.mevcut_seçenekler = mevcut_seçenekler

    secenek10 = discord.ui.TextInput(
        label='Seçenek 10 (Opsiyonel)',
        placeholder='Onuncu seçeneği yazın...',
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        seçenekler = self.mevcut_seçenekler.copy()
        
        if self.secenek10.value:
            seçenekler.append(self.secenek10.value)
        
        view = DogruCevapView(self.soru, seçenekler)
        
        embed = discord.Embed(
            title="Doğru Cevabı Seçin",
            description=f"**Soru:** {self.soru}\n\n" + 
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(seçenekler)]),
            color=0x00ff00
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ContinueView(discord.ui.View):
    def __init__(self, soru: str, seçenekler: List[str]):
        super().__init__(timeout=300)
        self.soru = soru
        self.seçenekler = seçenekler

    @discord.ui.button(label="Evet, daha fazla seçenek ekle", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_more_options(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = QuizModal2(self.soru, self.seçenekler)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Hayır, devam et", style=discord.ButtonStyle.secondary, emoji="✅")
    async def continue_quiz(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = DogruCevapView(self.soru, self.seçenekler)
        
        embed = discord.Embed(
            title="Doğru Cevabı Seçin",
            description=f"**Soru:** {self.soru}\n\n" + 
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(self.seçenekler)]),
            color=0x00ff00
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class ContinueView2(discord.ui.View):
    def __init__(self, soru: str, seçenekler: List[str]):
        super().__init__(timeout=300)
        self.soru = soru
        self.seçenekler = seçenekler

    @discord.ui.button(label="Son seçeneği ekle", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_last_option(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = QuizModal3(self.soru, self.seçenekler)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Devam et", style=discord.ButtonStyle.secondary, emoji="✅")
    async def continue_quiz(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = DogruCevapView(self.soru, self.seçenekler)
        
        embed = discord.Embed(
            title="Doğru Cevabı Seçin",
            description=f"**Soru:** {self.soru}\n\n" + 
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(self.seçenekler)]),
            color=0x00ff00
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class DogruCevapView(discord.ui.View):
    def __init__(self, soru: str, seçenekler: List[str]):
        super().__init__(timeout=300)
        self.soru = soru
        self.seçenekler = seçenekler
        self.doğru_cevap = None
        
        # Dinamik butonlar oluştur (maksimum 25 buton limiti)
        for i, seçenek in enumerate(seçenekler[:25]):  # Discord limiti
            button = discord.ui.Button(
                label=f"{i+1}. {seçenek[:50]}",
                style=discord.ButtonStyle.secondary,
                custom_id=f"dogru_{i}",
                row=i // 5  # Her satırda 5 buton
            )
            button.callback = self.dogru_cevap_callback
            self.add_item(button)

    async def dogru_cevap_callback(self, interaction: discord.Interaction):
        button_id = interaction.data['custom_id']
        self.doğru_cevap = int(button_id.split('_')[1])
        
        view = SureModal(self.soru, self.seçenekler, self.doğru_cevap)
        
        embed = discord.Embed(
            title="Süre Belirleyin",
            description=f"**Soru:** {self.soru}\n**Doğru Cevap:** {self.seçenekler[self.doğru_cevap]}",
            color=0x0099ff
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class SureModal(discord.ui.View):
    def __init__(self, soru: str, seçenekler: List[str], doğru_cevap: int):
        super().__init__(timeout=300)
        self.soru = soru
        self.seçenekler = seçenekler
        self.doğru_cevap = doğru_cevap
        
    @discord.ui.button(label="Süre Belirle", style=discord.ButtonStyle.primary, emoji="⏱️")
    async def set_time(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TimeInputModal(self.soru, self.seçenekler, self.doğru_cevap)
        await interaction.response.send_modal(modal)

class TimeInputModal(discord.ui.Modal, title='Anket Süresini Belirleyin'):
    def __init__(self, soru: str, seçenekler: List[str], doğru_cevap: int):
        super().__init__()
        self.soru = soru
        self.seçenekler = seçenekler
        self.doğru_cevap = doğru_cevap

    sure_input = discord.ui.TextInput(
        label='Süre (saniye)',
        placeholder='10-3600 arasında saniye cinsinden süre girin',
        required=True,
        max_length=4,
        min_length=1
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            sure = int(self.sure_input.value)
            
            if sure < 10:
                await interaction.response.send_message("❌ Minimum süre 10 saniye olmalıdır!", ephemeral=True)
                return
            elif sure > 86400:
                await interaction.response.send_message("❌ Maksimum süre 3600 saniye (1 saat) olmalıdır!", ephemeral=True)
                return
                
        except ValueError:
            await interaction.response.send_message("❌ Lütfen geçerli bir sayı girin!", ephemeral=True)
            return
        
        # Anket başlat
        quiz_view = QuizVotingView(self.soru, self.seçenekler, self.doğru_cevap, sure, interaction.user.id)
        
        # Emojiler listesi genişletildi
        emojiler = ['🅰️', '🅱️', '🅾️', '💠', '🔵', '🟢', '🟡', '🟠', '🔴', '🟣']
        
        embed = discord.Embed(
            title="📊 ANKET",
            description=f"**{self.soru}**\n\n" + 
                       "\n".join([f"{emojiler[i] if i < len(emojiler) else f'{i+1}️⃣'} {seçenek}" 
                                 for i, seçenek in enumerate(self.seçenekler)]),
            color=0xff6b35,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Süre: {sure} saniye | Doğru cevap gizli")
        
        await interaction.response.edit_message(embed=embed, view=quiz_view)
        
        # Anket bitirme görevi başlat
        asyncio.create_task(quiz_view.finish_quiz(interaction, sure))

class QuizVotingView(discord.ui.View):
    def __init__(self, soru: str, seçenekler: List[str], doğru_cevap: int, sure: int, quiz_owner_id: int):
        super().__init__(timeout=sure + 10)
        self.soru = soru
        self.seçenekler = seçenekler
        self.doğru_cevap = doğru_cevap
        self.sure = sure
        self.quiz_owner_id = quiz_owner_id
        self.oylar = {}  # user_id: seçenek_index
        self.finished = False
        
        # Emojiler listesi genişletildi
        emojis = ['🅰️', '🅱️', '🅾️', '💠', '🔵', '🟢', '🟡', '🟠', '🔴', '🟣']
        
        # Maksimum 25 buton (Discord limiti)
        for i, seçenek in enumerate(seçenekler[:25]):
            button = discord.ui.Button(
                emoji=emojis[i] if i < len(emojis) else None,
                label=f"{i+1}. {seçenek[:45]}" if i >= len(emojis) else seçenek[:50],
                style=discord.ButtonStyle.primary,
                custom_id=f"vote_{i}",
                row=i // 5  # Her satırda 5 buton
            )
            button.callback = self.vote_callback
            self.add_item(button)

    async def vote_callback(self, interaction: discord.Interaction):
        if self.finished:
            await interaction.response.send_message("⏰ Anket süresi dolmuş!", ephemeral=True)
            return
            
        button_id = interaction.data['custom_id']
        seçenek_index = int(button_id.split('_')[1])
        
        self.oylar[interaction.user.id] = seçenek_index
        
        await interaction.response.send_message(
            f"✅ **{self.seçenekler[seçenek_index]}** seçeneğine oy verdiniz!", 
            ephemeral=True
        )

    async def finish_quiz(self, interaction: discord.Interaction, sure: int):
        await asyncio.sleep(sure)
        self.finished = True
        
        # Sonuçları hesapla
        sonuçlar = {}
        for i, seçenek in enumerate(self.seçenekler):
            sonuçlar[i] = 0
            
        for user_id, seçenek_index in self.oylar.items():
            sonuçlar[seçenek_index] += 1
            
        toplam_oy = len(self.oylar)
        
        # HTML rapor oluştur
        html_content = self.create_html_report(sonuçlar, toplam_oy)
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file_path = f.name
        
        # Discord embed güncelle - sadece anket sonlandığını belirt
        result_embed = discord.Embed(
            title="📊 ANKET SONUÇLANDI",
            description=f"**{self.soru}**\n\n✅ Anket tamamlandı!\n📊 Toplam **{toplam_oy}** oy alındı.\n📧 Detaylı sonuçlar anket sahibine DM olarak gönderildi.",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        
        # Mesajı güncelle
        await interaction.edit_original_response(embed=result_embed, view=None)
        
        # HTML dosyasını sadece anket sahibine DM olarak gönder
        try:
            quiz_owner = interaction.client.get_user(self.quiz_owner_id)
            if quiz_owner:
                file = discord.File(temp_file_path, filename=f"anket_sonuclari_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                
                # Emojiler listesi
                emojis = ['🅰️', '🅱️', '🅾️', '💠', '🔵', '🟢', '🟡', '🟠', '🔴', '🟣']
                
                # DM embed'i detaylı sonuçlarla
                dm_embed = discord.Embed(
                    title="📊 Anket Sonuçlarınız",
                    description=f"**{self.soru}**",
                    color=0x00ff00,
                    timestamp=datetime.datetime.now()
                )
                
                for i, seçenek in enumerate(self.seçenekler):
                    oy_sayısı = sonuçlar[i]
                    yüzde = (oy_sayısı / toplam_oy * 100) if toplam_oy > 0 else 0
                    is_correct = "✅" if i == self.doğru_cevap else "❌"
                    emoji = emojis[i] if i < len(emojis) else f"{i+1}️⃣"
                    
                    dm_embed.add_field(
                        name=f"{emoji} {seçenek} {is_correct}",
                        value=f"**{oy_sayısı}** oy (%{yüzde:.1f})",
                        inline=True
                    )
                
                doğru_oy = sonuçlar[self.doğru_cevap]
                başarı_oranı = (doğru_oy / toplam_oy * 100) if toplam_oy > 0 else 0
                
                dm_embed.add_field(
                    name="📈 İstatistikler", 
                    value=f"Toplam Oy: **{toplam_oy}**\nDoğru Cevap: **{self.seçenekler[self.doğru_cevap]}**\nBaşarı Oranı: **%{başarı_oranı:.1f}**", 
                    inline=False
                )
                
                await quiz_owner.send(embed=dm_embed, file=file)
            
        except discord.Forbidden:
            # DM gönderilemezse kanala bildirim yap
            await interaction.followup.send(
                f"<@{self.quiz_owner_id}> DM'iniz kapalı olduğu için HTML raporu gönderilemiyor!", 
                ephemeral=True
            )
        except Exception as e:
            print(f"DM gönderme hatası: {e}")
        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)[seçenek_index] += 1
            
        toplam_oy = len(self.oylar)
        
        # HTML rapor oluştur
        html_content = self.create_html_report(sonuçlar, toplam_oy)
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file_path = f.name
        
        # Discord embed güncelle
        result_embed = discord.Embed(
            title="📊 ANKET SONUÇLANDI",
            description=f"**{self.soru}**",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        
        emojis = ['🅰️', '🅱️', '🅾️', '💠']
        for i, seçenek in enumerate(self.seçenekler):
            oy_sayısı = sonuçlar[i]
            yüzde = (oy_sayısı / toplam_oy * 100) if toplam_oy > 0 else 0
            is_correct = "✅" if i == self.doğru_cevap else "❌"
            
            result_embed.add_field(
                name=f"{emojis[i]} {seçenek} {is_correct}",
                value=f"**{oy_sayısı}** oy (%{yüzde:.1f})",
                inline=True
            )
            
        result_embed.add_field(
            name="📈 İstatistikler", 
            value=f"Toplam: {toplam_oy} oy\nDoğru Cevap: {self.seçenekler[self.doğru_cevap]}", 
            inline=False
        )
        
        # Mesajı güncelle
        await interaction.edit_original_response(embed=result_embed, view=None)
        
        # HTML dosyasını DM olarak gönder
        try:
            file = discord.File(temp_file_path, filename=f"anket_sonuclari_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
            
            dm_embed = discord.Embed(
                title="📊 Anket Sonuçları",
                description="Detaylı anket raporunuz hazır!",
                color=0x00ff00
            )
            
            await interaction.user.send(embed=dm_embed, file=file)
            
        except discord.Forbidden:
            # DM gönderilemezse kanala bildirim yap
            await interaction.followup.send(
                f"{interaction.user.mention} DM'iniz kapalı olduğu için HTML raporu gönderilemiyor!", 
                ephemeral=True
            )
        finally:
            # Geçici dosyayı sil
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def create_html_report(self, sonuçlar: dict, toplam_oy: int) -> str:
        html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Anket Sonuçları</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2em;
                }}
                .content {{
                    padding: 30px;
                }}
                .question {{
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-bottom: 30px;
                    color: #333;
                    text-align: center;
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #ff6b35;
                }}
                .option {{
                    margin-bottom: 20px;
                    background: #fff;
                    border-radius: 10px;
                    border: 2px solid #e9ecef;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .option.correct {{
                    border-color: #28a745;
                    background: #d4edda;
                }}
                .option.incorrect {{
                    border-color: #dc3545;
                    background: #f8d7da;
                }}
                .option-header {{
                    padding: 15px 20px;
                    font-weight: bold;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .progress-bar {{
                    height: 12px;
                    background: #e9ecef;
                    margin: 0 20px 15px 20px;
                    border-radius: 6px;
                    overflow: hidden;
                }}
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #ff6b35, #f7931e);
                    transition: width 0.3s ease;
                    border-radius: 6px;
                }}
                .correct .progress-fill {{
                    background: linear-gradient(90deg, #28a745, #34ce57);
                }}
                .incorrect .progress-fill {{
                    background: linear-gradient(90deg, #dc3545, #e74c3c);
                }}
                .stats {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 10px;
                    margin-top: 30px;
                    text-align: center;
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                }}
                .stat-item {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .stat-number {{
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #ff6b35;
                    display: block;
                    margin-bottom: 5px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #6c757d;
                    font-size: 0.9em;
                    border-top: 1px solid #e9ecef;
                    background: #f8f9fa;
                }}
                .emoji {{
                    font-size: 1.3em;
                    margin-right: 10px;
                }}
                .option-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 15px;
                }}
                @media (max-width: 768px) {{
                    .option-grid {{
                        grid-template-columns: 1fr;
                    }}
                    .stats {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Anket Sonuçları</h1>
                    <p>Detaylı Analiz Raporu</p>
                </div>
                
                <div class="content">
                    <div class="question">
                        {self.soru}
                    </div>
                    
                    <div class="option-grid">
        """
        
        # Emojiler listesi genişletildi
        emojis = ['🅰️', '🅱️', '🅾️', '💠', '🔵', '🟢', '🟡', '🟠', '🔴', '🟣']
        
        for i, seçenek in enumerate(self.seçenekler):
            oy_sayısı = sonuçlar[i]
            yüzde = (oy_sayısı / toplam_oy * 100) if toplam_oy > 0 else 0
            is_correct = i == self.doğru_cevap
            status_class = "correct" if is_correct else "incorrect"
            status_icon = "✅" if is_correct else "❌"
            emoji = emojis[i] if i < len(emojis) else f"{i+1}️⃣"
            
            html += f"""
                        <div class="option {status_class}">
                            <div class="option-header">
                                <span><span class="emoji">{emoji}</span>{seçenek} {status_icon}</span>
                                <span><strong>{oy_sayısı}</strong> oy (%{yüzde:.1f})</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {yüzde}%"></div>
                            </div>
                        </div>
            """
        
        doğru_oy_sayısı = sonuçlar[self.doğru_cevap]
        yanlış_oy_sayısı = toplam_oy - doğru_oy_sayısı
        başarı_oranı = (doğru_oy_sayısı / toplam_oy * 100) if toplam_oy > 0 else 0
        
        # En çok oy alan yanlış cevap
        en_populer_yanlış = -1
        en_populer_yanlış_oy = 0
        for i, oy_sayısı in sonuçlar.items():
            if i != self.doğru_cevap and oy_sayısı > en_populer_yanlış_oy:
                en_populer_yanlış_oy = oy_sayısı
                en_populer_yanlış = i
        
        html += f"""
                    </div>
                    
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-number">{toplam_oy}</span>
                            <div>Toplam Katılımcı</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{doğru_oy_sayısı}</span>
                            <div>Doğru Cevap</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{yanlış_oy_sayısı}</span>
                            <div>Yanlış Cevap</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">%{başarı_oranı:.1f}</span>
                            <div>Başarı Oranı</div>
                        </div>
        """
        
        if en_populer_yanlış != -1:
            html += f"""
                        <div class="stat-item">
                            <span class="stat-number">{en_populer_yanlış_oy}</span>
                            <div>En Popüler Yanlış<br><small>({self.seçenekler[en_populer_yanlış][:30]}{"..." if len(self.seçenekler[en_populer_yanlış]) > 30 else ""})</small></div>
                        </div>
            """
        
        html += f"""
                    </div>
                </div>
                
                <div class="footer">
                    <p>🤖 Discord Bot Anket Sistemi | {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                    <p><strong>Doğru Cevap:</strong> {emojis[self.doğru_cevap] if self.doğru_cevap < len(emojis) else f"{self.doğru_cevap+1}️⃣"} {self.seçenekler[self.doğru_cevap]}</p>
                    <p><strong>Anket Süresi:</strong> {self.sure} saniye</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

class SoruCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="soru", description="İnteraktif anket/quiz oluşturun (2 zorunlu, 8 opsiyonel seçenek)")
    async def soru(self, interaction: discord.Interaction):
        """Kullanıcıdan soru ve seçenekleri alarak anket oluşturur"""
        modal = QuizModal1()
        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(SoruCog(bot))
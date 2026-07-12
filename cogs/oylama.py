import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import datetime
import os
import tempfile
from typing import List

class VoteModal1(discord.ui.Modal, title='Oylama Oluştur - 1/3'):
    def __init__(self):
        super().__init__()

    baslik = discord.ui.TextInput(
        label='Oylama Başlığı',
        placeholder='Oylamanızın başlığını yazın...',
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
        
        view = VoteContinueView(self.baslik.value, seçenekler)
        
        embed = discord.Embed(
            title="Daha Fazla Seçenek Eklemek İstiyor Musunuz?",
            description=f"**Başlık:** {self.baslik.value}\n\n" + 
                       "**Mevcut Seçenekler:**\n" +
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(seçenekler)]),
            color=0x5865F2
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class VoteModal2(discord.ui.Modal, title='Ek Seçenekler - 2/3'):
    def __init__(self, baslik: str, mevcut_seçenekler: List[str]):
        super().__init__()
        self.baslik = baslik
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
        
        view = VoteContinueView2(self.baslik, seçenekler)
        
        embed = discord.Embed(
            title="Daha Fazla Seçenek Eklemek İstiyor Musunuz?",
            description=f"**Başlık:** {self.baslik}\n\n" + 
                       "**Mevcut Seçenekler:**\n" +
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(seçenekler)]),
            color=0x5865F2
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class VoteModalExtra(discord.ui.Modal, title='Ek Seçenekler'):
    def __init__(self, baslik: str, mevcut_seçenekler: List[str]):
        super().__init__()
        self.baslik = baslik
        self.mevcut_seçenekler = mevcut_seçenekler

    # Manuel olarak 5 adet TextInput tanımla (dinamik yerine)
    secenek1 = discord.ui.TextInput(
        label='',  # Bu label'lar __init__ metodunda güncellenecek
        placeholder='',
        required=False,
        max_length=100
    )
    
    secenek2 = discord.ui.TextInput(
        label='',
        placeholder='',
        required=False,
        max_length=100
    )
    
    secenek3 = discord.ui.TextInput(
        label='',
        placeholder='',
        required=False,
        max_length=100
    )
    
    secenek4 = discord.ui.TextInput(
        label='',
        placeholder='',
        required=False,
        max_length=100
    )
    
    secenek5 = discord.ui.TextInput(
        label='',
        placeholder='',
        required=False,
        max_length=100
    )
    
    def __init__(self, baslik: str, mevcut_seçenekler: List[str]):
        super().__init__()
        self.baslik = baslik
        self.mevcut_seçenekler = mevcut_seçenekler
        
        # Label'ları ve placeholder'ları dinamik olarak güncelle
        start_index = len(mevcut_seçenekler)
        
        self.secenek1.label = f'Seçenek {start_index + 1} (Opsiyonel)'
        self.secenek1.placeholder = f'{start_index + 1}. seçeneği yazın...'
        
        self.secenek2.label = f'Seçenek {start_index + 2} (Opsiyonel)'
        self.secenek2.placeholder = f'{start_index + 2}. seçeneği yazın...'
        
        self.secenek3.label = f'Seçenek {start_index + 3} (Opsiyonel)'
        self.secenek3.placeholder = f'{start_index + 3}. seçeneği yazın...'
        
        self.secenek4.label = f'Seçenek {start_index + 4} (Opsiyonel)'
        self.secenek4.placeholder = f'{start_index + 4}. seçeneği yazın...'
        
        self.secenek5.label = f'Seçenek {start_index + 5} (Opsiyonel)'
        self.secenek5.placeholder = f'{start_index + 5}. seçeneği yazın...'

    async def on_submit(self, interaction: discord.Interaction):
        seçenekler = self.mevcut_seçenekler.copy()
        
        # 5 adet seçeneği kontrol et
        ek_seçenekler = [
            self.secenek1.value, 
            self.secenek2.value, 
            self.secenek3.value,
            self.secenek4.value, 
            self.secenek5.value
        ]
        
        for seçenek in ek_seçenekler:
            if seçenek and seçenek.strip():  # Boş olmayan seçenekleri ekle
                seçenekler.append(seçenek.strip())
        
        view = VoteContinueView2(self.baslik, seçenekler)
        
        embed = discord.Embed(
            title="Daha Fazla Seçenek Eklemek İstiyor Musunuz?",
            description=f"**Başlık:** {self.baslik}\n\n" + 
                       "**Mevcut Seçenekler:**\n" +
                       "\n".join([f"{i+1}. {seçenek}" for i, seçenek in enumerate(seçenekler)]),
            color=0x5865F2
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class VoteContinueView(discord.ui.View):
    def __init__(self, baslik: str, seçenekler: List[str]):
        super().__init__(timeout=300)
        self.baslik = baslik
        self.seçenekler = seçenekler

    @discord.ui.button(label="Evet, daha fazla seçenek ekle", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_more_options(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VoteModal2(self.baslik, self.seçenekler)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Hayır, süre belirle", style=discord.ButtonStyle.secondary, emoji="⏱️")
    async def set_time(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VoteTimeInputModal(self.baslik, self.seçenekler)
        await interaction.response.send_modal(modal)

class VoteContinueView2(discord.ui.View):
    def __init__(self, baslik: str, seçenekler: List[str]):
        super().__init__(timeout=300)
        self.baslik = baslik
        self.seçenekler = seçenekler

    @discord.ui.button(label="Daha fazla seçenek ekle", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_more_options(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Discord'un 25 buton limitine göre maksimum seçenek sayısını belirle
        if len(self.seçenekler) < 24:  # 1 buton finish için ayrılıyor
            modal = VoteModalExtra(self.baslik, self.seçenekler)
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(
                "⚠️ Discord'un 25 buton limiti nedeniyle daha fazla seçenek ekleyemezsiniz!\nOylamayı başlatmak için **Süre Belirle** butonuna tıklayın.", 
                ephemeral=True
            )

    @discord.ui.button(label="Süre belirle", style=discord.ButtonStyle.secondary, emoji="⏱️")
    async def set_time(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = VoteTimeInputModal(self.baslik, self.seçenekler)
        await interaction.response.send_modal(modal)

class VoteTimeInputModal(discord.ui.Modal, title='Oylama Süresini Belirleyin'):
    def __init__(self, baslik: str, seçenekler: List[str]):
        super().__init__()
        self.baslik = baslik
        self.seçenekler = seçenekler

    sure_input = discord.ui.TextInput(
        label='Süre (saniye)',
        placeholder='10-86400 arasında saniye cinsinden süre girin (0 = süresiz)',
        required=True,
        max_length=5,
        min_length=1
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            sure = int(self.sure_input.value)
            
            if sure < 0:
                await interaction.response.send_message("❌ Süre negatif olamaz!", ephemeral=True)
                return
            elif sure > 86400:
                await interaction.response.send_message("❌ Maksimum süre 86400 saniye (24 saat) olmalıdır!", ephemeral=True)
                return
            elif sure > 0 and sure < 10:
                await interaction.response.send_message("❌ Minimum süre 10 saniye olmalıdır! (0 = süresiz)", ephemeral=True)
                return
                
        except ValueError:
            await interaction.response.send_message("❌ Lütfen geçerli bir sayı girin!", ephemeral=True)
            return
        
        # Oylama başlat
        vote_view = VotingView(self.baslik, self.seçenekler, sure, interaction.user.id)
        
        embed = discord.Embed(
            title="🗳️ OYLAMA",
            description=f"**{self.baslik}**\n\n" + 
                       "\n".join([f"{i+1}️⃣ {seçenek}" 
                                 for i, seçenek in enumerate(self.seçenekler)]),
            color=0x5865F2,
            timestamp=datetime.datetime.now()
        )
        
        if sure == 0:
            embed.set_footer(text="Süresiz oylama")
        else:
            embed.set_footer(text=f"Süre: {sure} saniye")
        
        # Ephemeral mesajı kapat ve herkese görünür oylama başlat
        await interaction.response.send_message("✅ Oylama başlatılıyor...", ephemeral=True, delete_after=1)
        message = await interaction.followup.send(embed=embed, view=vote_view, ephemeral=False)
        
        # Oylamayı aktif oylamalar listesine ekle
        if hasattr(interaction.client, 'get_cog'):
            cog = interaction.client.get_cog('OylamaCog')
            if cog:
                cog.active_votes[f"vote_{message.id}"] = vote_view
        
        # Oylama bitirme görevi başlat (eğer süre varsa)
        if sure > 0:
            asyncio.create_task(vote_view.finish_vote(interaction, sure))

class VotingView(discord.ui.View):
    def __init__(self, baslik: str, seçenekler: List[str], sure: int, vote_owner_id: int):
        # Süresiz oylamalar için timeout'u None yap
        super().__init__(timeout=None if sure == 0 else sure + 10)
        self.baslik = baslik
        self.seçenekler = seçenekler
        self.sure = sure
        self.vote_owner_id = vote_owner_id
        self.oylar = {}  # user_id: seçenek_index
        self.finished = False
        
        # Seçenekler için butonlar (maksimum 24 buton - 1 sonlandırma butonu için yer bırak)
        for i, seçenek in enumerate(seçenekler[:24]):
            button = discord.ui.Button(
                label=f"{i+1}. {seçenek[:50]}",
                style=discord.ButtonStyle.secondary,
                custom_id=f"vote_{i}",
                row=i // 5  # Her satırda 5 buton
            )
            button.callback = self.vote_callback
            self.add_item(button)
        
        # Erken bitirme butonu (sadece oylama sahibi için)
        finish_button = discord.ui.Button(
            label="🛑 Oylamayı Sonlandır",
            style=discord.ButtonStyle.danger,
            custom_id="finish_vote",
            row=4 if len(seçenekler) <= 20 else min(4, (len(seçenekler) - 1) // 5)
        )
        finish_button.callback = self.finish_early_callback
        self.add_item(finish_button)

    async def vote_callback(self, interaction: discord.Interaction):
        if self.finished:
            await interaction.response.send_message("⏰ Oylama sonlandırılmış!", ephemeral=True)
            return
            
        button_id = interaction.data['custom_id']
        seçenek_index = int(button_id.split('_')[1])
        
        # Önceki oyunu kontrol et
        previous_vote = self.oylar.get(interaction.user.id)
        self.oylar[interaction.user.id] = seçenek_index
        
        if previous_vote is not None:
            await interaction.response.send_message(
                f"🔄 Oyunuz **{self.seçenekler[seçenek_index]}** olarak güncellendi!\n" +
                f"*(Önceki: {self.seçenekler[previous_vote]})*", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"✅ **{self.seçenekler[seçenek_index]}** seçeneğine oy verdiniz!", 
                ephemeral=True
            )

    async def finish_early_callback(self, interaction: discord.Interaction):
        # Sadece oylama sahibi erken bitirebilir
        if interaction.user.id != self.vote_owner_id:
            await interaction.response.send_message("❌ Sadece oylama sahibi oylamayı erken sonlandırabilir!", ephemeral=True)
            return
        
        if self.finished:
            await interaction.response.send_message("⏰ Oylama zaten sonlandırılmış!", ephemeral=True)
            return
        
        self.finished = True
        await interaction.response.send_message("✅ Oylama erken sonlandırıldı!", ephemeral=True)
        
        # Oylama sonuçlarını göster
        await self.process_results(interaction)

    async def finish_vote(self, interaction: discord.Interaction, sure: int):
        try:
            await asyncio.sleep(sure)
            if not self.finished:  # Eğer erken bitirmemişse
                self.finished = True
                await self.process_results(interaction)
        except asyncio.CancelledError:
            print("Oylama task'ı iptal edildi")
        except Exception as e:
            print(f"finish_vote hatası: {e}")
            # Hata durumunda da finished durumunu güncelle
            self.finished = True

    async def process_results(self, interaction: discord.Interaction):
        # Aktif oylamalar listesinden kaldır
        if hasattr(interaction.client, 'get_cog'):
            cog = interaction.client.get_cog('OylamaCog')
            if cog:
                # Bu oylamayı listeden kaldır
                to_remove = None
                for vote_id, vote_view in cog.active_votes.items():
                    if vote_view == self:
                        to_remove = vote_id
                        break
                if to_remove:
                    del cog.active_votes[to_remove]
        
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
        
        # Discord embed güncelle
        result_embed = discord.Embed(
            title="🗳️ OYLAMA SONUÇLANDI",
            description=f"**{self.baslik}**\n\n✅ Oylama tamamlandı!\n📊 Toplam **{toplam_oy}** oy alındı.\n📧 Detaylı sonuçlar oylama sahibine DM olarak gönderildi.",
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        
        # Interaction timeout sorununu çöz - güvenli mesaj güncelleme
        message_updated = False
        
        try:
            # Önce interaction durumunu kontrol et
            if not interaction.response.is_done():
                # Response henüz gönderilmediyse
                await interaction.response.edit_message(embed=result_embed, view=None)
                message_updated = True
            else:
                # Response zaten gönderilmişse edit_original_response kullan
                await interaction.edit_original_response(embed=result_embed, view=None)
                message_updated = True
        except discord.InteractionResponded:
            # Interaction zaten yanıtlanmışsa
            try:
                await interaction.edit_original_response(embed=result_embed, view=None)
                message_updated = True
            except Exception:
                pass
        except discord.NotFound:
            # Mesaj bulunamazsa
            pass
        except Exception as e:
            print(f"Interaction güncelleme hatası: {e}")
        
        # Eğer mesaj güncellenemezse kanal mesajı gönder
        if not message_updated:
            try:
                await interaction.channel.send(embed=result_embed)
            except Exception as e:
                print(f"Kanal mesajı gönderme hatası: {e}")
                # Son çare: followup kullan
                try:
                    await interaction.followup.send(embed=result_embed, ephemeral=False)
                except Exception:
                    pass
        
        # HTML dosyasını sadece oylama sahibine DM olarak gönder
        try:
            vote_owner = interaction.client.get_user(self.vote_owner_id)
            if vote_owner:
                file = discord.File(temp_file_path, filename=f"oylama_sonuclari_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                
                # DM embed'i detaylı sonuçlarla - Discord'un 25 field limitine dikkat et
                dm_embed = discord.Embed(
                    title="🗳️ Oylama Sonuçlarınız",
                    description=f"**{self.baslik}**",
                    color=0x5865F2,
                    timestamp=datetime.datetime.now()
                )
                
                # İlk 20 seçeneği field olarak ekle (5 field daha için yer bırak)
                for i, seçenek in enumerate(self.seçenekler[:20]):
                    oy_sayısı = sonuçlar[i]
                    yüzde = (oy_sayısı / toplam_oy * 100) if toplam_oy > 0 else 0
                    
                    dm_embed.add_field(
                        name=f"{i+1}️⃣ {seçenek[:50]}",
                        value=f"**{oy_sayısı}** oy (%{yüzde:.1f})",
                        inline=True
                    )
                
                # Eğer 20'den fazla seçenek varsa, kalanları description'a ekle
                if len(self.seçenekler) > 20:
                    extra_results = "\n\n**Diğer Seçenekler:**\n"
                    for i in range(20, len(self.seçenekler)):
                        seçenek = self.seçenekler[i]
                        oy_sayısı = sonuçlar[i]
                        yüzde = (oy_sayısı / toplam_oy * 100) if toplam_oy > 0 else 0
                        extra_results += f"{i+1}️⃣ {seçenek[:40]} - **{oy_sayısı}** oy (%{yüzde:.1f})\n"
                    
                    # Description limitini kontrol et (4096 karakter)
                    if len(dm_embed.description + extra_results) <= 4000:
                        dm_embed.description += extra_results
                
                # En çok oy alan seçenek
                if toplam_oy > 0:
                    kazanan_index = max(sonuçlar, key=sonuçlar.get)
                    kazanan_oy = sonuçlar[kazanan_index]
                    
                    dm_embed.add_field(
                        name="🏆 En Çok Oy Alan", 
                        value=f"**{self.seçenekler[kazanan_index][:50]}**\n{kazanan_oy} oy (%{(kazanan_oy/toplam_oy*100):.1f})", 
                        inline=False
                    )
                
                dm_embed.add_field(
                    name="📈 İstatistikler", 
                    value=f"Toplam Oy: **{toplam_oy}**\nSeçenek Sayısı: **{len(self.seçenekler)}**", 
                    inline=False
                )
                
                # DM gönder
                await vote_owner.send(embed=dm_embed, file=file)
            
        except discord.Forbidden:
            # DM gönderilemezse kanala bildirim yap
            try:
                if message_updated:
                    await interaction.followup.send(
                        f"<@{self.vote_owner_id}> DM'iniz kapalı olduğu için HTML raporu gönderilemiyor!", 
                        ephemeral=True
                    )
                else:
                    await interaction.channel.send(
                        f"<@{self.vote_owner_id}> DM'iniz kapalı olduğu için HTML raporu gönderilemiyor!"
                    )
            except Exception as e:
                print(f"DM uyarı mesajı hatası: {e}")
        except Exception as e:
            print(f"DM gönderme hatası: {e}")
            # Hata durumunda da kullanıcıyı bilgilendir
            try:
                if message_updated:
                    await interaction.followup.send(
                        f"<@{self.vote_owner_id}> DM gönderilirken bir hata oluştu: {str(e)}", 
                        ephemeral=True
                    )
                else:
                    await interaction.channel.send(
                        f"<@{self.vote_owner_id}> DM gönderilirken bir hata oluştu!"
                    )
            except Exception as e2:
                print(f"Hata bildirimi hatası: {e2}")
        finally:
            # Geçici dosyayı sil
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except Exception as e:
                print(f"Geçici dosya silme hatası: {e}")

    def create_html_report(self, sonuçlar: dict, toplam_oy: int) -> str:
        html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Oylama Sonuçları</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #5865F2 0%, #7289DA 100%);
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
                    background: linear-gradient(135deg, #5865F2 0%, #7289DA 100%);
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
                .title {{
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-bottom: 30px;
                    color: #333;
                    text-align: center;
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #5865F2;
                }}
                .option {{
                    margin-bottom: 20px;
                    background: #fff;
                    border-radius: 10px;
                    border: 2px solid #e9ecef;
                    overflow: hidden;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .option.winner {{
                    border-color: #FFD700;
                    background: #FFFBF0;
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
                    background: linear-gradient(90deg, #5865F2, #7289DA);
                    transition: width 0.3s ease;
                    border-radius: 6px;
                }}
                .winner .progress-fill {{
                    background: linear-gradient(90deg, #FFD700, #FFA500);
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
                    color: #5865F2;
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
                    <h1>🗳️ Oylama Sonuçları</h1>
                    <p>Detaylı Analiz Raporu</p>
                </div>
                
                <div class="content">
                    <div class="title">
                        {self.baslik}
                    </div>
                    
                    <div class="option-grid">
        """
        
        # En çok oy alan seçeneği bul
        kazanan_index = -1
        if toplam_oy > 0:
            kazanan_index = max(sonuçlar, key=sonuçlar.get)
        
        for i, seçenek in enumerate(self.seçenekler):
            oy_sayısı = sonuçlar[i]
            yüzde = (oy_sayısı / toplam_oy * 100) if toplam_oy > 0 else 0
            is_winner = i == kazanan_index and toplam_oy > 0
            status_class = "winner" if is_winner else ""
            status_icon = "🏆" if is_winner else ""
            
            html += f"""
                        <div class="option {status_class}">
                            <div class="option-header">
                                <span><span class="emoji">{i+1}️⃣</span>{seçenek} {status_icon}</span>
                                <span><strong>{oy_sayısı}</strong> oy (%{yüzde:.1f})</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {yüzde}%"></div>
                            </div>
                        </div>
            """
        
        # İstatistik hesaplamaları - DÜZELTİLMİŞ BÖLÜM
        if toplam_oy > 0:
            kazanan_oy = sonuçlar[kazanan_index]
            kazanan_seçenek = self.seçenekler[kazanan_index]
            kazanan_yuzde = (kazanan_oy / toplam_oy * 100)
        else:
            kazanan_oy = 0
            kazanan_seçenek = "Oy verilmedi"
            kazanan_yuzde = 0
        
        html += f"""
                    </div>
                    
                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-number">{toplam_oy}</span>
                            <div>Toplam Katılımcı</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{len(self.seçenekler)}</span>
                            <div>Seçenek Sayısı</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{kazanan_oy}</span>
                            <div>En Yüksek Oy</div>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">%{kazanan_yuzde:.1f}</span>
                            <div>En Yüksek Oran</div>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🤖 Discord Bot Oylama Sistemi | {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                    <p><strong>En Çok Oy Alan:</strong> {kazanan_seçenek} ({kazanan_oy} oy)</p>
                    <p><strong>Oylama Süresi:</strong> {"Süresiz" if self.sure == 0 else f"{self.sure} saniye"}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


class OylamaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_votes = {}  # message_id: VotingView

    @app_commands.command(name="oylama", description="İnteraktif oylama oluşturun (2 zorunlu, sınırsız opsiyonel seçenek)")
    async def oylama(self, interaction: discord.Interaction):
        """Kullanıcıdan başlık ve seçenekleri alarak oylama oluşturur"""
        modal = VoteModal1()
        await interaction.response.send_modal(modal)

    @app_commands.command(name="oylama-bitir", description="Aktif oylamalarınızı erken sonlandırın")
    async def oylama_bitir(self, interaction: discord.Interaction, oylama_id: str = None):
        """Kullanıcının aktif oylamasını erken sonlandırır"""
        # Kullanıcının aktif oylamalarını bul
        user_votes = []
        for vote_id, vote_view in self.active_votes.items():
            if vote_view.vote_owner_id == interaction.user.id and not vote_view.finished:
                # vote_ prefix'ini kaldır
                actual_msg_id = vote_id.replace("vote_", "")
                user_votes.append((actual_msg_id, vote_view, vote_id))
        
        if not user_votes:
            await interaction.response.send_message(
                "❌ Aktif oylamanız bulunamadı! Sadece kendi oluşturduğunuz aktif oylamayı sonlandırabilirsiniz.", 
                ephemeral=True
            )
            return
        
        # Eğer oylama_id belirtilmişse o oylamayı bul
        if oylama_id:
            target_vote = None
            target_vote_id = None
            
            for msg_id, vote_view, vote_id in user_votes:
                if str(msg_id) == oylama_id:
                    target_vote = vote_view
                    target_vote_id = vote_id
                    break
            
            if not target_vote:
                await interaction.response.send_message(
                    f"❌ ID '{oylama_id}' ile oylama bulunamadı!", 
                    ephemeral=True
                )
                return
        else:
            # Oylama ID belirtilmemişse
            if len(user_votes) == 1:
                # Tek oylama varsa direkt sonlandır
                msg_id, target_vote, target_vote_id = user_votes[0]
            else:
                # Birden fazla oylama varsa liste göster
                oylama_listesi = "\n".join([
                    f"🔹 **ID: {msg_id}** - {vote_view.baslik[:50]}{'...' if len(vote_view.baslik) > 50 else ''}"
                    for msg_id, vote_view, _ in user_votes
                ])
                
                await interaction.response.send_message(
                    f"🗳️ **Aktif Oylamalarınız:**\n\n{oylama_listesi}\n\n" +
                    "Belirli bir oylamayı sonlandırmak için: `/oylama-bitir oylama_id:<ID>`", 
                    ephemeral=True
                )
                return
        
        # Oylamayı sonlandır
        target_vote.finished = True
        await interaction.response.send_message(
            f"✅ Oylama sonlandırıldı!\n**Başlık:** {target_vote.baslik[:100]}{'...' if len(target_vote.baslik) > 100 else ''}", 
            ephemeral=True
        )
        
        # Sonuçları işle
        await target_vote.process_results(interaction)
        
        # Aktif oylamalar listesinden kaldır
        if target_vote_id in self.active_votes:
            del self.active_votes[target_vote_id]

    @app_commands.command(name="oylamalarım", description="Aktif oylamalarınızı listeleyin")
    async def oylamalrim(self, interaction: discord.Interaction):
        """Kullanıcının aktif oylamalarını listeler"""
        user_votes = []
        for vote_id, vote_view in self.active_votes.items():
            if vote_view.vote_owner_id == interaction.user.id and not vote_view.finished:
                # vote_ prefix'ini kaldır
                actual_msg_id = vote_id.replace("vote_", "")
                user_votes.append((actual_msg_id, vote_view))
        
        if not user_votes:
            await interaction.response.send_message(
                "❌ Aktif oylamanız bulunmuyor.", 
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🗳️ Aktif Oylamalarınız",
            color=0x5865F2,
            timestamp=datetime.datetime.now()
        )
        
        for i, (msg_id, vote_view) in enumerate(user_votes, 1):
            toplam_oy = len(vote_view.oylar)
            sure_bilgisi = "Süresiz" if vote_view.sure == 0 else f"{vote_view.sure} saniye"
            
            embed.add_field(
                name=f"#{i} - ID: {msg_id}",
                value=f"**Başlık:** {vote_view.baslik[:80]}{'...' if len(vote_view.baslik) > 80 else ''}\n" +
                      f"**Toplam Oy:** {toplam_oy}\n" +
                      f"**Seçenek Sayısı:** {len(vote_view.seçenekler)}\n" +
                      f"**Süre:** {sure_bilgisi}",
                inline=False
            )
        
        embed.set_footer(text=f"Toplam {len(user_votes)} aktif oylama | Sonlandırmak için: /oylama-bitir")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(OylamaCog(bot))

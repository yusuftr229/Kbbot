import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
from datetime import datetime, timezone

class KayitSistemi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.pending_registrations = {}
        
    def load_config(self):
        try:
            with open('kayit_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'kayitsiz_rol': None,
                'kayitli_rol': None,
                'kayit_kanal': None,
                'anayasa_kanal': None,
                'onay_kanal': None,
                'log_kanal': None,
                'yetkili_rol': None,
                'sorular': []
            }
    
    def save_config(self):
        with open('kayit_config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.config['kayitsiz_rol']:
            rol = member.guild.get_role(self.config['kayitsiz_rol'])
            if rol:
                await member.add_roles(rol)
                
        if self.config['kayit_kanal']:
            kanal = member.guild.get_channel(self.config['kayit_kanal'])
            if kanal:
                await self.send_kayit_mesaji(kanal)
    
    async def send_kayit_mesaji(self, kanal):
        await kanal.purge(limit=100)
        
        embed = discord.Embed(
            title="🎉 Sunucumuza Hoş Geldiniz!",
            description="Kayıt işlemini tamamlamak için lütfen aşağıdaki adımları takip edin:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📜 Adım 1",
            value="Öncelikle anayasa kanalını okuyun ve kurallarımızı öğrenin.",
            inline=False
        )
        embed.add_field(
            name="✅ Adım 2",
            value="Anayasayı okuduktan sonra aşağıdaki butona tıklayın ve kayıt sorularını cevaplayın.",
            inline=False
        )
        
        view = KayitButton(self)
        await kanal.send(embed=embed, view=view)
    
    async def baslat_kayit(self, interaction: discord.Interaction):
        if not self.config['sorular']:
            await interaction.response.send_message(
                "❌ Henüz kayıt soruları ayarlanmamış!",
                ephemeral=True
            )
            return
        
        # Eski kayıt varsa sil ve yeniden başlat
        if interaction.user.id in self.pending_registrations:
            del self.pending_registrations[interaction.user.id]
        
        # Geçici kayıt oluştur
        self.pending_registrations[interaction.user.id] = {
            'user': interaction.user,
            'cevaplar': [],
            'timestamp': datetime.now(),
            'current_page': 0
        }
        
        # İlk 5 soru için modal göster
        modal = KayitModal(self, self.config['sorular'][:5], 0, interaction.user.id)
        await interaction.response.send_modal(modal)
    
    async def gonder_onay(self, guild, user, cevaplar):
        if not self.config['onay_kanal']:
            return
        
        kanal = guild.get_channel(self.config['onay_kanal'])
        if not kanal:
            return
        
        # Tarih hesaplamaları
        member = guild.get_member(user.id)
        discord_katilim = user.created_at
        sunucu_katilim = member.joined_at if member else None
        
        # Tarih farkını hesapla (gün cinsinden)
        if sunucu_katilim:
            fark = (sunucu_katilim - discord_katilim).days
            guvenli = fark >= 15
        else:
            fark = None
            guvenli = None
        
        # Embed rengi güvenlik durumuna göre
        if guvenli is False:
            embed_color = discord.Color.red()
        elif guvenli is True:
            embed_color = discord.Color.green()
        else:
            embed_color = discord.Color.orange()
        
        embed = discord.Embed(
            title="🆕 Yeni Kayıt Başvurusu",
            description=f"**Kullanıcı:** {user.mention}\n**ID:** {user.id}",
            color=embed_color,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Tarih bilgileri
        discord_tarih_str = f"<t:{int(discord_katilim.timestamp())}:F> (<t:{int(discord_katilim.timestamp())}:R>)"
        embed.add_field(
            name="📅 Discord'a Katılma",
            value=discord_tarih_str,
            inline=False
        )
        
        if sunucu_katilim:
            sunucu_tarih_str = f"<t:{int(sunucu_katilim.timestamp())}:F> (<t:{int(sunucu_katilim.timestamp())}:R>)"
            embed.add_field(
                name="🏠 Sunucuya Katılma",
                value=sunucu_tarih_str,
                inline=False
            )
            
            # Güvenlik durumu
            if guvenli is False:
                embed.add_field(
                    name="⚠️ GÜVENLİK UYARISI",
                    value=f"❗ **Hesap yeni!** Discord hesabı ile sunucuya katılma arasında sadece **{fark} gün** var. (15 günden az)\n🔴 **Potansiyel risk!**",
                    inline=False
                )
            else:
                embed.add_field(
                    name="✅ Güvenlik Durumu",
                    value=f"✔️ Güvenli - Discord hesabı ile sunucuya katılma arasında **{fark} gün** var.",
                    inline=False
                )
        
        # Cevaplar
        for i, item in enumerate(cevaplar, 1):
            embed.add_field(
                name=f"❓ {item['soru']}",
                value=f"💬 {item['cevap']}",
                inline=False
            )
        
        self.pending_registrations[user.id] = {
            'user': user,
            'cevaplar': cevaplar,
            'timestamp': datetime.now()
        }
        
        view = OnayView(self, user.id)
        
        # Yetkili rolü varsa tag'le
        content = None
        if self.config.get('yetkili_rol'):
            yetkili_rol = guild.get_role(self.config['yetkili_rol'])
            if yetkili_rol:
                if guvenli is False:
                    content = f"{yetkili_rol.mention} ⚠️ Yeni kayıt başvurusu - **GÜVENLİK UYARISI!**"
                else:
                    content = f"{yetkili_rol.mention} 🔔 Yeni kayıt başvurusu!"
        
        await kanal.send(content=content, embed=embed, view=view)
    
    async def kabul_et(self, interaction: discord.Interaction, user_id: int):
        if user_id not in self.pending_registrations:
            await interaction.response.send_message("❌ Bu kayıt bulunamadı!", ephemeral=True)
            return
        
        data = self.pending_registrations[user_id]
        member = interaction.guild.get_member(user_id)
        
        if not member:
            await interaction.response.send_message("❌ Kullanıcı sunucudan ayrılmış!", ephemeral=True)
            del self.pending_registrations[user_id]
            return
        
        kayitsiz_rol = interaction.guild.get_role(self.config['kayitsiz_rol']) if self.config['kayitsiz_rol'] else None
        kayitli_rol = interaction.guild.get_role(self.config['kayitli_rol']) if self.config['kayitli_rol'] else None
        
        if kayitsiz_rol:
            await member.remove_roles(kayitsiz_rol)
        if kayitli_rol:
            await member.add_roles(kayitli_rol)
        
        # Orijinal mesajı güncelle
        original_embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if original_embed:
            # Orijinal embed'i kopyala ve güncelle
            updated_embed = discord.Embed(
                title="✅ Kayıt Kabul Edildi",
                description=original_embed.description,
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            # Tüm fieldları kopyala
            for field in original_embed.fields:
                updated_embed.add_field(name=field.name, value=field.value, inline=field.inline)
            
            # İşlemi yapan bilgisini ekle
            updated_embed.add_field(
                name="👮 İşlemi Yapan",
                value=f"{interaction.user.mention} tarafından kabul edildi",
                inline=False
            )
            
            if original_embed.thumbnail:
                updated_embed.set_thumbnail(url=original_embed.thumbnail.url)
            
            # Mesajı güncelle ve butonları kaldır
            await interaction.message.edit(embed=updated_embed, view=None)
            await interaction.response.send_message(f"✅ {member.mention} başarıyla kayıt edildi!", ephemeral=True)
        else:
            await interaction.response.send_message(f"✅ {member.mention} başarıyla kayıt edildi!")
        
        try:
            await member.send(f"🎉 Tebrikler! **{interaction.guild.name}** sunucusuna kabul edildiniz!")
        except:
            pass
        
        await self.log_kayit(interaction.guild, member, data['cevaplar'], interaction.user, "Kabul Edildi")
        del self.pending_registrations[user_id]
    
    async def reddet(self, interaction: discord.Interaction, user_id: int, sebep: str):
        if user_id not in self.pending_registrations:
            await interaction.response.send_message("❌ Bu kayıt bulunamadı!", ephemeral=True)
            return
        
        data = self.pending_registrations[user_id]
        member = interaction.guild.get_member(user_id)
        
        # Red mesajını güncelle
        embed = discord.Embed(
            title="❌ Kayıt Reddedildi",
            description=f"**Kullanıcı:** {member.mention if member else 'Bilinmeyen'}\n**Reddeden:** {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="📝 Red Sebebi", value=sebep, inline=False)
        if member:
            embed.set_thumbnail(url=member.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
        if member:
            try:
                dm_embed = discord.Embed(
                    title="❌ Kayıt Başvurunuz Reddedildi",
                    description=f"**{interaction.guild.name}** sunucusuna kaydınız reddedildi.",
                    color=discord.Color.red()
                )
                dm_embed.add_field(name="📝 Red Sebebi", value=sebep, inline=False)
                dm_embed.set_footer(text="Tekrar başvurabilirsiniz.")
                await member.send(embed=dm_embed)
            except:
                pass
            
            await self.log_kayit(interaction.guild, member, data['cevaplar'], interaction.user, "Reddedildi", sebep)
        
        del self.pending_registrations[user_id]
    
    async def log_kayit(self, guild, member, cevaplar, yetkili, durum, sebep=None):
        if not self.config['log_kanal']:
            return
        
        kanal = guild.get_channel(self.config['log_kanal'])
        if not kanal:
            return
        
        renk = discord.Color.green() if durum == "Kabul Edildi" else discord.Color.red()
        
        embed = discord.Embed(
            title=f"📋 Kayıt İşlemi - {durum}",
            color=renk,
            timestamp=datetime.now()
        )
        embed.add_field(name="👤 Kullanıcı", value=f"{member.mention} ({member.id})", inline=True)
        embed.add_field(name="👮 İşlemi Yapan", value=f"{yetkili.mention}", inline=True)
        embed.add_field(name="📊 Durum", value=durum, inline=True)
        
        # Tarih bilgileri
        discord_katilim = member.created_at
        sunucu_katilim = member.joined_at
        
        if sunucu_katilim:
            fark = (sunucu_katilim - discord_katilim).days
            guvenli = fark >= 15
            
            discord_str = f"<t:{int(discord_katilim.timestamp())}:F>"
            sunucu_str = f"<t:{int(sunucu_katilim.timestamp())}:F>"
            
            embed.add_field(name="📅 Discord'a Katılma", value=discord_str, inline=True)
            embed.add_field(name="🏠 Sunucuya Katılma", value=sunucu_str, inline=True)
            
            if guvenli:
                embed.add_field(name="🔒 Güvenlik", value=f"✅ Güvenli ({fark} gün)", inline=True)
            else:
                embed.add_field(name="⚠️ Güvenlik", value=f"❗ Risk ({fark} gün)", inline=True)
        
        if sebep and durum == "Reddedildi":
            embed.add_field(name="📝 Red Sebebi", value=sebep, inline=False)
        
        for i, item in enumerate(cevaplar, 1):
            embed.add_field(
                name=f"❓ Soru {i}",
                value=f"**{item['soru']}**\n{item['cevap']}",
                inline=False
            )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Kayıt Sistemi")
        
        await kanal.send(embed=embed)
    
    @app_commands.command(name="kayit-ayarla", description="Kayıt sistemini yapılandırın")
    @app_commands.describe(
        kayitsiz_rol="Kayıtsız üyelere verilecek rol",
        kayitli_rol="Kayıtlı üyelere verilecek rol",
        kayit_kanal="Kayıt mesajının gösterileceği kanal",
        anayasa_kanal="Anayasa kanalı",
        onay_kanal="Kayıt onaylarının gösterileceği kanal",
        log_kanal="Kayıt loglarının tutulacağı kanal",
        yetkili_rol="Kayıt bildirimi alacak yetkili rolü"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def kayit_ayarla(
        self,
        interaction: discord.Interaction,
        kayitsiz_rol: discord.Role = None,
        kayitli_rol: discord.Role = None,
        kayit_kanal: discord.TextChannel = None,
        anayasa_kanal: discord.TextChannel = None,
        onay_kanal: discord.TextChannel = None,
        log_kanal: discord.TextChannel = None,
        yetkili_rol: discord.Role = None
    ):
        if kayitsiz_rol:
            self.config['kayitsiz_rol'] = kayitsiz_rol.id
        if kayitli_rol:
            self.config['kayitli_rol'] = kayitli_rol.id
        if kayit_kanal:
            self.config['kayit_kanal'] = kayit_kanal.id
        if anayasa_kanal:
            self.config['anayasa_kanal'] = anayasa_kanal.id
        if onay_kanal:
            self.config['onay_kanal'] = onay_kanal.id
        if log_kanal:
            self.config['log_kanal'] = log_kanal.id
        if yetkili_rol:
            self.config['yetkili_rol'] = yetkili_rol.id
        
        self.save_config()
        
        embed = discord.Embed(
            title="✅ Kayıt Sistemi Ayarlandı",
            color=discord.Color.green()
        )
        if kayitsiz_rol:
            embed.add_field(name="Kayıtsız Rol", value=kayitsiz_rol.mention, inline=True)
        if kayitli_rol:
            embed.add_field(name="Kayıtlı Rol", value=kayitli_rol.mention, inline=True)
        if kayit_kanal:
            embed.add_field(name="Kayıt Kanalı", value=kayit_kanal.mention, inline=True)
        if anayasa_kanal:
            embed.add_field(name="Anayasa Kanalı", value=anayasa_kanal.mention, inline=True)
        if onay_kanal:
            embed.add_field(name="Onay Kanalı", value=onay_kanal.mention, inline=True)
        if log_kanal:
            embed.add_field(name="Log Kanalı", value=log_kanal.mention, inline=True)
        if yetkili_rol:
            embed.add_field(name="Yetkili Rolü", value=yetkili_rol.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        if kayit_kanal:
            await self.send_kayit_mesaji(kayit_kanal)
    
    @app_commands.command(name="kayıt-soru-ekle", description="Kayıt sorusu ekleyin")
    @app_commands.describe(soru="Eklenecek soru")
    @app_commands.checks.has_permissions(administrator=True)
    async def soru_ekle(self, interaction: discord.Interaction, soru: str):
        self.config['sorular'].append(soru)
        self.save_config()
        toplam = len(self.config['sorular'])
        sayfa = (toplam - 1) // 5 + 1
        await interaction.response.send_message(
            f"✅ Soru eklendi: **{soru}**\n📊 Toplam soru: {toplam} (Sayfa {sayfa})"
        )
    
    @app_commands.command(name="kayıt-soru-sil", description="Kayıt sorusu silin")
    @app_commands.describe(index="Silinecek sorunun numarası (1'den başlar)")
    @app_commands.checks.has_permissions(administrator=True)
    async def soru_sil(self, interaction: discord.Interaction, index: int):
        if 1 <= index <= len(self.config['sorular']):
            silinen = self.config['sorular'].pop(index - 1)
            self.save_config()
            await interaction.response.send_message(f"✅ Soru silindi: **{silinen}**")
        else:
            await interaction.response.send_message("❌ Geçersiz soru numarası!")
    
    @app_commands.command(name="kayıt-sorular", description="Tüm kayıt sorularını listeleyin")
    @app_commands.checks.has_permissions(administrator=True)
    async def sorular(self, interaction: discord.Interaction):
        if not self.config['sorular']:
            await interaction.response.send_message("❌ Henüz soru eklenmemiş!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📝 Kayıt Soruları",
            color=discord.Color.blue()
        )
        for i, soru in enumerate(self.config['sorular'], 1):
            embed.add_field(name=f"Soru {i}", value=soru, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="kayit-mesaj-gonder", description="Kayıt mesajını yeniden gönderin")
    @app_commands.checks.has_permissions(administrator=True)
    async def kayit_mesaj_gonder(self, interaction: discord.Interaction):
        if self.config['kayit_kanal']:
            kanal = interaction.guild.get_channel(self.config['kayit_kanal'])
            if kanal:
                await self.send_kayit_mesaji(kanal)
                await interaction.response.send_message("✅ Kayıt mesajı gönderildi!")
            else:
                await interaction.response.send_message("❌ Kayıt kanalı bulunamadı!")
        else:
            await interaction.response.send_message("❌ Kayıt kanalı ayarlanmamış!")

class KayitButton(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="📝 Anayasayı Okudum, Kayıt Ol", style=discord.ButtonStyle.green, custom_id="kayit_baslat")
    async def kayit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.baslat_kayit(interaction)

class KayitModal(discord.ui.Modal):
    def __init__(self, cog, sorular, page, user_id):
        self.page = page
        total_pages = (len(cog.config['sorular']) - 1) // 5 + 1
        
        if total_pages > 1:
            title = f"📝 Kayıt Formu (Sayfa {page + 1}/{total_pages})"
        else:
            title = "📝 Kayıt Formu"
            
        super().__init__(title=title, timeout=600)
        self.cog = cog
        self.sorular = sorular
        self.user_id = user_id
        self.total_questions = len(cog.config['sorular'])
        
        # Bu sayfadaki soruları ekle (maksimum 5)
        start_index = page * 5
        for i, soru in enumerate(sorular, 1):
            # Kısa sorular için short, uzun açıklamalar için paragraph
            style = discord.TextStyle.short if len(soru) < 50 else discord.TextStyle.paragraph
            
            self.add_item(
                discord.ui.TextInput(
                    label=f"Soru {start_index + i}",
                    placeholder=soru[:100],  # Placeholder max 100 karakter
                    style=style,
                    required=True,
                    max_length=1024
                )
            )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.user_id not in self.cog.pending_registrations:
            await interaction.response.send_message(
                "❌ Kayıt oturumunuz sonlanmış!",
                ephemeral=True
            )
            return
        
        # Cevapları kaydet
        start_index = self.page * 5
        for i, child in enumerate(self.children):
            if isinstance(child, discord.ui.TextInput):
                self.cog.pending_registrations[self.user_id]['cevaplar'].append({
                    'soru': self.sorular[i],
                    'cevap': child.value
                })
        
        # Daha fazla soru var mı kontrol et
        next_page = self.page + 1
        total_pages = (self.total_questions - 1) // 5 + 1
        
        if next_page < total_pages:
            # Bir sonraki sayfa için buton göster
            view = NextPageView(self.cog, next_page, self.user_id)
            await interaction.response.send_message(
                f"✅ Sayfa {self.page + 1}/{total_pages} tamamlandı!\n🔄 Devam etmek için aşağıdaki butona basın.",
                view=view,
                ephemeral=True
            )
        else:
            # Tüm sorular tamamlandı
            await interaction.response.send_message(
                "✅ Kayıt formunuz başarıyla gönderildi! Yetkililerin onayını bekleyin.",
                ephemeral=True
            )
            
            data = self.cog.pending_registrations[self.user_id]
            await self.cog.gonder_onay(interaction.guild, interaction.user, data['cevaplar'])

class NextPageView(discord.ui.View):
    def __init__(self, cog, page, user_id):
        super().__init__(timeout=300)
        self.cog = cog
        self.page = page
        self.user_id = user_id
    
    @discord.ui.button(label="➡️ Sonraki Sayfa", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Bu sizin kayıt formunuz değil!", ephemeral=True)
            return
        
        # Sonraki 5 soruyu al
        start = self.page * 5
        end = start + 5
        sorular = self.cog.config['sorular'][start:end]
        
        modal = KayitModal(self.cog, sorular, self.page, self.user_id)
        await interaction.response.send_modal(modal)
        self.stop()

class OnayView(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.user_id = user_id
    
    @discord.ui.button(label="✅ Kabul Et", style=discord.ButtonStyle.success)
    async def kabul_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cog.kabul_et(interaction, self.user_id)
        self.stop()
    
    @discord.ui.button(label="❌ Reddet", style=discord.ButtonStyle.danger)
    async def red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ReddetModal(self.cog, self.user_id)
        await interaction.response.send_modal(modal)

class ReddetModal(discord.ui.Modal):
    def __init__(self, cog, user_id):
        super().__init__(title="❌ Kayıt Reddetme", timeout=300)
        self.cog = cog
        self.user_id = user_id
        
        self.add_item(
            discord.ui.TextInput(
                label="Red Sebebi",
                placeholder="Lütfen kayıt başvurusunu neden reddettiğinizi açıklayın...",
                style=discord.TextStyle.paragraph,
                required=True,
                min_length=1,
                max_length=500
            )
        )
    
    async def on_submit(self, interaction: discord.Interaction):
        sebep = self.children[0].value
        await self.cog.reddet(interaction, self.user_id, sebep)

async def setup(bot):
    await bot.add_cog(KayitSistemi(bot))

import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone, timedelta
import io
import re
import asyncio

# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='kb!', intents=intents)

# ./cogs klasöründeki tüm .py dosyalarını extension olarak yükleme
COGS_DIR = './cogs'

async def load_cogs():
    """cogs klasöründeki her .py dosyasını (isim _ ile başlamayanları) yükler"""
    if not os.path.isdir(COGS_DIR):
        print(f"⚠️ '{COGS_DIR}' klasörü bulunamadı, cog yükleme atlanıyor.")
        return

    for filename in os.listdir(COGS_DIR):
        if filename.endswith('.py') and not filename.startswith('_'):
            extension = f'cogs.{filename[:-3]}'
            try:
                await bot.load_extension(extension)
                print(f"✅ Cog yüklendi: {extension}")
            except commands.ExtensionAlreadyLoaded:
                print(f"ℹ️ Cog zaten yüklü: {extension}")
            except Exception as e:
                print(f"❌ Cog yüklenemedi: {extension} -> {e}")

@bot.event
async def setup_hook():
    await load_cogs()
    # Slash komutlarını senkronize et (app_commands kullanan cog'lar için)
    try:
        synced = await bot.tree.sync()
        print(f"🔄 {len(synced)} slash komut senkronize edildi.")
    except Exception as e:
        print(f"❌ Slash komutlar senkronize edilemedi: {e}")

# Sabıka verileri için dosya yolu
DATA_FILE = 'sabika_data.json'

# Türkiye saati (UTC+3)
TURKEY_TZ = timezone(timedelta(hours=3))

# Sabıka verilerini yükleme
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

# Sabıka verilerini kaydetme
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Kullanıcı ID'sini çıkartma (mention veya direkt ID)
def extract_user_id(user_input):
    """Kullanıcı mention'ından veya direkt ID'den user_id çıkartır"""
    if isinstance(user_input, str):
        # Mention formatı: <@123456789> veya <@!123456789>
        match = re.match(r'<@!?(\d+)>', user_input)
        if match:
            return int(match.group(1))
        # Direkt ID kontrolü
        if user_input.isdigit():
            return int(user_input)
    return None

# Kullanıcı bilgilerini alma (sunucuda olmasa da)
async def get_user_info(user_id, guild):
    """Kullanıcı bilgilerini çeşitli yöntemlerle almaya çalışır"""
    try:
        # Önce sunucudaki üyelerden kontrol et
        member = guild.get_member(user_id)
        if member:
            return {
                'id': user_id,
                'name': member.name,
                'display_name': member.display_name,
                'mention': member.mention,
                'in_guild': True
            }
        
        # Sunucuda değilse bot cache'inden kontrol et
        user = bot.get_user(user_id)
        if user:
            return {
                'id': user_id,
                'name': user.name,
                'display_name': user.display_name,
                'mention': user.mention,
                'in_guild': False
            }
        
        # Cache'de yoksa API'den çekmeye çalış
        try:
            user = await bot.fetch_user(user_id)
            return {
                'id': user_id,
                'name': user.name,
                'display_name': user.display_name,
                'mention': user.mention,
                'in_guild': False
            }
        except:
            # Hiçbir yerde bulunamadıysa
            return {
                'id': user_id,
                'name': f"Bilinmeyen Kullanıcı",
                'display_name': f"Bilinmeyen Kullanıcı ({user_id})",
                'mention': f"<@{user_id}>",
                'in_guild': False
            }
    except Exception:
        return {
            'id': user_id,
            'name': f"Bilinmeyen Kullanıcı",
            'display_name': f"Bilinmeyen Kullanıcı ({user_id})",
            'mention': f"<@{user_id}>",
            'in_guild': False
        }

# Türkiye saatini alma
def get_turkey_time():
    """Türkiye saatini döndürür (UTC+3)"""
    return datetime.now(TURKEY_TZ).strftime('%d.%m.%Y %H:%M')

# Sabıka txt dosyası oluşturma
def create_sabika_txt(user_info, sabikalar):
    """Tek kullanıcı için sabıka txt dosyası oluşturur"""
    content = "=" * 50 + "\n"
    content += f"SABIKA KAYDI - {user_info['display_name']}\n"
    content += "=" * 50 + "\n"
    content += f"Kullanıcı Adı: {user_info['name']}\n"
    content += f"Görüntülenen Ad: {user_info['display_name']}\n"
    content += f"Kullanıcı ID: {user_info['id']}\n"
    content += f"Sunucuda: {'Evet' if user_info['in_guild'] else 'Hayır'}\n"
    content += f"Rapor Tarihi: {get_turkey_time()}\n"
    content += f"Toplam Sabıka Sayısı: {len(sabikalar)}\n"
    content += "=" * 50 + "\n\n"
    
    if not sabikalar:
        content += "Bu kullanıcının sabıka kaydı bulunmamaktadır.\n"
    else:
        for i, sabika in enumerate(sabikalar, 1):
            content += f"{i}. SABIKA KAYDI\n"
            content += "-" * 20 + "\n"
            content += f"🚨 SUÇ: {sabika['suc']}\n"
            content += f"📅 TARİH: {sabika['tarih']}\n"
            content += f"👮 KAYDEDEN: {sabika['kaydeden']}\n"
            if 'aktar_tarihi' in sabika:
                content += f"📋 AKTARIM TARİHİ: {sabika['aktar_tarihi']}\n"
                content += f"🔄 AKTARAN: {sabika['aktaran']}\n"
            content += "\n"
    
    content += "=" * 50 + "\n"
    content += "Bu rapor Discord Sabıka Botu tarafından oluşturulmuştur.\n"
    
    return content

# Global veri
sabika_data = load_data()

class SabikaView(discord.ui.View):
    def __init__(self, user_id, user_info, sabikalar, guild):
        super().__init__(timeout=600)  # 10 dakika timeout
        self.user_id = str(user_id)
        self.user_info = user_info
        self.sabikalar = sabikalar
        self.guild = guild
        self.current_page = 0
        self.update_buttons()
    
    async def on_timeout(self):
        # Timeout olduğunda butonları devre dışı bırak
        for item in self.children:
            item.disabled = True
        
        # Mesajı güncelle (hata yakalama ile)
        try:
            embed = discord.Embed(
                title="⏰ Oturum Süresi Doldu",
                description="Güvenlik nedeniyle butonlar devre dışı bırakıldı. Yeniden görüntülemek için komutu tekrar çalıştırın.",
                color=0xff9900
            )
            # Bu fonksiyon interaction message'ını güncellemek için kullanılır
            # Ama biz burada message objesine erişemiyoruz, bu yüzden sadece view'i devre dışı bırakıyoruz
        except:
            pass
    
    def update_buttons(self):
        self.clear_items()
        
        # Sayfalama için önceki/sonraki butonlar
        if len(self.sabikalar) > 1:
            previous_btn = discord.ui.Button(
                label="◀️ Önceki",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page == 0
            )
            previous_btn.callback = self.previous_page
            self.add_item(previous_btn)
            
            next_btn = discord.ui.Button(
                label="Sonraki ▶️",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_page >= len(self.sabikalar) - 1
            )
            next_btn.callback = self.next_page
            self.add_item(next_btn)
        
        # Silme butonu
        if self.sabikalar:
            delete_btn = discord.ui.Button(
                label="🗑️ Bu Sabıkayı Sil",
                style=discord.ButtonStyle.danger
            )
            delete_btn.callback = self.delete_current
            self.add_item(delete_btn)
        
        # TXT dosyası gönderme butonu
        txt_btn = discord.ui.Button(
            label="📄 Sabıkayı TXT Olarak Gönder",
            style=discord.ButtonStyle.primary,
            emoji="📄"
        )
        txt_btn.callback = self.send_txt_file
        self.add_item(txt_btn)
    
    async def previous_page(self, interaction: discord.Interaction):
        # Yetki kontrolü
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bu butonu kullanmak için **Administrator** yetkisi gereklidir!", ephemeral=True)
            return
            
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        # Yetki kontrolü
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bu butonu kullanmak için **Administrator** yetkisi gereklidir!", ephemeral=True)
            return
            
        if self.current_page < len(self.sabikalar) - 1:
            self.current_page += 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def delete_current(self, interaction: discord.Interaction):
        # Yetki kontrolü - Administrator yetkisi gerekli
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bu butonu kullanmak için **Administrator** yetkisi gereklidir!", ephemeral=True)
            return
            
        if self.sabikalar and self.current_page < len(self.sabikalar):
            # Sabıkayı sil
            deleted_sabika = self.sabikalar.pop(self.current_page)
            
            # Veriyi güncelle
            global sabika_data
            if self.sabikalar:
                sabika_data[self.user_id] = self.sabikalar
            else:
                # Tüm sabıkalar silindiyse kullanıcıyı tamamen kaldır
                if self.user_id in sabika_data:
                    del sabika_data[self.user_id]
            
            save_data(sabika_data)
            
            # Sayfa kontrolü
            if self.current_page >= len(self.sabikalar) and self.current_page > 0:
                self.current_page = len(self.sabikalar) - 1
            
            if not self.sabikalar:
                # Hiç sabıka kalmadıysa
                embed = discord.Embed(
                    title=f"📋 {self.user_info['display_name']} - Sabıka Kaydı",
                    description="Bu kullanıcının sabıka kaydı bulunmamaktadır.",
                    color=0x00ff00
                )
                
                # Kullanıcı sunucada değilse bilgi ver
                if not self.user_info['in_guild']:
                    embed.add_field(name="ℹ️ Durum", value="Kullanıcı şu anda sunucuda değil", inline=False)
                
                # Sadece TXT butonu ekle
                new_view = discord.ui.View(timeout=600)
                txt_btn = discord.ui.Button(
                    label="📄 Sabıkayı TXT Olarak Gönder",
                    style=discord.ButtonStyle.primary,
                    emoji="📄"
                )
                txt_btn.callback = self.send_txt_file
                new_view.add_item(txt_btn)
                
                await interaction.response.edit_message(embed=embed, view=new_view)
            else:
                self.update_buttons()
                embed = self.create_embed()
                await interaction.response.edit_message(embed=embed, view=self)
            
            # Silme başarılı mesajı
            await interaction.followup.send(f"✅ Sabıka silindi: {deleted_sabika['suc']}", ephemeral=True)
    
    async def send_txt_file(self, interaction: discord.Interaction):
        # Yetki kontrolü
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bu butonu kullanmak için **Administrator** yetkisi gereklidir!", ephemeral=True)
            return
        
        # TXT dosyası içeriği oluştur
        content = create_sabika_txt(self.user_info, self.sabikalar)
        
        # Dosya adı oluştur
        safe_name = re.sub(r'[^\w\s-]', '', self.user_info['display_name']).strip()
        safe_name = re.sub(r'[-\s]+', '-', safe_name)
        file_name = f"sabika_{safe_name}_{self.user_id}_{datetime.now(TURKEY_TZ).strftime('%d-%m-%Y_%H-%M')}.txt"
        
        # Discord dosyası oluştur
        discord_file = discord.File(
            io.BytesIO(content.encode('utf-8')),
            filename=file_name
        )
        
        # DM ile gönder
        try:
            dm_embed = discord.Embed(
                title="📄 Sabıka Raporu",
                description=f"**{self.user_info['display_name']}** kullanıcısının sabıka raporu:",
                color=0x0099ff
            )
            dm_embed.add_field(name="📊 Toplam Sabıka", value=str(len(self.sabikalar)), inline=True)
            dm_embed.add_field(name="📅 Rapor Tarihi", value=get_turkey_time(), inline=True)
            dm_embed.add_field(name="🏢 Sunucu", value=self.guild.name, inline=True)
            
            await interaction.user.send(embed=dm_embed, file=discord_file)
            await interaction.response.send_message("✅ Sabıka raporu DM'inize gönderildi!", ephemeral=True)
        
        except discord.Forbidden:
            await interaction.response.send_message("❌ DM'iniz kapalı! Rapor gönderilemedi. Lütfen DM'inizi açın ve tekrar deneyin.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Dosya gönderilirken hata oluştu: {str(e)}", ephemeral=True)
    
    def create_embed(self):
        if not self.sabikalar:
            embed = discord.Embed(
                title=f"📋 {self.user_info['display_name']} - Sabıka Kaydı",
                description="Bu kullanıcının sabıka kaydı bulunmamaktadır.",
                color=0x00ff00
            )
        else:
            sabika = self.sabikalar[self.current_page]
            embed = discord.Embed(
                title=f"📋 {self.user_info['display_name']} - Sabıka Kaydı",
                color=0xff0000
            )
            
            embed.add_field(
                name="🚨 Suç",
                value=sabika['suc'],
                inline=False
            )
            
            embed.add_field(
                name="📅 Tarih",
                value=sabika['tarih'],
                inline=True
            )
            
            embed.add_field(
                name="👮 Kaydeden",
                value=sabika['kaydeden'],
                inline=True
            )
            
            if len(self.sabikalar) > 1:
                embed.set_footer(text=f"Sayfa {self.current_page + 1}/{len(self.sabikalar)}")
        
        # Kullanıcı sunucada değilse bilgi ekle
        if not self.user_info['in_guild']:
            embed.add_field(name="ℹ️ Durum", value="Kullanıcı şu anda sunucuda değil", inline=False)
        
        return embed

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')
    print(f'Bot {len(bot.guilds)} sunucuda aktif!')


@bot.command(name='sabıka')
async def sabika_ekle(ctx, kullanici_input, *, suc):
    """Kullanıcıya sabıka ekler (mention veya ID ile)"""
    
    # Yetki kontrolü - Administrator yetkisi gerekli
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Bu komutu kullanmak için **Administrator** yetkisi gereklidir!")
        return
    
    # Kullanıcı ID'sini çıkart
    user_id = extract_user_id(kullanici_input)
    if not user_id:
        await ctx.send("❌ Geçersiz kullanıcı! Lütfen @kullanıcı veya kullanıcı ID'si kullanın.")
        return
    
    # Kullanıcı bilgilerini al
    user_info = await get_user_info(user_id, ctx.guild)
    
    # Sabıka verisi oluştur
    sabika_entry = {
        'suc': suc,
        'tarih': get_turkey_time(),
        'kaydeden': str(ctx.author),
        'kaydeden_id': str(ctx.author.id),
        'kullanici_adi': user_info['name'],
        'kullanici_display_name': user_info['display_name']
    }
    
    # Kullanıcının sabıka listesini al veya oluştur
    user_id_str = str(user_id)
    if user_id_str not in sabika_data:
        sabika_data[user_id_str] = []
    
    sabika_data[user_id_str].append(sabika_entry)
    save_data(sabika_data)
    
    # Başarı mesajı
    embed = discord.Embed(
        title="✅ Sabıka Eklendi",
        description=f"**{user_info['mention']}** kullanıcısına sabıka eklendi.",
        color=0x00ff00
    )
    embed.add_field(name="🚨 Suç", value=suc, inline=False)
    embed.add_field(name="📅 Tarih", value=sabika_entry['tarih'], inline=True)
    embed.add_field(name="👮 Kaydeden", value=ctx.author.mention, inline=True)
    
    # Kullanıcı sunucada değilse bilgi ver
    if not user_info['in_guild']:
        embed.add_field(name="ℹ️ Durum", value="Kullanıcı şu anda sunucuda değil", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='sabıka-gör')
async def sabika_gor(ctx, kullanici_input):
    """Kullanıcının sabıka kaydını gösterir (mention veya ID ile)"""
    
    # Yetki kontrolü - Administrator yetkisi gerekli
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Bu komutu kullanmak için **Administrator** yetkisi gereklidir!")
        return
    
    # Kullanıcı ID'sini çıkart
    user_id = extract_user_id(kullanici_input)
    if not user_id:
        await ctx.send("❌ Geçersiz kullanıcı! Lütfen @kullanıcı veya kullanıcı ID'si kullanın.")
        return
    
    # Kullanıcı bilgilerini al
    user_info = await get_user_info(user_id, ctx.guild)
    user_id_str = str(user_id)
    
    # Sabıka verilerini al
    sabikalar = sabika_data.get(user_id_str, [])
    
    # Sabıka görüntüleme view'i oluştur
    view = SabikaView(user_id, user_info, sabikalar, ctx.guild)
    embed = view.create_embed()
    
    await ctx.send(embed=embed, view=view)

@bot.command(name='sabıka-aktar')
async def sabika_aktar(ctx, kullanici1_input, kullanici2_input):
    """Kullanıcı1'in tüm sabıkasını kullanıcı2'ye kopyalar"""
    
    # Yetki kontrolü - Administrator yetkisi gerekli
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Bu komutu kullanmak için **Administrator** yetkisi gereklidir!")
        return
    
    # Kullanıcı ID'lerini çıkart
    user1_id = extract_user_id(kullanici1_input)
    user2_id = extract_user_id(kullanici2_input)
    
    if not user1_id or not user2_id:
        await ctx.send("❌ Geçersiz kullanıcı! Lütfen @kullanıcı veya kullanıcı ID'si kullanın.")
        return
    
    if user1_id == user2_id:
        await ctx.send("❌ Aynı kullanıcının sabıkasını kendisine aktaramazsınız!")
        return
    
    # Kullanıcı bilgilerini al
    user1_info = await get_user_info(user1_id, ctx.guild)
    user2_info = await get_user_info(user2_id, ctx.guild)
    
    user1_id_str = str(user1_id)
    user2_id_str = str(user2_id)
    
    # Kullanıcı1'in sabıkası var mı kontrol et
    if user1_id_str not in sabika_data or not sabika_data[user1_id_str]:
        await ctx.send(f"❌ {user1_info['mention']} kullanıcısının aktarılacak sabıka kaydı bulunmamaktadır!")
        return
    
    # Kullanıcı2'nin sabıka listesini al veya oluştur
    if user2_id_str not in sabika_data:
        sabika_data[user2_id_str] = []
    
    # Sabıkaları kopyala ve kullanıcı2'ye ekle
    aktarilan_sabika_sayisi = 0
    for sabika in sabika_data[user1_id_str]:
        # Sabıkayı kopyala ve kullanıcı2'nin bilgileriyle güncelle
        yeni_sabika = sabika.copy()
        yeni_sabika['kullanici_adi'] = user2_info['name']
        yeni_sabika['kullanici_display_name'] = user2_info['display_name']
        
        # Orijinal sabıka bilgisini ekle
        yeni_sabika['suc'] = f"[AKTARILDI: {user1_info['display_name']}] {sabika['suc']}"
        yeni_sabika['aktar_tarihi'] = get_turkey_time()
        yeni_sabika['aktaran'] = str(ctx.author)
        
        sabika_data[user2_id_str].append(yeni_sabika)
        aktarilan_sabika_sayisi += 1
    
    save_data(sabika_data)
    
    # Başarı mesajı
    embed = discord.Embed(
        title="✅ Sabıka Aktarımı Tamamlandı",
        description=f"**{user1_info['mention']}** kullanıcısının sabıka kayıtları **{user2_info['mention']}** kullanıcısına aktarıldı.",
        color=0x00ff00
    )
    embed.add_field(name="📊 Aktarılan Kayıt Sayısı", value=str(aktarilan_sabika_sayisi), inline=True)
    embed.add_field(name="📅 Aktarım Tarihi", value=get_turkey_time(), inline=True)
    embed.add_field(name="👮 Aktaran", value=ctx.author.mention, inline=True)
    
    # Kullanıcılar sunucada değilse bilgi ver
    durum_bilgisi = []
    if not user1_info['in_guild']:
        durum_bilgisi.append(f"• {user1_info['display_name']} şu anda sunucuda değil")
    if not user2_info['in_guild']:
        durum_bilgisi.append(f"• {user2_info['display_name']} şu anda sunucuda değil")
    
    if durum_bilgisi:
        embed.add_field(name="ℹ️ Durum", value="\n".join(durum_bilgisi), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='sabıkalar')
async def tum_sabikalar(ctx):
    """Tüm kullanıcıların sabıkalarını txt dosyası olarak gönderir"""
    
    # Yetki kontrolü
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Bu komutu kullanmak için yönetici yetkisi gereklidir!")
        return
    
    if not sabika_data:
        await ctx.send("❌ Hiç sabıka kaydı bulunmamaktadır!")
        return
    
    # Txt dosyası içeriği oluştur
    content = "=" * 50 + "\n"
    content += "SABIKA KAYITLARI\n"
    content += "=" * 50 + "\n"
    content += f"Oluşturulma Tarihi: {get_turkey_time()}\n"
    content += f"Sunucu: {ctx.guild.name}\n"
    content += "=" * 50 + "\n\n"
    
    for user_id, sabikalar in sabika_data.items():
        try:
            # Kullanıcı bilgilerini al
            user_info = await get_user_info(int(user_id), ctx.guild)
            username = user_info['name']
            display_name = user_info['display_name']
            in_guild = user_info['in_guild']
        except:
            username = f"Bilinmeyen Kullanıcı ({user_id})"
            display_name = username
            in_guild = False
        
        content += f"👤 KULLANICI: {display_name} ({username})\n"
        content += f"🆔 ID: {user_id}\n"
        content += f"📊 Toplam Sabıka: {len(sabikalar)}\n"
        content += f"📍 Sunucuda: {'Evet' if in_guild else 'Hayır'}\n"
        content += "-" * 30 + "\n"
        
        for i, sabika in enumerate(sabikalar, 1):
            content += f"{i}. 🚨 SUÇ: {sabika['suc']}\n"
            content += f"   📅 TARİH: {sabika['tarih']}\n"
            content += f"   👮 KAYDEDEN: {sabika['kaydeden']}\n"
            if 'aktar_tarihi' in sabika:
                content += f"   📋 AKTARIM TARİHİ: {sabika['aktar_tarihi']}\n"
                content += f"   🔄 AKTARAN: {sabika['aktaran']}\n"
            content += "\n"
        
        content += "=" * 50 + "\n\n"
    
    # Dosya oluştur ve gönder (DM ile güvenli gönderim)
    file_buffer = io.StringIO(content)
    file_name = f"sabika_kayitlari_{datetime.now(TURKEY_TZ).strftime('%d-%m-%Y_%H-%M')}.txt"
    
    discord_file = discord.File(
        io.BytesIO(content.encode('utf-8')),
        filename=file_name
    )
    
    embed = discord.Embed(
        title="📄 Sabıka Kayıtları",
        description=f"Güvenlik nedeniyle sabıka kayıtları **DM** ile gönderildi.",
        color=0x0099ff
    )
    embed.add_field(name="📊 Toplam Kullanıcı", value=str(len(sabika_data)), inline=True)
    embed.add_field(name="📋 Toplam Sabıka", value=str(sum(len(sabikalar) for sabikalar in sabika_data.values())), inline=True)
    
    # Önce kanala bilgilendirme mesajı gönder
    await ctx.send(embed=embed)
    
    # Sonra dosyayı DM ile gönder
    try:
        dm_embed = discord.Embed(
            title="🔒 Sabıka Kayıtları (Gizli)",
            description=f"**{ctx.guild.name}** sunucusunun sabıka kayıtları:",
            color=0xff0000
        )
        await ctx.author.send(embed=dm_embed, file=discord_file)
    except discord.Forbidden:
        await ctx.send("❌ DM'iniz kapalı! Dosya gönderilemedi. Lütfen DM'inizi açın ve tekrar deneyin.")
        return

@bot.command(name='sabıka-temizle')
async def sabika_temizle(ctx, kullanici_input):
    """Kullanıcının tüm sabıka kayıtlarını temizler (mention veya ID ile)"""
    
    # Yetki kontrolü
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Bu komutu kullanmak için yönetici yetkisi gereklidir!")
        return
    
    # Kullanıcı ID'sini çıkart
    user_id = extract_user_id(kullanici_input)
    if not user_id:
        await ctx.send("❌ Geçersiz kullanıcı! Lütfen @kullanıcı veya kullanıcı ID'si kullanın.")
        return
    
    # Kullanıcı bilgilerini al
    user_info = await get_user_info(user_id, ctx.guild)
    user_id_str = str(user_id)
    
    if user_id_str not in sabika_data:
        await ctx.send(f"❌ {user_info['mention']} kullanıcısının sabıka kaydı bulunmamaktadır!")
        return
    
    # Sabıka kayıtlarını sil
    sabika_sayisi = len(sabika_data[user_id_str])
    del sabika_data[user_id_str]
    save_data(sabika_data)
    
    embed = discord.Embed(
        title="🗑️ Sabıka Kayıtları Temizlendi",
        description=f"**{user_info['mention']}** kullanıcısının tüm sabıka kayıtları temizlendi.",
        color=0x00ff00
    )
    embed.add_field(name="📊 Silinen Kayıt Sayısı", value=str(sabika_sayisi), inline=True)
    
    # Kullanıcı sunucada değilse bilgi ver
    if not user_info['in_guild']:
        embed.add_field(name="ℹ️ Durum", value="Kullanıcı şu anda sunucuda değil", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='yardım')
async def yardim(ctx):
    """Bot komutlarını gösterir"""
    
    # Yetki kontrolü - Administrator yetkisi gerekli
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Bu komutu kullanmak için **Administrator** yetkisi gereklidir!")
        return
    
    embed = discord.Embed(
        title="🤖 Sabıka Botu Komutları",
        description="Aşağıdaki komutları kullanabilirsiniz:",
        color=0x0099ff
    )
    
    embed.add_field(
        name="📝 kb!sabıka @kullanıcı/ID suç",
        value="Kullanıcıya sabıka ekler (Admin)",
        inline=False
    )
    
    embed.add_field(
        name="👀 kb!sabıka-gör @kullanıcı/ID",
        value="Kullanıcının sabıka kayıtlarını gösterir (Admin)",
        inline=False
    )
    
    embed.add_field(
        name="🔄 kb!sabıka-aktar @kullanıcı1/ID1 @kullanıcı2/ID2",
        value="Kullanıcı1'in sabıkasını kullanıcı2'ye kopyalar (Admin)",
        inline=False
    )
    
    embed.add_field(
        name="📄 kb!sabıkalar",
        value="Tüm sabıka kayıtlarını txt dosyası olarak gönderir (Admin)",
        inline=False
    )
    
    embed.add_field(
        name="🗑️ kb!sabıka-temizle @kullanıcı/ID",
        value="Kullanıcının tüm sabıka kayıtlarını siler (Admin)",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ kb!yardım",
        value="Bu yardım mesajını gösterir (Admin)",
        inline=False
    )
    
    embed.add_field(
        name="🌟 Özellikler",
        value="• Sunucuda olmayan kullanıcılar için de çalışır\n• Kullanıcı ID'si ile de kullanılabilir\n• Saat UTC+3 (Türkiye saati)\n• İnteraktif butonlar ile kolay yönetim",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Hata yönetimi - Güvenli hata mesajları
@sabika_ekle.error
async def sabika_ekle_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kullanım: `kb!sabıka @kullanıcı/ID suç açıklaması`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Belirtilen kullanıcı bulunamadı!")
    else:
        await ctx.send("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

@sabika_gor.error
async def sabika_gor_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kullanım: `kb!sabıka-gör @kullanıcı/ID`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Belirtilen kullanıcı bulunamadı!")
    else:
        await ctx.send("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

@sabika_aktar.error
async def sabika_aktar_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kullanım: `kb!sabıka-aktar @kullanıcı1/ID1 @kullanıcı2/ID2`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Belirtilen kullanıcı bulunamadı!")
    else:
        await ctx.send("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

@sabika_temizle.error
async def sabika_temizle_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Kullanım: `kb!sabıka-temizle @kullanıcı/ID`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Belirtilen kullanıcı bulunamadı!")
    else:
        await ctx.send("❌ Bir hata oluştu. Lütfen tekrar deneyin.")

@tum_sabikalar.error
async def tum_sabikalar_error(ctx, error):
    await ctx.send("❌ Dosya oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.")

# Botu çalıştır
if __name__ == "__main__":
    # Bot tokenı ortam değişkeninden okunur (DISCORD_BOT_TOKEN)
    BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Lütfen bot tokenınızı kodda belirtin!")
        print("Bot tokenını Discord Developer Portal'dan alabilirsiniz.")
    else:
        try:
            bot.run(BOT_TOKEN)
        except discord.LoginFailure:
            print("❌ Geçersiz bot tokeni!")
        except Exception as e:
            print(f"❌ Bot çalıştırılırken hata oluştu: {e}")
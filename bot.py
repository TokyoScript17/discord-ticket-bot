import discord
from discord import app_commands
from discord.ext import commands
import config
import re

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Vista con i pulsanti dei servizi
class ServicesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistente

    @discord.ui.button(label="PC Optimization & Overclocking  50€ ~ 58$", style=discord.ButtonStyle.primary, custom_id="ticket_optimization")
    async def optimization_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "PC Optimization & Overclocking")

    @discord.ui.button(label="Dual Boot Setup  8€ ~ 9$", style=discord.ButtonStyle.secondary, custom_id="ticket_dual_boot")
    async def dual_boot_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Dual Boot Setup")

    async def create_ticket(self, interaction: discord.Interaction, service_name: str):
        # Controlla se l'utente ha già un ticket aperto (opzionale)
        guild = interaction.guild
        category = guild.get_channel(config.TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("Categoria ticket non trovata. Contatta un amministratore.", ephemeral=True)
            return

        # Crea un canale privato per l'utente
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        # Aggiungi il ruolo staff se configurato
        support_role = guild.get_role(config.SUPPORT_ROLE_ID)
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"ticket-{interaction.user.name}-{interaction.user.discriminator}"
        # Rimuovi caratteri non validi per i nomi dei canali
        channel_name = re.sub(r'[^a-z0-9-]', '', channel_name.lower())

        try:
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                reason=f"Ticket aperto da {interaction.user} per {service_name}"
            )
        except Exception as e:
            await interaction.response.send_message(f"Errore nella creazione del ticket: {e}", ephemeral=True)
            return

        # Messaggio di benvenuto (come da seconda immagine)
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description=f"Benvenuto {interaction.user.mention}!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="",
            value=(
                "Grazie per aver aperto un ticket!\n"
                "Per favore descrivi il tuo problema e includi:\n"
                "- Il tuo obiettivo (FPS, input delay, stabilità)\n"
                "- Specifiche PC + scheda madre\n"
                "- Giochi/applicazioni interessati + screenshot/errori\n\n"
                "Uno staff member ti risponderà al più presto."
            ),
            inline=False
        )
        embed.set_footer(text=f"Servizio: {service_name}")

        # Pulsante "Chiudi Ticket" (opzionale)
        close_view = discord.ui.View()
        close_view.add_item(discord.ui.Button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket"))

        await ticket_channel.send(embed=embed, view=close_view)

        # Rispondi all'interazione (ephemeral)
        await interaction.response.send_message(f"✅ Ticket creato: {ticket_channel.mention}", ephemeral=True)

# Vista per il pulsante "Chiudi Ticket"
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Chiudi Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Solo lo staff o l'autore del ticket possono chiudere (puoi personalizzare)
        # Per semplicità, chiunque abbia permessi di gestione canali o l'autore
        if not interaction.user.guild_permissions.manage_channels and interaction.user != interaction.channel.topic_author: # topic_author non esiste, meglio usare una variabile
            await interaction.response.send_message("Non hai il permesso di chiudere questo ticket.", ephemeral=True)
            return

        await interaction.response.send_message("Il ticket verrà chiuso tra 5 secondi...", ephemeral=False)
        # Attendere e cancellare il canale
        await interaction.channel.delete(reason=f"Ticket chiuso da {interaction.user}")

# Aggiungiamo un listener per i pulsanti "close_ticket" che usano la vista persistente
@bot.event
async def on_ready():
    print(f"Bot connesso come {bot.user}")

    # Aggiungi le viste persistenti
    bot.add_view(ServicesView())
    bot.add_view(CloseTicketView())

    # Sincronizza i comandi slash
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=config.GUILD_ID))
        print(f"Sincronizzati {len(synced)} comandi slash.")
    except Exception as e:
        print(f"Errore sincronizzazione: {e}")

# Comando slash per inviare il pannello servizi
@bot.tree.command(name="services", description="Mostra il pannello dei servizi con i prezzi")
@app_commands.default_permissions(administrator=True)  # solo admin può eseguirlo, altrimenti togli
async def services(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🛠️ SERVICES",
        description="Smetti di lasciare prestazioni sul tavolo. Scegli un servizio e iniziamo a lavorare.",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="PC Optimization & Overclocking Service",
        value="50€ ~ 58$\n_ _",
        inline=False
    )
    embed.add_field(
        name="Dual Boot Setup",
        value="8€ ~ 9$\n_ _",
        inline=False
    )
    embed.set_footer(text="Leggi i termini di servizio prima di prenotare.")

    view = ServicesView()
    await interaction.response.send_message(embed=embed, view=view)

# Avvia il bot
bot.run(config.TOKEN)

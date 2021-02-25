"""
{
  "embed": {
    "description": "🟡 This is text",
    "color": 13224481,
    "footer": {
      "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png",
      "text": "Warbler"
    }
  }
}

https://leovoel.github.io/embed-visualizer/
"""

# Error
embed = discord.Embed(colour=discord.Colour(0xd81e45), description="❌ We hit a error.")
embed.set_footer(text="Warbler", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
await bot.say(embed=embed)
# Success
embed = discord.Embed(colour=discord.Colour(0x59b82b), description="✔️ It worked!")
embed.set_footer(text="Warbler", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
await bot.say(embed=embed)
# Warn
embed = discord.Embed(colour=discord.Colour(0xc9ca21), description="🟡 This is a warning")
embed.set_footer(text="Warbler", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
await bot.say(embed=embed)
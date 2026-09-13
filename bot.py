import requests
import asyncio
from telegram import Bot

# ================= البيانات الخاصة بك =================
TELEGRAM_TOKEN = "8535103152:AAGlnovpRReXe9hrWz9qb0aVdaOEw8KNH8g"
CHAT_ID = "7861179502"
LUNARCRUSH_API_KEY = "tnvx15cju9hohuyp2aj3ef9cromtz5ebh5cuuszts"
# =======================================================

def get_lunarcrush_trending_coins():
    """جلب قائمة العملات الأكثر حديثاً وهايباً من LunarCrush"""
    print("🔍 جاري جلب العملات ذات الزخم الاجتماعي العالي (Hype) من LunarCrush...")
    
    # واجهة LunarCrush الخاصة بالعملات الشهيرة والأكثر تفاعلاً
    url = "https://lunarcrush.com/api3/public/coins/list"
    headers = {'Authorization': f'Bearer {LUNARCRUSH_API_KEY}'}
    
    hype_tokens = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📡 حالة اتصال LunarCrush API: {response.status_code}")
        
        if response.status_code != 200:
            return []
            
        data = response.json()
        coins = data.get('data', [])
        
        for coin in coins:
            symbol = coin.get('symbol', '').upper()
            name = coin.get('name', '')
            social_score = coin.get('social_score', 0)
            social_volume = coin.get('social_volume', 0)
            price = coin.get('price', 0)
            
            # نفحص العملات التي لديها تفاعل اجتماعي نشط
            if social_volume > 10:  # شرط أن يكون هناك حديث عنها
                # الآن نتحقق من تفاصيلها عبر DexScreener لمعرفة إذا كانت على شبكة سولانا ولجلب العقد الخاص بها
                dex_url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
                try:
                    dex_res = requests.get(dex_url, timeout=5)
                    if dex_res.status_code == 200:
                        dex_data = dex_res.json()
                        pairs = dex_data.get('pairs', [])
                        
                        for pair in pairs:
                            # التأكد حصرياً أنها على شبكة سولانا
                            if pair.get('chainId') == 'solana':
                                token_address = pair.get('baseToken', {}).get('address', '')
                                pair_url = pair.get('url', '')
                                liquidity = pair.get('liquidity', {}).get('usd', 0)
                                
                                if token_address:
                                    hype_tokens.append({
                                        'symbol': symbol,
                                        'name': name,
                                        'price': price,
                                        'social_volume': social_volume,
                                        'social_score': social_score,
                                        'liquidity': liquidity,
                                        'address': token_address,
                                        'link': pair_url
                                    })
                                    print(f"🔥 تم العثور على عملة هايب على سولانا: ${symbol} - تفاعل: {social_volume}")
                                    break
                except:
                    continue
                    
        return hype_tokens
    except Exception as e:
        print(f"❌ خطأ تقني أثناء جلب بيانات LunarCrush: {e}")
        return []

async def run_bot():
    bot = Bot(token=TELEGRAM_TOKEN)
    sent_tokens = set()
    
    print("🚀 رادار الهايب الاجتماعي يعمل الآن (كل 30 ثانية)...")
    try:
        await bot.send_message(chat_id=CHAT_ID, text="🔥 تم تفعيل رادار الهايب (LunarCrush) حصرياً للعملات التي يتحدث عنها الناس على شبكة سولانا!")
    except Exception as e:
        print(f"❌ خطأ في إرسال رسالة التليجرام: {e}")

    while True:
        print("\n-----------------------------------------")
        tokens = get_lunarcrush_trending_coins()
        print(f"🔎 عدد عملات الهايب المتاحة للإرسال: {len(tokens)}")
        
        for token in tokens:
            symbol = token['symbol']
            
            if symbol not in sent_tokens:
                msg = (
                    f"🚨 **عملة عليها هايب عالي في السوشيال ميديا!** 🚨\n\n"
                    f"🪙 **الاسم:** {token['name']} (${symbol})\n"
                    f"💬 **حجم التفاعل (LunarCrush):** {token['social_volume']:,}\n"
                    f"⭐ **الدرجة الاجتماعية:** {token['social_score']}\n"
                    f"💵 **السعر:** ${token['price']}\n"
                    f"💧 **السيولة:** ${token['liquidity']:,.0f}\n\n"
                    f"📋 **عقد العملة (انسخه لـ Axiom):**\n`{token['address']}`\n\n"
                    f"🔗 [رابط الرسم البياني (Chart)]({token['link']})"
                )
                try:
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
                    sent_tokens.add(symbol)
                    print(f"📤 تم إرسال تنبيه الهايب للعملة ${symbol} بنجاح!")
                    await asyncio.sleep(1)
                except Exception as e:
                    print(f"❌ خطأ أثناء إرسال الرسالة: {e}")
            else:
                print(f"ℹ️ العملة ${symbol} أُرسلت مسبقاً، يتم تخطيها.")
                
        print("⏳ الانتظار لمدة 30 ثانية قبل فحص الهايب القادم...")
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_bot())

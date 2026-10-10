"""
BeforePay — Multi-Language User Alert Translations
-----------------------------------------------------
Razorpay AI Risk Manager — Track 02: AI Risk Manager

Provides vernacular language support for user-facing fraud alert messages.
NPCI and RBI mandate multilingual alerts for UPI fraud interventions.

Supported locales: en, hi, ta, te, bn
Alert keys: SOFT_WARNING, COOLING_OFF, HARD_INTERCEPT, NOMINEE_ALERT, SAFE_APPROVE
"""

# ──────────────────────────────────────────────────────────────────
# Translation Registry
# Keys → locale → alert string
# ──────────────────────────────────────────────────────────────────

TRANSLATIONS: dict[str, dict[str, str]] = {

    "SOFT_WARNING": {
        "en": "⚠️ You are on an active call. Are you being instructed by someone to transfer funds? Real banks and government agencies NEVER ask for transfers via UPI.",
        "hi": "⚠️ आप एक सक्रिय कॉल पर हैं। क्या कोई आपको पैसे ट्रांसफर करने का निर्देश दे रहा है? असली बैंक और सरकारी एजेंसियां कभी भी UPI से ट्रांसफर नहीं माँगतीं।",
        "ta": "⚠️ நீங்கள் ஒரு செயலில் உள்ள அழைப்பில் இருக்கிறீர்கள். யாரோ உங்களை பணம் பரிமாற்றம் செய்யுமாறு அறிவுறுத்துகிறார்களா? உண்மையான வங்கிகள் மற்றும் அரசு நிறுவனங்கள் UPI மூலம் பரிமாற்றம் கேட்கமாட்டார்கள்.",
        "te": "⚠️ మీరు యాక్టివ్ కాల్‌లో ఉన్నారు. ఎవరైనా మీకు నిధులు బదిలీ చేయమని సూచిస్తున్నారా? నిజమైన బ్యాంకులు మరియు ప్రభుత్వ సంస్థలు UPI ద్వారా బదిలీలు అడగవు.",
        "bn": "⚠️ আপনি একটি সক্রিয় কলে আছেন। কেউ কি আপনাকে তহবিল স্থানান্তর করতে নির্দেশ দিচ্ছে? আসল ব্যাংক এবং সরকারি সংস্থা কখনো UPI-এ স্থানান্তর চায় না।",
    },

    "COOLING_OFF": {
        "en": "⏳ This transfer has been paused for 15 minutes as a protective cooling-off period. Your nominee has been notified. You can override this with their confirmation.",
        "hi": "⏳ इस ट्रांसफर को सुरक्षात्मक कूलिंग-ऑफ अवधि के रूप में 15 मिनट के लिए रोका गया है। आपके नॉमिनी को सूचित किया गया है। उनकी पुष्टि से आप इसे ओवरराइड कर सकते हैं।",
        "ta": "⏳ இந்த பரிமாற்றம் 15 நிமிடங்களுக்கு பாதுகாப்பு குளிர்ச்சி காலமாக நிறுத்தப்பட்டுள்ளது. உங்கள் பரிந்துரைத்தவருக்கு அறிவிக்கப்பட்டுள்ளது. அவர்களின் உறுதிப்படுத்தலுடன் மேலெழுதலாம்.",
        "te": "⏳ ఈ బదిలీ రక్షణాత్మక కూలింగ్-ఆఫ్ వ్యవధిగా 15 నిమిషాలు పాజ్ చేయబడింది. మీ నామినీకి నోటిఫై చేయబడింది. వారి నిర్ధారణతో మీరు దీన్ని ఓవర్‌రైడ్ చేయవచ్చు.",
        "bn": "⏳ এই স্থানান্তর সুরক্ষামূলক কুলিং-অফ পিরিয়ড হিসেবে ১৫ মিনিটের জন্য বিরতি দেওয়া হয়েছে। আপনার মনোনীতকে অবহিত করা হয়েছে। তাদের নিশ্চিতকরণে ওভাররাইড করা যাবে।",
    },

    "HARD_INTERCEPT": {
        "en": "🚨 TRANSFER BLOCKED. We detected behavioral patterns of a Digital Arrest or AI Voice-Clone scam. Call 1930 (Cyber Crime Helpline) immediately if you believe you have been targeted.",
        "hi": "🚨 ट्रांसफर अवरुद्ध। हमने डिजिटल अरेस्ट या AI वॉयस-क्लोन स्कैम के व्यवहारिक संकेत पाए। यदि आप लक्षित हुए हैं तो तुरंत 1930 (साइबर क्राइम हेल्पलाइन) पर कॉल करें।",
        "ta": "🚨 பரிமாற்றம் தடுக்கப்பட்டது. டிஜிட்டல் கைது அல்லது AI குரல்-க்ளோன் மோசடியின் நடத்தை முறைகளை கண்டறிந்தோம். இலக்கு வைக்கப்பட்டதாக நம்பினால் உடனடியாக 1930 (சைபர் க்ரைம் ஹெல்ப்லைன்) அழைக்கவும்.",
        "te": "🚨 బదిలీ నిరోధించబడింది. డిజిటల్ అరెస్ట్ లేదా AI వాయిస్-క్లోన్ స్కామ్ యొక్క ప్రవర్తన నమూనాలను గుర్తించాము. లక్ష్యంగా చేయబడ్డారని భావిస్తే వెంటనే 1930కి కాల్ చేయండి.",
        "bn": "🚨 স্থানান্তর ব্লক করা হয়েছে। ডিজিটাল অ্যারেস্ট বা AI ভয়েস-ক্লোন স্কামের আচরণগত নমুনা সনাক্ত করা হয়েছে। লক্ষ্যবস্তু হয়েছেন বলে মনে করলে অবিলম্বে 1930-এ কল করুন।",
    },

    "NOMINEE_ALERT": {
        "en": "📱 Emergency Alert: {payer_name} is attempting a ₹{amount} transfer to an unverified account while on an active phone call. Tap 'Intercept' to pause this transfer.",
        "hi": "📱 आपातकालीन अलर्ट: {payer_name} एक सक्रिय फ़ोन कॉल के दौरान एक असत्यापित खाते में ₹{amount} ट्रांसफर करने की कोशिश कर रहे हैं। इस ट्रांसफर को रोकने के लिए 'इंटरसेप्ट' टैप करें।",
        "ta": "📱 அவசர எச்சரிக்கை: {payer_name} ஒரு செயலில் உள்ள தொலைபேசி அழைப்பில் இருக்கும்போது ஒரு சரிபார்க்கப்படாத கணக்கிற்கு ₹{amount} பரிமாற்ற முயற்சிக்கிறார்கள். இந்த பரிமாற்றத்தை நிறுத்த 'தடை' என்பதை தட்டவும்.",
        "te": "📱 అత్యవసర హెచ్చరిక: {payer_name} యాక్టివ్ ఫోన్ కాల్‌లో ఉండి ధృవీకరించబడని ఖాతాకు ₹{amount} బదిలీ చేయడానికి ప్రయత్నిస్తున్నారు. ఈ బదిలీని నిలిపివేయడానికి 'ఇంటర్‌సెప్ట్' నొక్కండి.",
        "bn": "📱 জরুরি সতর্কতা: {payer_name} একটি সক্রিয় ফোন কলে থাকাকালীন একটি অযাচাইকৃত অ্যাকাউন্টে ₹{amount} স্থানান্তর করার চেষ্টা করছেন। এই স্থানান্তর বিরতি দিতে 'ইন্টারসেপ্ট' ট্যাপ করুন।",
    },

    "SAFE_APPROVE": {
        "en": "✅ Transaction approved. Normal behavioral footprint — no coercion signals detected.",
        "hi": "✅ लेनदेन स्वीकृत। सामान्य व्यवहारिक पैटर्न — कोई जबरदस्ती संकेत नहीं मिला।",
        "ta": "✅ பரிமாற்றம் அங்கீகரிக்கப்பட்டது. சாதாரண நடத்தை தடம் — கட்டாய சமிக்ஞைகள் எதுவும் கண்டறியப்படவில்லை।",
        "te": "✅ లావాదేవీ ఆమోదించబడింది. సాధారణ ప్రవర్తన పాదముద్ర — బలవంతపు సంకేతాలు ఏవీ గుర్తించబడలేదు.",
        "bn": "✅ লেনদেন অনুমোদিত। স্বাভাবিক আচরণগত পদচিহ্ন — কোনো জবরদস্তির সংকেত সনাক্ত হয়নি।",
    },
}

# Maps action codes to alert keys
ACTION_TO_ALERT_KEY: dict[str, str] = {
    "AUTO_APPROVE":    "SAFE_APPROVE",
    "SOFT_WARNING":    "SOFT_WARNING",
    "COOLING_OFF_LOCK": "COOLING_OFF",
    "HARD_INTERCEPT":  "HARD_INTERCEPT",
}

SUPPORTED_LOCALES = ["en", "hi", "ta", "te", "bn"]


def get_alert(alert_key: str, locale: str = "en", **kwargs) -> str:
    """
    Returns a localized alert message for the given alert_key and locale.
    Falls back to English if the locale is unsupported.
    Supports .format(**kwargs) for dynamic values (e.g., payer_name, amount).

    Example:
        get_alert("NOMINEE_ALERT", locale="hi", payer_name="Priya", amount="85,000")
    """
    locale = locale if locale in SUPPORTED_LOCALES else "en"
    alerts = TRANSLATIONS.get(alert_key, {})
    template = alerts.get(locale) or alerts.get("en", "")
    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    return template


def get_alert_for_action(action: str, locale: str = "en", **kwargs) -> str:
    """
    Convenience wrapper: maps an action code directly to its localized alert.
    """
    key = ACTION_TO_ALERT_KEY.get(action, "SOFT_WARNING")
    return get_alert(key, locale, **kwargs)


if __name__ == "__main__":
    print("=== BeforePay — Multi-Language Alert Samples ===\n")
    for locale, lang in [("en", "English"), ("hi", "Hindi"), ("ta", "Tamil"),
                          ("te", "Telugu"), ("bn", "Bengali")]:
        msg = get_alert("HARD_INTERCEPT", locale=locale)
        print(f"[{lang}]\n  {msg}\n")

    print("[Nominee Alert — Hindi with dynamic values]")
    print(f"  {get_alert('NOMINEE_ALERT', 'hi', payer_name='Priya Sharma', amount='85,000')}")

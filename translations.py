from config import ASSISTANT_NAME
from helpers.bot_utils import BOT_NAME, USERNAME


START_TEXT = f"👋🏻 **Salut**, \n\nAceasta este **{BOT_NAME}** \nPot transmite live, radiouri, videoclipuri YouTube și fișiere audio/video Telegram pe chatul vocal al grupurilor Telegram. Să ne bucurăm de vizualizarea cinematografică a playerului video de grup cu prietenii tăi 😉! \n\n**Creatorul meu ❤️ AnastasiaV || SPT, pentru mai multe grupuri @uniunea !** 👑"
HELP_TEXT = f"""
🛠-- **Configurarea botului**:--

\u2022 Începeți chatul vocal în grupul dvs!
\u2022 Adaugă-mă (@{USERNAME}) & Asistentul meu (@{ASSISTANT_NAME}) Grupului tău !
\u2022 Fă-mi admin (@{USERNAME}) & Asistentul meu (@{ASSISTANT_NAME}) în grupul tău !

⚔️-- **Comenzi disponibile**:--

\u2022 `/play` - Stream An Audio
\u2022 `/stream` - Stream An Video
\u2022 `/pause` - Pauză Stream
\u2022 `/resume` - Reluare pauză Stream
\u2022 `/endstream` - Sfarșit Stream & Ieșire VC
\u2022 `/restart` - Restart Bot (Sudo Only)
"""
ABOUT_TEXT = f"💡-- **Informație**:-- \n\nAcest bot este creat pentru difuzarea videoclipurilor în chat-urile video de grup Telegram folosind mai multe metode de la WebRTC. Produs de pytgcalls the async client API-ul client asincron pentru apelurile de grup Telegram și Pyrogram-ul Telegram MTProto API Client Library and Framework în Pure Python pentru utilizatori și roboți. \n\n**Acest bot este licențiat sub GNU-GPL 3.0 License!**"

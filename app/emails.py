# SPDX-License-Identifier: BUSL-1.1
# Copyright (c) 2026 pyoneerC. All rights reserved.

"""
Email templates for Deadhand Protocol.
Supports: English (en), Spanish (es), Portuguese (pt), German (de), French (fr), Japanese (ja)
"""

SUPPORTED_LANGUAGES = ["en", "es", "pt", "de", "fr", "ja"]
DEFAULT_LANGUAGE = "en"


def get_language_from_email(email: str) -> str:
    """
    Heuristic: detect language from email TLD.
    Falls back to English if unknown.
    """
    if not email or "@" not in email:
        return DEFAULT_LANGUAGE

    domain = email.split("@")[-1].lower()

    if domain.endswith(".ar") or domain.endswith(".mx") or domain.endswith(".cl") or domain.endswith(".co") or domain.endswith(".pe") or domain.endswith(".uy"):
        return "es"
    if domain.endswith(".br"):
        return "pt"
    if domain.endswith(".de") or domain.endswith(".at") or domain.endswith(".ch"):
        return "de"
    if domain.endswith(".fr"):
        return "fr"
    if domain.endswith(".jp"):
        return "ja"

    return DEFAULT_LANGUAGE


# ---------------------------------------------------------------------------
# SUBJECTS
# ---------------------------------------------------------------------------

SUBJECTS = {
    "welcome": {
        "en": "not just a welcome email (and a drawing for you)",
        "es": "no es solo un email de bienvenida (y un dibujo para vos)",
        "pt": "não é só um e-mail de boas-vindas (e um desenho pra você)",
        "de": "nicht nur eine Willkommens-E-Mail (und eine Zeichnung für dich)",
        "fr": "pas juste un e-mail de bienvenue (et un dessin pour vous)",
        "ja": "ただの歓迎メールじゃありません（あなたへの絵も添えて）",
    },
    "cancellation": {
        "en": "your deadhand vault has been deactivated",
        "es": "tu vault de deadhand fue desactivado",
        "pt": "seu vault do deadhand foi desativado",
        "de": "dein deadhand-Vault wurde deaktiviert",
        "fr": "votre coffre deadhand a été désactivé",
        "ja": "deadhandのvaultが無効化されました",
    },
    "reminder_30d": {
        "en": "quick check-in from Deadhand",
        "es": "aviso rápido de Deadhand",
        "pt": "lembrete rápido do Deadhand",
        "de": "kurze Erinnerung von Deadhand",
        "fr": "petit rappel de Deadhand",
        "ja": "Deadhandからの確認",
    },
    "warning_60d": {
        "en": "urgent: we haven't heard from you in 60 days",
        "es": "urgente: no sabemos nada de vos hace 60 días",
        "pt": "urgente: não temos notícias suas há 60 dias",
        "de": "dringend: wir haben seit 60 Tagen nichts von dir gehört",
        "fr": "urgent : sans nouvelles depuis 60 jours",
        "ja": "緊急：60日間連絡がありません",
    },
    "death": {
        "en": "important: digital recovery key for {owner_email}",
        "es": "importante: clave de recuperación digital de {owner_email}",
        "pt": "importante: chave de recuperação digital de {owner_email}",
        "de": "wichtig: digitaler Wiederherstellungsschlüssel für {owner_email}",
        "fr": "important : clé de récupération numérique de {owner_email}",
        "ja": "重要：{owner_email}のデジタル回復キー",
    },
}


# ---------------------------------------------------------------------------
# EMAIL BODIES
# ---------------------------------------------------------------------------

BASE_STYLES = """
    body { font-family: Georgia, serif; line-height: 1.6; color: #222;
           max-width: 600px; margin: 0 auto; padding: 40px 20px; background: #fff; }
    h1 { font-size: 22px; color: #000; font-weight: normal; margin-top: 0; }
    .heartbeat-link { display: inline-block; color: #000 !important;
                      text-decoration: underline; font-weight: bold; margin: 20px 0; }
    .footer { font-size: 11px; color: #999; margin-top: 60px;
              border-top: 1px solid #eee; padding-top: 20px; }
    .warning-box { border: 1px dashed #ff4444; padding: 20px; margin: 20px 0; }
    .shard-box { background: #fefefe; border: 1px dashed #ccc; padding: 25px;
                 margin: 30px 0; font-family: monospace; font-size: 13px;
                 word-break: break-all; color: #222; }
    .instructions { background: #fff; border: 1px solid #eee; padding: 20px;
                    border-radius: 4px; margin: 30px 0; }
    .cta-box { background: #fafafa; border: 1px solid #ddd; padding: 25px;
               margin-top: 40px; text-align: center; }
    .cta-link { display: inline-block; background: #222; color: #fff !important;
                text-decoration: none; padding: 12px 20px; border-radius: 4px;
                font-weight: bold; margin-top: 15px; }
"""


def _html_wrap(body: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><style>{BASE_STYLES}</style></head>
<body>{body}</body>
</html>"""


# ---------------------------------------------------------------------------
# WELCOME EMAIL
# ---------------------------------------------------------------------------

def get_welcome_email(lang: str, email: str, beneficiary_email: str, heartbeat_link: str) -> str:
    bodies = {
        "en": f"""
            <h1>it's not just a welcome email.</h1>
            <p>hey,</p>
            <p>you just did something most people never do: you protected your crypto for the people you love.</p>
            <p>your vault is now active. here's what happens next:</p>
            <ul>
                <li>every 30 days, we'll send you a heartbeat link.</li>
                <li>click it. that's it. takes 5 seconds.</li>
                <li>if you miss 90 days in a row, shard c goes to your beneficiary.</li>
            </ul>
            <p><strong>vault active for: {email}</strong><br>
            beneficiary: {beneficiary_email}</p>
            <p>your first heartbeat link: <a href="{heartbeat_link}" class="heartbeat-link">click here to confirm you're alive</a></p>
            <p>if you have any questions, just reply to this email. i read them all.</p>
            <p>with care,<br><strong>max</strong><br><i>(the guy who sends you crayon drawings)</i></p>
            <div class="footer"><p>sent by deadhand - built with care in argentina.</p></div>
        """,
        "es": f"""
            <h1>no es solo un email de bienvenida.</h1>
            <p>hola,</p>
            <p>acabás de hacer algo que la mayoría de la gente nunca hace: protegiste tus cripto para las personas que querés.</p>
            <p>tu vault ya está activo. esto es lo que pasa ahora:</p>
            <ul>
                <li>cada 30 días te enviamos un link de heartbeat.</li>
                <li>hacé clic. eso es todo. tarda 5 segundos.</li>
                <li>si pasás 90 días sin responder, el shard c se envía a tu beneficiario.</li>
            </ul>
            <p><strong>vault activo para: {email}</strong><br>
            beneficiario: {beneficiary_email}</p>
            <p>tu primer link de heartbeat: <a href="{heartbeat_link}" class="heartbeat-link">hacé clic para confirmar que estás vivo</a></p>
            <p>si tenés alguna pregunta, respondé este email. los leo todos.</p>
            <p>con cuidado,<br><strong>max</strong><br><i>(el que te manda los dibujos con crayones)</i></p>
            <div class="footer"><p>enviado por deadhand - hecho con cuidado en argentina.</p></div>
        """,
        "pt": f"""
            <h1>não é só um e-mail de boas-vindas.</h1>
            <p>olá,</p>
            <p>você acabou de fazer algo que a maioria das pessoas nunca faz: protegeu suas criptos para as pessoas que ama.</p>
            <p>seu vault já está ativo. veja o que acontece agora:</p>
            <ul>
                <li>a cada 30 dias, vamos te enviar um link de heartbeat.</li>
                <li>clique nele. só isso. leva 5 segundos.</li>
                <li>se você ficar 90 dias sem responder, o shard c vai para seu beneficiário.</li>
            </ul>
            <p><strong>vault ativo para: {email}</strong><br>
            beneficiário: {beneficiary_email}</p>
            <p>seu primeiro link: <a href="{heartbeat_link}" class="heartbeat-link">clique aqui para confirmar que está vivo</a></p>
            <p>se tiver dúvidas, responda este e-mail. eu leio todos.</p>
            <p>com cuidado,<br><strong>max</strong></p>
            <div class="footer"><p>enviado pelo deadhand - feito com carinho na argentina.</p></div>
        """,
        "de": f"""
            <h1>das ist nicht nur eine Willkommens-E-Mail.</h1>
            <p>hey,</p>
            <p>du hast gerade etwas getan, das die meisten Menschen nie tun: du hast deine Krypto für deine Lieben gesichert.</p>
            <p>dein Vault ist jetzt aktiv. so geht es weiter:</p>
            <ul>
                <li>alle 30 Tage senden wir dir einen Heartbeat-Link.</li>
                <li>klick drauf. das ist alles. dauert 5 Sekunden.</li>
                <li>wenn du 90 Tage nicht antwortest, wird Shard C an deinen Begünstigten gesendet.</li>
            </ul>
            <p><strong>vault aktiv für: {email}</strong><br>
            begünstigte(r): {beneficiary_email}</p>
            <p>dein erster Heartbeat-Link: <a href="{heartbeat_link}" class="heartbeat-link">hier klicken um zu bestätigen, dass du am Leben bist</a></p>
            <p>bei Fragen einfach auf diese E-Mail antworten.</p>
            <p>mit Sorgfalt,<br><strong>max</strong></p>
            <div class="footer"><p>gesendet von deadhand - mit Sorgfalt in Argentinien gebaut.</p></div>
        """,
        "fr": f"""
            <h1>ce n'est pas juste un e-mail de bienvenue.</h1>
            <p>bonjour,</p>
            <p>vous venez de faire quelque chose que la plupart des gens ne font jamais : protéger vos cryptos pour les personnes que vous aimez.</p>
            <p>votre vault est maintenant actif. voici ce qui se passe :</p>
            <ul>
                <li>tous les 30 jours, nous vous envoyons un lien heartbeat.</li>
                <li>cliquez dessus. c'est tout. ça prend 5 secondes.</li>
                <li>si vous ne répondez pas pendant 90 jours, le shard c est envoyé à votre bénéficiaire.</li>
            </ul>
            <p><strong>vault actif pour : {email}</strong><br>
            bénéficiaire : {beneficiary_email}</p>
            <p>votre premier lien heartbeat : <a href="{heartbeat_link}" class="heartbeat-link">cliquez ici pour confirmer que vous êtes en vie</a></p>
            <p>pour toute question, répondez à cet e-mail. je les lis tous.</p>
            <p>avec soin,<br><strong>max</strong></p>
            <div class="footer"><p>envoyé par deadhand - fait avec soin en argentine.</p></div>
        """,
        "ja": f"""
            <h1>これはただの歓迎メールではありません。</h1>
            <p>こんにちは、</p>
            <p>あなたは多くの人がしないことをしました：愛する人のために暗号資産を守ったのです。</p>
            <p>vaultが有効になりました。これからの流れ：</p>
            <ul>
                <li>30日ごとにハートビートリンクをお送りします。</li>
                <li>クリックするだけ。5秒で完了します。</li>
                <li>90日間応答がない場合、shard cが受取人に送られます。</li>
            </ul>
            <p><strong>vault有効：{email}</strong><br>
            受取人：{beneficiary_email}</p>
            <p>最初のハートビートリンク：<a href="{heartbeat_link}" class="heartbeat-link">生存確認のためここをクリック</a></p>
            <p>ご質問はこのメールに返信してください。すべて読んでいます。</p>
            <p>大切に、<br><strong>max</strong></p>
            <div class="footer"><p>deadhandより - アルゼンチンで心を込めて作られました。</p></div>
        """,
    }
    return _html_wrap(bodies.get(lang, bodies["en"]))


# ---------------------------------------------------------------------------
# CANCELLATION EMAIL
# ---------------------------------------------------------------------------

def get_cancellation_email(lang: str) -> str:
    bodies = {
        "en": """
            <p>hey,</p>
            <p>your deadhand vault has been deactivated. your data has been deleted.</p>
            <p>i'm not going to send you a survey or a discount code. i just want to say thanks for trusting deadhand for a while.</p>
            <p>if you ever change your mind, the door is open.</p>
            <p>take care,<br><strong>max</strong></p>
            <div class="footer"><p>sent by deadhand - built with care in argentina.</p></div>
        """,
        "es": """
            <p>hola,</p>
            <p>tu vault de deadhand fue desactivado. tus datos fueron eliminados.</p>
            <p>no te voy a mandar una encuesta ni un cupón de descuento. solo quiero decirte gracias por haber confiado en deadhand.</p>
            <p>si algún día cambiás de opinión, la puerta está abierta.</p>
            <p>cuidate,<br><strong>max</strong></p>
            <div class="footer"><p>enviado por deadhand - hecho con cuidado en argentina.</p></div>
        """,
        "pt": """
            <p>olá,</p>
            <p>seu vault do deadhand foi desativado. seus dados foram deletados.</p>
            <p>não vou te mandar pesquisa nem cupom de desconto. só quero dizer obrigado por ter confiado no deadhand.</p>
            <p>se mudar de ideia, a porta está aberta.</p>
            <p>cuide-se,<br><strong>max</strong></p>
            <div class="footer"><p>enviado pelo deadhand - feito com carinho na argentina.</p></div>
        """,
        "de": """
            <p>hey,</p>
            <p>dein deadhand-Vault wurde deaktiviert. deine Daten wurden gelöscht.</p>
            <p>ich werde dir keine Umfrage oder einen Rabattcode schicken. ich möchte nur danke sagen, dass du deadhand vertraut hast.</p>
            <p>wenn du deine Meinung änderst, ist die Tür offen.</p>
            <p>pass auf dich auf,<br><strong>max</strong></p>
            <div class="footer"><p>gesendet von deadhand - mit Sorgfalt in Argentinien gebaut.</p></div>
        """,
        "fr": """
            <p>bonjour,</p>
            <p>votre vault deadhand a été désactivé. vos données ont été supprimées.</p>
            <p>je ne vais pas vous envoyer un sondage ou un code de réduction. je veux juste vous remercier d'avoir fait confiance à deadhand.</p>
            <p>si vous changez d'avis, la porte est ouverte.</p>
            <p>prenez soin de vous,<br><strong>max</strong></p>
            <div class="footer"><p>envoyé par deadhand - fait avec soin en argentine.</p></div>
        """,
        "ja": """
            <p>こんにちは、</p>
            <p>deadhandのvaultが無効化されました。データは削除されました。</p>
            <p>アンケートや割引コードは送りません。deadhandを信頼してくれたことへの感謝だけ伝えたいです。</p>
            <p>気が変わったら、いつでもどうぞ。</p>
            <p>お気をつけて、<br><strong>max</strong></p>
            <div class="footer"><p>deadhandより - アルゼンチンで心を込めて作られました。</p></div>
        """,
    }
    return _html_wrap(bodies.get(lang, bodies["en"]))


# ---------------------------------------------------------------------------
# 30-DAY REMINDER EMAIL
# ---------------------------------------------------------------------------

def get_reminder_30d_email(lang: str, heartbeat_link: str) -> str:
    bodies = {
        "en": f"""
            <p>hey,</p>
            <p>just a quick check-in. your 30-day heartbeat timer is almost up.</p>
            <p>click the link below to reset it — takes 5 seconds:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">i'm here, reset the timer</a>
            <p>if you don't click it, no big deal for now. i'll check in again in another 30 days. but after 90 days of silence, we'll have to send shard c to your beneficiary.</p>
            <p>stay safe,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>sent by deadhand - built with care in argentina.</p></div>
        """,
        "es": f"""
            <p>hola,</p>
            <p>solo un aviso rápido. tu timer de heartbeat de 30 días está por vencer.</p>
            <p>hacé clic en el link para resetearlo — tarda 5 segundos:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">estoy aquí, resetear el timer</a>
            <p>si no hacés clic, por ahora no pasa nada. te vuelvo a escribir en 30 días. pero después de 90 días de silencio, vamos a tener que enviar el shard c a tu beneficiario.</p>
            <p>cuidate,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>enviado por deadhand - hecho con cuidado en argentina.</p></div>
        """,
        "pt": f"""
            <p>olá,</p>
            <p>só um lembrete rápido. seu timer de heartbeat de 30 dias está quase vencendo.</p>
            <p>clique no link abaixo para resetá-lo — leva 5 segundos:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">estou aqui, resetar o timer</a>
            <p>se não clicar, não tem problema por enquanto. vou te escrever novamente em 30 dias. mas após 90 dias de silêncio, precisaremos enviar o shard c para seu beneficiário.</p>
            <p>cuide-se,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>enviado pelo deadhand - feito com carinho na argentina.</p></div>
        """,
        "de": f"""
            <p>hey,</p>
            <p>kurze Erinnerung. dein 30-Tage-Heartbeat-Timer läuft bald ab.</p>
            <p>klick den Link unten, um ihn zurückzusetzen — dauert 5 Sekunden:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">ich bin hier, Timer zurücksetzen</a>
            <p>wenn du nicht klickst, ist das erstmal kein Problem. ich melde mich in 30 Tagen wieder. aber nach 90 Tagen ohne Signal müssen wir Shard C an deinen Begünstigten senden.</p>
            <p>bleib gesund,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>gesendet von deadhand - mit Sorgfalt in Argentinien gebaut.</p></div>
        """,
        "fr": f"""
            <p>bonjour,</p>
            <p>juste un petit rappel. votre timer heartbeat de 30 jours arrive bientôt à expiration.</p>
            <p>cliquez sur le lien ci-dessous pour le réinitialiser — 5 secondes suffisent :</p>
            <a href="{heartbeat_link}" class="heartbeat-link">je suis là, réinitialiser le timer</a>
            <p>si vous ne cliquez pas, pas de panique pour l'instant. je vous recontacterai dans 30 jours. mais après 90 jours de silence, nous devrons envoyer le shard c à votre bénéficiaire.</p>
            <p>prenez soin de vous,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>envoyé par deadhand - fait avec soin en argentine.</p></div>
        """,
        "ja": f"""
            <p>こんにちは、</p>
            <p>簡単なお知らせです。30日間のハートビートタイマーがもうすぐ切れます。</p>
            <p>下のリンクをクリックしてリセットしてください — 5秒で完了します：</p>
            <a href="{heartbeat_link}" class="heartbeat-link">ここにいます、タイマーをリセット</a>
            <p>クリックしなくても今はまだ大丈夫です。30日後に再度連絡します。ただし90日間応答がない場合、shard cを受取人に送る必要があります。</p>
            <p>お気をつけて、<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>deadhandより - アルゼンチンで心を込めて作られました。</p></div>
        """,
    }
    return _html_wrap(bodies.get(lang, bodies["en"]))


# ---------------------------------------------------------------------------
# 60-DAY WARNING EMAIL
# ---------------------------------------------------------------------------

def get_warning_60d_email(lang: str, heartbeat_link: str) -> str:
    bodies = {
        "en": f"""
            <p>hey,</p>
            <p>i'm getting a little worried. we haven't heard from you in 60 days.</p>
            <div class="warning-box">
                <p><strong>just 30 days left.</strong></p>
                <p>if you don't click the link below within the next month, our system will assume the worst and automatically send shard c to your beneficiary.</p>
            </div>
            <p>if you're just busy, i totally get it. but please, click this now:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">i'm here, reset the timer</a>
            <p>talk soon,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>sent by deadhand - protecting your crypto legacy.</p></div>
        """,
        "es": f"""
            <p>hola,</p>
            <p>estoy un poco preocupado. no sabemos nada de vos hace 60 días.</p>
            <div class="warning-box">
                <p><strong>solo quedan 30 días.</strong></p>
                <p>si no hacés clic en el link en el próximo mes, el sistema va a asumir lo peor y enviará automáticamente el shard c a tu beneficiario.</p>
            </div>
            <p>si estás ocupado, lo entiendo. pero por favor, hacé clic ahora:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">estoy aquí, resetear el timer</a>
            <p>hasta pronto,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>enviado por deadhand - protegiendo tu legado cripto.</p></div>
        """,
        "pt": f"""
            <p>olá,</p>
            <p>estou um pouco preocupado. não temos notícias suas há 60 dias.</p>
            <div class="warning-box">
                <p><strong>só faltam 30 dias.</strong></p>
                <p>se não clicar no link abaixo dentro de um mês, o sistema vai assumir o pior e enviar automaticamente o shard c para seu beneficiário.</p>
            </div>
            <p>se estiver ocupado, entendo. mas por favor, clique agora:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">estou aqui, resetar o timer</a>
            <p>até logo,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>enviado pelo deadhand - protegendo seu legado cripto.</p></div>
        """,
        "de": f"""
            <p>hey,</p>
            <p>ich mache mir ein wenig Sorgen. wir haben seit 60 Tagen nichts von dir gehört.</p>
            <div class="warning-box">
                <p><strong>nur noch 30 Tage.</strong></p>
                <p>wenn du den Link unten nicht innerhalb des nächsten Monats klickst, nimmt unser System das Schlimmste an und sendet Shard C automatisch an deinen Begünstigten.</p>
            </div>
            <p>wenn du nur beschäftigt bist, verstehe ich das. aber bitte, klick jetzt:</p>
            <a href="{heartbeat_link}" class="heartbeat-link">ich bin hier, Timer zurücksetzen</a>
            <p>bis bald,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>gesendet von deadhand - dein Krypto-Erbe schützen.</p></div>
        """,
        "fr": f"""
            <p>bonjour,</p>
            <p>je commence à m'inquiéter. nous n'avons pas de nouvelles depuis 60 jours.</p>
            <div class="warning-box">
                <p><strong>plus que 30 jours.</strong></p>
                <p>si vous ne cliquez pas sur le lien ci-dessous dans le mois qui vient, notre système supposera le pire et enverra automatiquement le shard c à votre bénéficiaire.</p>
            </div>
            <p>si vous êtes simplement occupé, je comprends tout à fait. mais s'il vous plaît, cliquez maintenant :</p>
            <a href="{heartbeat_link}" class="heartbeat-link">je suis là, réinitialiser le timer</a>
            <p>à bientôt,<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>envoyé par deadhand - protéger votre héritage crypto.</p></div>
        """,
        "ja": f"""
            <p>こんにちは、</p>
            <p>少し心配しています。60日間連絡がありません。</p>
            <div class="warning-box">
                <p><strong>残り30日です。</strong></p>
                <p>来月中にリンクをクリックしない場合、システムは最悪の事態を想定し、shard cを受取人に自動送信します。</p>
            </div>
            <p>お忙しいのは理解できます。でも今すぐクリックしてください：</p>
            <a href="{heartbeat_link}" class="heartbeat-link">ここにいます、タイマーをリセット</a>
            <p>またお話しましょう、<br><strong>deadhand protocol</strong></p>
            <div class="footer"><p>deadhandより - あなたの暗号資産の遺産を守ります。</p></div>
        """,
    }
    return _html_wrap(bodies.get(lang, bodies["en"]))


# ---------------------------------------------------------------------------
# DEATH EMAIL (to beneficiary)
# ---------------------------------------------------------------------------

def get_death_email(lang: str, owner_email: str, shard_c_value: str) -> str:
    bodies = {
        "en": f"""
            <h1>a message from Deadhand.</h1>
            <p>hello,</p>
            <p>i'm writing to you because 90 days ago, <strong>{owner_email}</strong> entrusted our system to reach out to you if we stopped hearing from them.</p>
            <p>we haven't received a heartbeat check-in from them in three months. as per their explicit instructions, i am now releasing the final piece of their digital legacy to you.</p>
            <p>this is <strong>shard c</strong>. it's one of three pieces needed to access their crypto assets. you should already have <strong>shard b</strong> (a document they gave you).</p>
            <div class="shard-box"><strong>shard c value:</strong><br>{shard_c_value}</div>
            <div class="instructions">
                <p><strong>how to use this:</strong></p>
                <ol>
                    <li>locate <strong>shard b</strong> (the one they gave you).</li>
                    <li>go to <a href="https://deadhandprotocol.com/recover">deadhandprotocol.com/recover</a>.</li>
                    <li>enter both shard b and shard c into the tool.</li>
                    <li>the tool will reconstruct their original seed phrase.</li>
                </ol>
            </div>
            <p>my deepest condolences. i built Deadhand so families wouldn't be locked out of their loved ones' assets during difficult times.</p>
            <p>with respect,<br><strong>deadhand protocol</strong></p>
            <div class="cta-box">
                <p><strong>protect your own legacy</strong></p>
                <p style="font-size:13px;color:#666;">you've just seen how Deadhand works. set up your own trustless switch in 5 minutes.</p>
                <a href="https://deadhandprotocol.com" class="cta-link">create your vault</a>
            </div>
            <div class="footer"><p>sent by deadhand - built with care in argentina.</p></div>
        """,
        "es": f"""
            <h1>un mensaje de Deadhand.</h1>
            <p>hola,</p>
            <p>te escribo porque hace 90 días, <strong>{owner_email}</strong> le encargó a nuestro sistema que te contactara si dejábamos de tener noticias de esa persona.</p>
            <p>no hemos recibido ningún heartbeat en tres meses. según sus instrucciones explícitas, te entrego ahora la última pieza de su legado digital.</p>
            <p>esto es el <strong>shard c</strong>. es una de las tres piezas necesarias para acceder a sus criptoactivos. ya deberías tener el <strong>shard b</strong> (un documento que te entregaron).</p>
            <div class="shard-box"><strong>valor del shard c:</strong><br>{shard_c_value}</div>
            <div class="instructions">
                <p><strong>cómo usarlo:</strong></p>
                <ol>
                    <li>encontrá el <strong>shard b</strong> (el que te dieron).</li>
                    <li>entrá a <a href="https://deadhandprotocol.com/recover">deadhandprotocol.com/recover</a>.</li>
                    <li>ingresá el shard b y el shard c en la herramienta.</li>
                    <li>la herramienta reconstruirá la seed phrase original.</li>
                </ol>
            </div>
            <p>mis más sinceras condolencias. construí Deadhand para que las familias no quedaran sin acceso a los activos de sus seres queridos en momentos difíciles.</p>
            <p>con respeto,<br><strong>deadhand protocol</strong></p>
            <div class="cta-box">
                <p><strong>protegé tu propio legado</strong></p>
                <p style="font-size:13px;color:#666;">acabás de ver cómo funciona Deadhand. configurá tu propio switch en 5 minutos.</p>
                <a href="https://deadhandprotocol.com" class="cta-link">crear tu vault</a>
            </div>
            <div class="footer"><p>enviado por deadhand - hecho con cuidado en argentina.</p></div>
        """,
        "pt": f"""
            <h1>uma mensagem do Deadhand.</h1>
            <p>olá,</p>
            <p>estou escrevendo porque há 90 dias, <strong>{owner_email}</strong> confiou ao nosso sistema que entrasse em contato com você se parássemos de receber notícias dela.</p>
            <p>não recebemos nenhum heartbeat em três meses. conforme suas instruções explícitas, estou liberando agora a peça final de seu legado digital para você.</p>
            <p>este é o <strong>shard c</strong>. é uma das três peças necessárias para acessar seus criptoativos. você já deve ter o <strong>shard b</strong> (um documento que te foi entregue).</p>
            <div class="shard-box"><strong>valor do shard c:</strong><br>{shard_c_value}</div>
            <div class="instructions">
                <p><strong>como usar:</strong></p>
                <ol>
                    <li>localize o <strong>shard b</strong> (o que te foi dado).</li>
                    <li>acesse <a href="https://deadhandprotocol.com/recover">deadhandprotocol.com/recover</a>.</li>
                    <li>insira o shard b e o shard c na ferramenta.</li>
                    <li>a ferramenta vai reconstruir a seed phrase original.</li>
                </ol>
            </div>
            <p>meus sinceros pêsames. construí o Deadhand para que as famílias não ficassem sem acesso aos ativos de seus entes queridos em momentos difíceis.</p>
            <p>com respeito,<br><strong>deadhand protocol</strong></p>
            <div class="cta-box">
                <p><strong>proteja seu próprio legado</strong></p>
                <p style="font-size:13px;color:#666;">você acabou de ver como o Deadhand funciona. configure seu próprio switch em 5 minutos.</p>
                <a href="https://deadhandprotocol.com" class="cta-link">criar seu vault</a>
            </div>
            <div class="footer"><p>enviado pelo deadhand - feito com carinho na argentina.</p></div>
        """,
        "de": f"""
            <h1>eine Nachricht von Deadhand.</h1>
            <p>hallo,</p>
            <p>ich schreibe dir, weil <strong>{owner_email}</strong> vor 90 Tagen unserem System die Aufgabe übertragen hat, dich zu kontaktieren, falls wir nichts mehr von ihr/ihm hören.</p>
            <p>wir haben seit drei Monaten keinen Heartbeat erhalten. gemäß ihren/seinen ausdrücklichen Anweisungen übergebe ich dir jetzt das letzte Stück ihres/seines digitalen Erbes.</p>
            <p>das ist <strong>Shard C</strong>. es ist eines von drei Teilen, die benötigt werden, um auf ihre/seine Krypto-Assets zuzugreifen. du solltest bereits <strong>Shard B</strong> haben (ein Dokument, das sie/er dir übergeben hat).</p>
            <div class="shard-box"><strong>Shard C Wert:</strong><br>{shard_c_value}</div>
            <div class="instructions">
                <p><strong>so verwendest du es:</strong></p>
                <ol>
                    <li>finde <strong>Shard B</strong> (den sie/er dir gegeben hat).</li>
                    <li>gehe zu <a href="https://deadhandprotocol.com/recover">deadhandprotocol.com/recover</a>.</li>
                    <li>gib Shard B und Shard C in das Tool ein.</li>
                    <li>das Tool rekonstruiert die ursprüngliche Seed-Phrase.</li>
                </ol>
            </div>
            <p>mein aufrichtiges Beileid. ich habe Deadhand gebaut, damit Familien nicht vom Zugang zu den Assets ihrer Lieben ausgeschlossen werden.</p>
            <p>mit Respekt,<br><strong>deadhand protocol</strong></p>
            <div class="cta-box">
                <p><strong>schütze dein eigenes Erbe</strong></p>
                <p style="font-size:13px;color:#666;">du hast gerade gesehen, wie Deadhand funktioniert. richte deinen eigenen Switch in 5 Minuten ein.</p>
                <a href="https://deadhandprotocol.com" class="cta-link">vault erstellen</a>
            </div>
            <div class="footer"><p>gesendet von deadhand - mit Sorgfalt in Argentinien gebaut.</p></div>
        """,
        "fr": f"""
            <h1>un message de Deadhand.</h1>
            <p>bonjour,</p>
            <p>je vous écris parce qu'il y a 90 jours, <strong>{owner_email}</strong> a confié à notre système de vous contacter si nous n'avions plus de nouvelles.</p>
            <p>nous n'avons reçu aucun heartbeat depuis trois mois. conformément à ses instructions explicites, je vous remets maintenant la dernière pièce de son héritage numérique.</p>
            <p>voici le <strong>shard c</strong>. c'est l'une des trois pièces nécessaires pour accéder à ses actifs crypto. vous devriez déjà avoir le <strong>shard b</strong> (un document qu'il/elle vous a remis).</p>
            <div class="shard-box"><strong>valeur du shard c :</strong><br>{shard_c_value}</div>
            <div class="instructions">
                <p><strong>comment l'utiliser :</strong></p>
                <ol>
                    <li>localisez le <strong>shard b</strong> (celui qu'on vous a donné).</li>
                    <li>rendez-vous sur <a href="https://deadhandprotocol.com/recover">deadhandprotocol.com/recover</a>.</li>
                    <li>entrez le shard b et le shard c dans l'outil.</li>
                    <li>l'outil reconstruira la phrase seed originale.</li>
                </ol>
            </div>
            <p>mes plus sincères condoléances. j'ai créé Deadhand pour que les familles ne soient pas exclues des actifs de leurs proches en période difficile.</p>
            <p>avec respect,<br><strong>deadhand protocol</strong></p>
            <div class="cta-box">
                <p><strong>protégez votre propre héritage</strong></p>
                <p style="font-size:13px;color:#666;">vous venez de voir comment Deadhand fonctionne. configurez votre propre switch en 5 minutes.</p>
                <a href="https://deadhandprotocol.com" class="cta-link">créer votre vault</a>
            </div>
            <div class="footer"><p>envoyé par deadhand - fait avec soin en argentine.</p></div>
        """,
        "ja": f"""
            <h1>Deadhandからのメッセージ。</h1>
            <p>こんにちは、</p>
            <p>90日前、<strong>{owner_email}</strong>が連絡を絶った場合にあなたへ連絡するよう、私たちのシステムに委託していました。</p>
            <p>3ヶ月間ハートビートを受信していません。明示的な指示に従い、デジタル遺産の最後のピースをあなたにお渡しします。</p>
            <p>これは<strong>shard c</strong>です。暗号資産にアクセスするために必要な3つのピースのうちの1つです。すでに<strong>shard b</strong>（渡されたドキュメント）をお持ちのはずです。</p>
            <div class="shard-box"><strong>shard cの値：</strong><br>{shard_c_value}</div>
            <div class="instructions">
                <p><strong>使い方：</strong></p>
                <ol>
                    <li><strong>shard b</strong>（渡されたもの）を見つけてください。</li>
                    <li><a href="https://deadhandprotocol.com/recover">deadhandprotocol.com/recover</a>にアクセスしてください。</li>
                    <li>ツールにshard bとshard cを入力してください。</li>
                    <li>ツールが元のシードフレーズを復元します。</li>
                </ol>
            </div>
            <p>心よりお悔やみ申し上げます。困難な時期に大切な人の資産にアクセスできなくならないよう、Deadhandを作りました。</p>
            <p>敬意を込めて、<br><strong>deadhand protocol</strong></p>
            <div class="cta-box">
                <p><strong>自分のレガシーを守る</strong></p>
                <p style="font-size:13px;color:#666;">Deadhandの仕組みを見ていただきました。5分で自分のスイッチを設定できます。</p>
                <a href="https://deadhandprotocol.com" class="cta-link">vaultを作成する</a>
            </div>
            <div class="footer"><p>deadhandより - アルゼンチンで心を込めて作られました。</p></div>
        """,
    }
    return _html_wrap(bodies.get(lang, bodies["en"]))
// Deadhand Internationalization (i18n)
const translations = {
    en: {
        // Nav
        nav_pricing: "Pricing",
        nav_docs: "Docs",
        nav_launch: "Launch App",

        // Hero
        hero_badge: "SHAMIR'S SECRET SHARING // 2-OF-3 THRESHOLD",
        hero_title_1: "Crypto Inheritance",
        hero_title_2: "Without Trust",
        hero_subtitle: "Split your seed phrase into three shards. Any two can recover it. Your beneficiary gets the third shard only when you stop responding.",
        hero_cta: "Create Vault",
        hero_cta_2: "View Protocol",

        // Specs
        spec_encryption: "ENCRYPTION",
        spec_encryption_val: "Client-Side Only",
        spec_threshold: "THRESHOLD",
        spec_threshold_val: "2-of-3 Shards",
        spec_trigger: "TRIGGER",
        spec_trigger_val: "90-Day Inactivity",
        spec_trust: "TRUST",
        spec_trust_val: "Zero Knowledge",

        // Problem
        problem_label: "// THE PROBLEM",
        problem_title: "$140B in Crypto Will Die With Its Owners",
        problem_subtitle: "Self-custody solves the trust problem. But it creates a new one: when you die, your keys die with you.",
        problem_stat_1: "4M+",
        problem_stat_1_desc: "Bitcoin lost forever",
        problem_stat_2: "23%",
        problem_stat_2_desc: "Of holders have no inheritance plan",
        problem_stat_3: "$0",
        problem_stat_3_desc: "Value of crypto without the key",

        // Solution
        solution_label: "// THE SOLUTION",
        solution_title: "The Deadhand Solution",
        solution_subtitle: "Split your seed phrase into 3 shards. Any 2 can recover it. No single party can steal it.",
        shard_a: "Shard A",
        shard_a_desc: "You keep this. Store in a safe or password manager.",
        shard_b: "Shard B",
        shard_b_desc: "Give to your beneficiary. Print it as PDF.",
        shard_c: "Shard C",
        shard_c_desc: "Held by Deadhand. Released when switch triggers.",

        // Protocol
        protocol_label: "// PROTOCOL",
        protocol_title: "How It Works",
        protocol_subtitle: "Mathematically secure. No single point of failure. No custodian risk.",
        step_1_title: "Split Locally",
        step_1_desc: "Your seed phrase is split into 3 shards using Shamir's Secret Sharing. This happens entirely in your browser. We never see the original.",
        step_2_title: "Distribute Shards",
        step_2_desc: "Shard A: You keep. Shard B: Give to beneficiary. Shard C: We store encrypted. Any 2 shards reconstruct the original.",
        step_3_title: "Dead Man's Switch",
        step_3_desc: "We ping you every 30 days. After 90 days of silence, Shard C is automatically sent to your beneficiary.",

        // Security
        security_label: "// SECURITY MODEL",
        security_title: "Zero Trust Architecture",
        security_subtitle: "Even if we're compromised, attackers get nothing useful.",

        // FAQ
        faq_label: "// FAQ",
        faq_title: "Frequently Asked Questions",
        faq_subtitle: "Everything you need to know about Deadhand.",

        // CTA
        cta_title: "Don't Let Your Crypto Die With You",
        cta_subtitle: "Set up your vault in under 5 minutes. Your seed phrase never leaves your device.",
        cta_button: "Create Your Vault",
        cta_note: "No credit card. No account required.",

        // Footer
        footer_opensource: "Source-Available · BSL 1.1"
    },

    es: {
        nav_pricing: "Precios",
        nav_docs: "Docs",
        nav_launch: "Abrir App",
        hero_badge: "SHAMIR'S SECRET SHARING // UMBRAL 2-DE-3",
        hero_title_1: "Herencia Cripto",
        hero_title_2: "Sin Confianza",
        hero_subtitle: "Divide tu frase semilla en tres fragmentos. Cualquier dos pueden recuperarla. Tu beneficiario recibe el tercer fragmento solo cuando dejas de responder.",
        hero_cta: "Crear Bóveda",
        hero_cta_2: "Ver Protocolo",
        spec_encryption: "ENCRIPTACIÓN",
        spec_encryption_val: "Solo Cliente",
        spec_threshold: "UMBRAL",
        spec_threshold_val: "2-de-3 Fragmentos",
        spec_trigger: "ACTIVADOR",
        spec_trigger_val: "90 Días Inactivo",
        spec_trust: "CONFIANZA",
        spec_trust_val: "Cero Conocimiento",
        problem_label: "// EL PROBLEMA",
        problem_title: "$140B en Cripto Morirán Con Sus Dueños",
        problem_subtitle: "La auto-custodia resuelve el problema de confianza. Pero crea uno nuevo: cuando mueres, tus claves mueren contigo.",
        problem_stat_1: "4M+",
        problem_stat_1_desc: "Bitcoin perdidos para siempre",
        problem_stat_2: "23%",
        problem_stat_2_desc: "De holders sin plan de herencia",
        problem_stat_3: "$0",
        problem_stat_3_desc: "Valor del cripto sin la clave",
        solution_label: "// LA SOLUCIÓN",
        solution_title: "La Solución Deadhand",
        solution_subtitle: "Divide tu frase semilla en 3 fragmentos. Cualquier 2 pueden recuperarla. Nadie puede robarla solo.",
        shard_a: "Fragmento A",
        shard_a_desc: "Tú lo guardas. Almacena en caja fuerte o gestor de contraseñas.",
        shard_b: "Fragmento B",
        shard_b_desc: "Dáselo a tu beneficiario. Imprímelo como PDF.",
        shard_c: "Fragmento C",
        shard_c_desc: "Lo guarda Deadhand. Se libera cuando se activa el switch.",
        protocol_label: "// PROTOCOLO",
        protocol_title: "Cómo Funciona",
        protocol_subtitle: "Matemáticamente seguro. Sin punto único de falla. Sin riesgo de custodia.",
        step_1_title: "Divide Localmente",
        step_1_desc: "Tu frase semilla se divide en 3 fragmentos usando Shamir's Secret Sharing. Esto sucede en tu navegador. Nunca vemos el original.",
        step_2_title: "Distribuye Fragmentos",
        step_2_desc: "Fragmento A: Tú guardas. Fragmento B: Para beneficiario. Fragmento C: Nosotros guardamos encriptado.",
        step_3_title: "Dead Man's Switch",
        step_3_desc: "Te contactamos cada 30 días. Después de 90 días sin respuesta, el Fragmento C se envía automáticamente a tu beneficiario.",
        security_label: "// MODELO DE SEGURIDAD",
        security_title: "Arquitectura Cero Confianza",
        security_subtitle: "Incluso si nos hackean, los atacantes no obtienen nada útil.",
        faq_label: "// FAQ",
        faq_title: "Preguntas Frecuentes",
        faq_subtitle: "Todo lo que necesitas saber sobre Deadhand.",
        cta_title: "No Dejes Que Tu Cripto Muera Contigo",
        cta_subtitle: "Configura tu bóveda en menos de 5 minutos. Tu frase semilla nunca sale de tu dispositivo.",
        cta_button: "Crear Tu Bóveda",
        cta_note: "Sin tarjeta de crédito. Sin cuenta requerida.",
        footer_opensource: "Código Disponible · BSL 1.1"
    },

    zh: {
        nav_pricing: "价格",
        nav_docs: "文档",
        nav_launch: "启动应用",
        hero_badge: "沙米尔秘密共享 // 2-OF-3 阈值",
        hero_title_1: "加密货币继承",
        hero_title_2: "无需信任",
        hero_subtitle: "将您的助记词分成三个碎片。任意两个可以恢复。只有当您停止响应时，您的受益人才会获得第三个碎片。",
        hero_cta: "创建保险库",
        hero_cta_2: "查看协议",
        spec_encryption: "加密",
        spec_encryption_val: "仅客户端",
        spec_threshold: "阈值",
        spec_threshold_val: "2-of-3 碎片",
        spec_trigger: "触发器",
        spec_trigger_val: "90天不活动",
        spec_trust: "信任",
        spec_trust_val: "零知识",
        problem_label: "// 问题",
        problem_title: "140亿美元加密货币将与其所有者一起消亡",
        problem_subtitle: "自托管解决了信任问题。但它创造了一个新问题：当你死亡时，你的密钥也随之消亡。",
        problem_stat_1: "400万+",
        problem_stat_1_desc: "比特币永远丢失",
        problem_stat_2: "23%",
        problem_stat_2_desc: "持有者没有继承计划",
        problem_stat_3: "$0",
        problem_stat_3_desc: "没有密钥的加密货币价值",
        solution_label: "// 解决方案",
        solution_title: "Deadhand 解决方案",
        solution_subtitle: "将您的助记词分成3个碎片。任意2个可以恢复。没有任何一方可以单独窃取。",
        shard_a: "碎片 A",
        shard_a_desc: "您保管。存储在保险箱或密码管理器中。",
        shard_b: "碎片 B",
        shard_b_desc: "交给您的受益人。打印成PDF。",
        shard_c: "碎片 C",
        shard_c_desc: "由Deadhand保管。开关触发时释放。",
        protocol_label: "// 协议",
        protocol_title: "工作原理",
        protocol_subtitle: "数学安全。无单点故障。无托管风险。",
        step_1_title: "本地分割",
        step_1_desc: "您的助记词使用沙米尔秘密共享分成3个碎片。这完全在您的浏览器中进行。我们从未看到原始内容。",
        step_2_title: "分发碎片",
        step_2_desc: "碎片A：您保管。碎片B：给受益人。碎片C：我们加密存储。",
        step_3_title: "死亡开关",
        step_3_desc: "我们每30天联系您一次。90天无响应后，碎片C自动发送给您的受益人。",
        security_label: "// 安全模型",
        security_title: "零信任架构",
        security_subtitle: "即使我们被入侵，攻击者也得不到任何有用的东西。",
        faq_label: "// 常见问题",
        faq_title: "常见问题",
        faq_subtitle: "关于Deadhand您需要知道的一切。",
        cta_title: "不要让您的加密货币与您一起消亡",
        cta_subtitle: "在5分钟内设置您的保险库。您的助记词永不离开您的设备。",
        cta_button: "创建您的保险库",
        cta_note: "无需信用卡。无需账户。",
        footer_opensource: "源码可查 · BSL 1.1"
    },

    ko: {
        nav_pricing: "가격",
        nav_docs: "문서",
        nav_launch: "앱 시작",
        hero_badge: "샤미르 비밀 공유 // 2-OF-3 임계값",
        hero_title_1: "암호화폐 상속",
        hero_title_2: "신뢰 없이",
        hero_subtitle: "시드 문구를 세 개의 조각으로 나눕니다. 어떤 두 개로도 복구할 수 있습니다. 수혜자는 당신이 응답을 멈출 때만 세 번째 조각을 받습니다.",
        hero_cta: "금고 만들기",
        hero_cta_2: "프로토콜 보기",
        spec_encryption: "암호화",
        spec_encryption_val: "클라이언트 측만",
        spec_threshold: "임계값",
        spec_threshold_val: "2-of-3 조각",
        spec_trigger: "트리거",
        spec_trigger_val: "90일 비활성",
        spec_trust: "신뢰",
        spec_trust_val: "제로 지식",
        problem_label: "// 문제",
        problem_title: "1400억 달러의 암호화폐가 소유자와 함께 사라질 것입니다",
        problem_subtitle: "셀프 커스터디는 신뢰 문제를 해결합니다. 하지만 새로운 문제를 만듭니다: 당신이 죽으면, 키도 함께 죽습니다.",
        solution_label: "// 해결책",
        solution_title: "Deadhand 솔루션",
        solution_subtitle: "시드 문구를 3개의 조각으로 나눕니다. 어떤 2개로도 복구할 수 있습니다. 어느 한 당사자도 혼자서 훔칠 수 없습니다.",
        cta_title: "암호화폐가 당신과 함께 사라지게 두지 마세요",
        cta_subtitle: "5분 안에 금고를 설정하세요. 시드 문구는 절대 기기를 떠나지 않습니다.",
        cta_button: "금고 만들기",
        cta_note: "신용카드 불필요. 계정 불필요.",
        footer_opensource: "소스 공개 · BSL 1.1"
    },

    de: {
        nav_pricing: "Preise",
        nav_docs: "Docs",
        nav_launch: "App Starten",
        hero_badge: "SHAMIR'S SECRET SHARING // 2-VON-3 SCHWELLE",
        hero_title_1: "Krypto-Vererbung",
        hero_title_2: "Ohne Vertrauen",
        hero_subtitle: "Teilen Sie Ihre Seed-Phrase in drei Teile. Beliebige zwei können sie wiederherstellen. Ihr Begünstigter erhält den dritten Teil nur, wenn Sie nicht mehr antworten.",
        hero_cta: "Tresor Erstellen",
        hero_cta_2: "Protokoll Ansehen",
        spec_encryption: "VERSCHLÜSSELUNG",
        spec_encryption_val: "Nur Client-Seite",
        spec_threshold: "SCHWELLE",
        spec_threshold_val: "2-von-3 Teile",
        spec_trigger: "AUSLÖSER",
        spec_trigger_val: "90 Tage Inaktivität",
        spec_trust: "VERTRAUEN",
        spec_trust_val: "Null Wissen",
        problem_label: "// DAS PROBLEM",
        problem_title: "$140 Mrd. in Krypto werden mit ihren Besitzern sterben",
        problem_subtitle: "Selbstverwahrung löst das Vertrauensproblem. Aber es schafft ein neues: Wenn Sie sterben, sterben Ihre Schlüssel mit Ihnen.",
        solution_label: "// DIE LÖSUNG",
        solution_title: "Die Deadhand Lösung",
        solution_subtitle: "Teilen Sie Ihre Seed-Phrase in 3 Teile. Beliebige 2 können sie wiederherstellen. Keine einzelne Partei kann sie stehlen.",
        cta_title: "Lassen Sie Ihre Krypto nicht mit Ihnen sterben",
        cta_subtitle: "Richten Sie Ihren Tresor in unter 5 Minuten ein. Ihre Seed-Phrase verlässt nie Ihr Gerät.",
        cta_button: "Tresor Erstellen",
        cta_note: "Keine Kreditkarte. Kein Konto erforderlich.",
        footer_opensource: "Quellcode Verfügbar · BSL 1.1"
    },

    ja: {
        nav_pricing: "料金",
        nav_docs: "ドキュメント",
        nav_launch: "アプリを起動",
        hero_badge: "シャミアの秘密分散 // 2-OF-3 閾値",
        hero_title_1: "暗号資産の相続",
        hero_title_2: "信頼不要",
        hero_subtitle: "シードフレーズを3つの断片に分割します。任意の2つで復元できます。受益者は、あなたが応答を停止した場合にのみ3番目の断片を受け取ります。",
        hero_cta: "金庫を作成",
        hero_cta_2: "プロトコルを見る",
        spec_encryption: "暗号化",
        spec_encryption_val: "クライアント側のみ",
        spec_threshold: "閾値",
        spec_threshold_val: "2-of-3 断片",
        spec_trigger: "トリガー",
        spec_trigger_val: "90日間非アクティブ",
        spec_trust: "信頼",
        spec_trust_val: "ゼロ知識",
        problem_label: "// 問題",
        problem_title: "1400億ドルの暗号資産が所有者と共に消える",
        problem_subtitle: "セルフカストディは信頼の問題を解決します。しかし新たな問題を生み出します：あなたが死ぬと、鍵も一緒に死にます。",
        solution_label: "// ソリューション",
        solution_title: "Deadhandソリューション",
        solution_subtitle: "シードフレーズを3つの断片に分割。任意の2つで復元可能。単独では誰も盗めません。",
        cta_title: "暗号資産をあなたと一緒に消えさせないで",
        cta_subtitle: "5分以内に金庫を設定。シードフレーズはデバイスから離れません。",
        cta_button: "金庫を作成",
        cta_note: "クレジットカード不要。アカウント不要。",
        footer_opensource: "ソース公開 · BSL 1.1"
    },

    pt: {
        nav_pricing: "Preços",
        nav_docs: "Docs",
        nav_launch: "Abrir App",
        hero_badge: "SHAMIR'S SECRET SHARING // LIMIAR 2-DE-3",
        hero_title_1: "Herança Cripto",
        hero_title_2: "Sem Confiança",
        hero_subtitle: "Divida sua frase semente em três fragmentos. Quaisquer dois podem recuperá-la. Seu beneficiário recebe o terceiro fragmento apenas quando você para de responder.",
        hero_cta: "Criar Cofre",
        hero_cta_2: "Ver Protocolo",
        spec_encryption: "CRIPTOGRAFIA",
        spec_encryption_val: "Apenas Cliente",
        spec_threshold: "LIMIAR",
        spec_threshold_val: "2-de-3 Fragmentos",
        spec_trigger: "GATILHO",
        spec_trigger_val: "90 Dias Inativo",
        spec_trust: "CONFIANÇA",
        spec_trust_val: "Zero Conhecimento",
        problem_label: "// O PROBLEMA",
        problem_title: "$140B em Cripto Morrerão Com Seus Donos",
        problem_subtitle: "Auto-custódia resolve o problema de confiança. Mas cria um novo: quando você morre, suas chaves morrem com você.",
        solution_label: "// A SOLUÇÃO",
        solution_title: "A Solução Deadhand",
        solution_subtitle: "Divida sua frase semente em 3 fragmentos. Quaisquer 2 podem recuperá-la. Nenhuma parte pode roubá-la sozinha.",
        cta_title: "Não Deixe Sua Cripto Morrer Com Você",
        cta_subtitle: "Configure seu cofre em menos de 5 minutos. Sua frase semente nunca sai do seu dispositivo.",
        cta_button: "Criar Seu Cofre",
        cta_note: "Sem cartão de crédito. Sem conta necessária.",
        footer_opensource: "Código Disponível · BSL 1.1"
    }
};

// Language names for selector
const languageNames = {
    en: { name: "English", flag: "🇺🇸" },
    es: { name: "Español", flag: "🇪🇸" },
    zh: { name: "中文", flag: "🇨🇳" },
    ko: { name: "한국어", flag: "🇰🇷" },
    de: { name: "Deutsch", flag: "🇩🇪" },
    ja: { name: "日本語", flag: "🇯🇵" },
    pt: { name: "Português", flag: "🇧🇷" }
};

// Current language
let currentLang = localStorage.getItem('Deadhand_lang') || 'en';

// Apply translations
function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('Deadhand_lang', lang);

    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });

    // Update language selector button
    const langBtn = document.getElementById('lang-btn');
    if (langBtn) {
        langBtn.innerHTML = `${languageNames[lang].flag} <span class="hidden md:inline">${languageNames[lang].name}</span>`;
    }

    // Close dropdown
    const dropdown = document.getElementById('lang-dropdown');
    if (dropdown) dropdown.classList.add('hidden');
}

// Toggle language dropdown
function toggleLangDropdown() {
    const dropdown = document.getElementById('lang-dropdown');
    dropdown.classList.toggle('hidden');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setLanguage(currentLang);
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const langSelector = document.getElementById('lang-selector');
    const dropdown = document.getElementById('lang-dropdown');
    if (langSelector && dropdown && !langSelector.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

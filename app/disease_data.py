"""
Static knowledge base: crop diseases, symptoms, remedies & farming tips.
Data is in Bangla with English keys so the Flutter app can filter/query easily.
"""

DISEASE_DB: list[dict] = [
    # ─────────────────────────── PADDY / RICE ───────────────────────────
    {
        "id": "paddy_blast",
        "crop": "paddy",
        "crop_bn": "ধান",
        "name": "Blast",
        "name_bn": "ব্লাস্ট রোগ",
        "category": "fungal",
        "affected_parts": ["leaf", "neck", "panicle"],
        "symptoms_bn": (
            "পাতায় ডায়মন্ড বা চোখের মতো বাদামি দাগ দেখা যায়। দাগের কেন্দ্র ধূসর এবং কিনারা বাদামি। "
            "গলা পচে শীষ মরে যায় (নেক ব্লাস্ট)। গাছের বৃদ্ধি থেমে যায়।"
        ),
        "causes_bn": "Pyricularia oryzae ছত্রাক দ্বারা সংক্রমিত। অতিরিক্ত নাইট্রোজেন, ঠান্ডা আবহাওয়া ও ঘন কুয়াশায় বেড়ে ওঠে।",
        "remedies_bn": [
            "ট্রাইসাইক্লাজল (Tricyclazole) ০.০৬% হারে স্প্রে করুন।",
            "ইসপ্রোথায়োলেন (Isoprothiolane) ৪০ EC – ২ মিলি/লিটার পানিতে মিশিয়ে স্প্রে করুন।",
            "কার্বেন্ডাজিম গ্রুপের ছত্রাকনাশক ব্যবহার করুন।",
            "রোগাক্রান্ত গাছ তুলে পুড়িয়ে ফেলুন।",
        ],
        "prevention_bn": [
            "রোগ-প্রতিরোধী জাত ব্যবহার করুন (BRRI dhan28, 29)।",
            "বীজ শোধন করুন – গরম পানিতে (৫৪°C, ১০ মিনিট) ভিজিয়ে রাখুন।",
            "অতিরিক্ত ইউরিয়া সার পরিহার করুন।",
            "জমিতে পানি সংরক্ষণ করুন।",
        ],
        "severity": "high",
        "season": ["kharif", "rabi"],
        "image_hint": "rice_blast_leaf_spots",
    },
    {
        "id": "paddy_blight",
        "crop": "paddy",
        "crop_bn": "ধান",
        "name": "Bacterial Leaf Blight",
        "name_bn": "ব্যাকটেরিয়াল লিফ ব্লাইট (পাতা পোড়া রোগ)",
        "category": "bacterial",
        "affected_parts": ["leaf"],
        "symptoms_bn": (
            "পাতার কিনারা হলুদ হয়ে শুকিয়ে যায়। পরে সম্পূর্ণ পাতা মরে ঘাস-রঙা হয়। "
            "সকালে পাতার ডগায় ব্যাকটেরিয়াল এক্সুডেট (আঠালো তরল) দেখা যায়।"
        ),
        "causes_bn": "Xanthomonas oryzae pv. oryzae ব্যাকটেরিয়া। বন্যা, ঝড় ও আঘাতের মাধ্যমে ছড়ায়।",
        "remedies_bn": [
            "কপার অক্সিক্লোরাইড ০.৩% হারে স্প্রে করুন।",
            "স্ট্রেপ্টোমাইসিন সালফেট + টেট্রাসাইক্লিন মিশ্রণ স্প্রে করুন।",
            "আক্রান্ত জমির পানি নিষ্কাশন করুন।",
        ],
        "prevention_bn": [
            "BRRI dhan47, 51 এর মতো প্রতিরোধী জাত ব্যবহার করুন।",
            "সুষম সার ব্যবস্থাপনা মেনে চলুন।",
            "বন্যার পানি দ্রুত সরানোর ব্যবস্থা রাখুন।",
        ],
        "severity": "high",
        "season": ["kharif"],
        "image_hint": "bacterial_leaf_blight_yellow_edges",
    },
    {
        "id": "paddy_sheath_blight",
        "crop": "paddy",
        "crop_bn": "ধান",
        "name": "Sheath Blight",
        "name_bn": "খোল পচা রোগ (শিথ ব্লাইট)",
        "category": "fungal",
        "affected_parts": ["sheath", "leaf"],
        "symptoms_bn": (
            "পানির কাছে কান্ডের খোলে ডিম্বাকার সবুজ-ধূসর দাগ দেখা যায়। "
            "দাগ বড় হয়ে পাতায় ছড়িয়ে পড়ে। গাছ দুর্বল হয়ে হেলে পড়ে।"
        ),
        "causes_bn": "Rhizoctonia solani ছত্রাক। ঘন রোপণ ও অতিরিক্ত নাইট্রোজেন সারে বেশি হয়।",
        "remedies_bn": [
            "ভ্যালিডামাইসিন (Validamycin) ৩ এল – ২ মিলি/লিটার পানিতে স্প্রে করুন।",
            "প্রোপিকোনাজল (Propiconazole) ২৫ EC – ১ মিলি/লিটার পানিতে স্প্রে করুন।",
            "আক্রান্ত খড় সরিয়ে পুড়িয়ে ফেলুন।",
        ],
        "prevention_bn": [
            "সারির মধ্যে দূরত্ব বজায় রাখুন (২৫×১৫ সেমি)।",
            "নাইট্রোজেন সার ভাগে ভাগে দিন।",
            "জমিতে পানি নিয়ন্ত্রণ করুন।",
        ],
        "severity": "medium",
        "season": ["kharif", "rabi"],
        "image_hint": "sheath_blight_oval_lesions",
    },
    {
        "id": "paddy_tungro",
        "crop": "paddy",
        "crop_bn": "ধান",
        "name": "Tungro Virus",
        "name_bn": "টুংরো ভাইরাস রোগ",
        "category": "viral",
        "affected_parts": ["leaf", "plant"],
        "symptoms_bn": (
            "পাতা হলুদ বা কমলা-হলুদ হয়ে যায়। গাছ খাটো থাকে, শীষ বের হয় না বা অসম্পূর্ণ থাকে। "
            "পাতার ডগা থেকে হলদে রঙ শুরু হয়।"
        ),
        "causes_bn": "Rice Tungro Bacilliform Virus (RTBV) ও Rice Tungro Spherical Virus (RTSV)। সবুজ পাতার হপার (Nephotettix virescens) দ্বারা ছড়ায়।",
        "remedies_bn": [
            "কোনো সরাসরি চিকিৎসা নেই – আক্রান্ত গাছ তুলে ফেলুন।",
            "সবুজ হপার দমনে কার্বোফুরান ৩জি বা ক্লোরপাইরিফস স্প্রে করুন।",
            "ইমিডাক্লোপ্রিড ৭০ WS দিয়ে বীজ শোধন করুন।",
        ],
        "prevention_bn": [
            "একই সময়ে রোপণ করুন (synchronized planting)।",
            "প্রতিরোধী জাত ব্যবহার করুন (BRRI dhan32, 40)।",
            "জমির আশেপাশের আগাছা পরিষ্কার রাখুন।",
        ],
        "severity": "high",
        "season": ["kharif"],
        "image_hint": "tungro_yellow_leaves",
    },

    # ─────────────────────────── POTATO ───────────────────────────
    {
        "id": "potato_late_blight",
        "crop": "potato",
        "crop_bn": "আলু",
        "name": "Late Blight",
        "name_bn": "আলুর নাবি ধ্বসা (লেট ব্লাইট)",
        "category": "fungal",
        "affected_parts": ["leaf", "stem", "tuber"],
        "symptoms_bn": (
            "পাতায় পানিতে ভেজা ধূসর-বাদামি দাগ। আর্দ্র আবহাওয়ায় পাতার নিচে সাদা ছাঁচ দেখা যায়। "
            "গাছ দ্রুত পচে যায়। কন্দে বাদামি-কালো দাগ পড়ে।"
        ),
        "causes_bn": "Phytophthora infestans। ঠান্ডা (১০–১৫°C) ও আর্দ্র (>৯০% RH) আবহাওয়ায় দ্রুত ছড়ায়।",
        "remedies_bn": [
            "মেটালাক্সিল + ম্যানকোজেব (Ridomil Gold MZ) – ২.৫ গ্রাম/লিটার পানিতে স্প্রে করুন।",
            "কপার অক্সিক্লোরাইড ৫০ WP – ৩ গ্রাম/লিটার স্প্রে করুন।",
            "ডাইফেনোকোনাজল + ম্যান্ডিপ্রোপামিড স্প্রে করুন।",
            "আক্রান্ত গাছ তুলে মাটিতে পুঁতুন বা পুড়িয়ে ফেলুন।",
        ],
        "prevention_bn": [
            "সার্টিফাইড বীজ ব্যবহার করুন।",
            "৭–১০ দিন অন্তর প্রতিরোধক ছত্রাকনাশক স্প্রে করুন।",
            "জমিতে পানি জমতে দেবেন না।",
            "ফসল কাটার পর জমি ভালো করে পরিষ্কার করুন।",
        ],
        "severity": "high",
        "season": ["rabi"],
        "image_hint": "potato_late_blight_dark_lesions",
    },
    {
        "id": "potato_early_blight",
        "crop": "potato",
        "crop_bn": "আলু",
        "name": "Early Blight",
        "name_bn": "আলুর আগাম ধ্বসা (আর্লি ব্লাইট)",
        "category": "fungal",
        "affected_parts": ["leaf", "stem"],
        "symptoms_bn": (
            "পুরনো পাতায় বাদামি, গোলাকার দাগ যার মধ্যে কেন্দ্রিক রিং থাকে (টার্গেট বোর্ডের মতো)। "
            "দাগের চারদিকে হলুদ হালো। শেষে পাতা শুকিয়ে ঝরে পড়ে।"
        ),
        "causes_bn": "Alternaria solani ছত্রাক। গরম ও আর্দ্র আবহাওয়ায় বেশি হয়।",
        "remedies_bn": [
            "ক্লোরোথালোনিল ৭৫ WP – ২ গ্রাম/লিটার পানিতে স্প্রে করুন।",
            "ম্যানকোজেব ৮০ WP – ২ গ্রাম/লিটার স্প্রে করুন।",
            "আজোক্সিস্ট্রোবিন গ্রুপের ছত্রাকনাশক ব্যবহার করুন।",
        ],
        "prevention_bn": [
            "ফসল আবর্তন (crop rotation) করুন।",
            "গাছের নিচের দিকের পাতা ভেজা রাখবেন না।",
            "সুষম পটাশ ও ফসফেট সার দিন।",
        ],
        "severity": "medium",
        "season": ["rabi"],
        "image_hint": "potato_early_blight_target_spots",
    },

    # ─────────────────────────── TOMATO ───────────────────────────
    {
        "id": "tomato_late_blight",
        "crop": "tomato",
        "crop_bn": "টমেটো",
        "name": "Late Blight",
        "name_bn": "টমেটোর নাবি ধ্বসা",
        "category": "fungal",
        "affected_parts": ["leaf", "stem", "fruit"],
        "symptoms_bn": (
            "পাতায় পানি-ভেজা বাদামি দাগ, পাতার নিচে সাদা ছাঁচ। ফলে বাদামি, শক্ত দাগ পড়ে। "
            "গাছ দ্রুত মরে যায়।"
        ),
        "causes_bn": "Phytophthora infestans। ঠান্ডা ও আর্দ্র আবহাওয়ায় দ্রুত ছড়ায়।",
        "remedies_bn": [
            "মেটালাক্সিল + ম্যানকোজেব – ২.৫ গ্রাম/লিটার স্প্রে করুন।",
            "কপার হাইড্রোক্সাইড স্প্রে করুন।",
            "আক্রান্ত ফল ও পাতা সংগ্রহ করে ধ্বংস করুন।",
        ],
        "prevention_bn": [
            "সারির মধ্যে দূরত্ব বজায় রাখুন।",
            "ওপর থেকে সেচ না দিয়ে গোড়ায় পানি দিন।",
            "স্বাস্থ্যকর বীজতলা থেকে চারা সংগ্রহ করুন।",
        ],
        "severity": "high",
        "season": ["rabi"],
        "image_hint": "tomato_late_blight_brown_spots",
    },
    {
        "id": "tomato_leaf_curl",
        "crop": "tomato",
        "crop_bn": "টমেটো",
        "name": "Leaf Curl Virus",
        "name_bn": "টমেটো লিফ কার্ল ভাইরাস",
        "category": "viral",
        "affected_parts": ["leaf", "plant"],
        "symptoms_bn": (
            "পাতা উপরের দিকে কুঁকড়ে যায়। পাতা মোটা, চামড়ার মতো হয়। "
            "নতুন পাতা সবুজ কিন্তু ছোট থাকে। ফলন ব্যাপক কমে যায়।"
        ),
        "causes_bn": "Tomato Leaf Curl Virus (ToLCV)। সাদামাছি (Bemisia tabaci) দ্বারা ছড়ায়।",
        "remedies_bn": [
            "কোনো সরাসরি ভাইরাস চিকিৎসা নেই।",
            "সাদামাছি দমনে ইমিডাক্লোপ্রিড ৭০ WS বা থায়ামেথক্সাম স্প্রে করুন।",
            "আক্রান্ত গাছ তুলে পুড়িয়ে ফেলুন।",
        ],
        "prevention_bn": [
            "সাদামাছি-রোধী জাল দিয়ে বীজতলা ঢেকে রাখুন।",
            "হলুদ আঠালো ফাঁদ ব্যবহার করুন।",
            "প্রতিরোধী জাত ব্যবহার করুন (BARI Tomato-14)।",
        ],
        "severity": "high",
        "season": ["kharif", "rabi"],
        "image_hint": "tomato_leaf_curl_curled_leaves",
    },

    # ─────────────────────────── JUTE ───────────────────────────
    {
        "id": "jute_stem_rot",
        "crop": "jute",
        "crop_bn": "পাট",
        "name": "Stem Rot",
        "name_bn": "পাটের কাণ্ড পচা রোগ",
        "category": "fungal",
        "affected_parts": ["stem", "root"],
        "symptoms_bn": (
            "কান্ডের গোড়ায় বাদামি-কালো দাগ, গাছ হেলে পড়ে। "
            "কান্ডের ভেতর পচে যায় ও ভেঙে পড়ে।"
        ),
        "causes_bn": "Macrophomina phaseolina ও Sclerotium rolfsii ছত্রাক। জলাবদ্ধতায় বেশি হয়।",
        "remedies_bn": [
            "কার্বেন্ডাজিম ৫০ WP – ১ গ্রাম/লিটার পানিতে গোড়ায় স্প্রে করুন।",
            "ট্রাইকোডার্মা ভিরিডি জৈব ছত্রাকনাশক ব্যবহার করুন।",
            "আক্রান্ত গাছ তুলে পুড়িয়ে ফেলুন।",
        ],
        "prevention_bn": [
            "জমিতে পানি নিষ্কাশনের ব্যবস্থা নিশ্চিত করুন।",
            "ফসল আবর্তন করুন।",
            "বীজ শোধন করে বপন করুন।",
        ],
        "severity": "medium",
        "season": ["kharif"],
        "image_hint": "jute_stem_rot_brown_base",
    },

    # ─────────────────────────── WHEAT ───────────────────────────
    {
        "id": "wheat_rust",
        "crop": "wheat",
        "crop_bn": "গম",
        "name": "Wheat Rust (Yellow/Brown/Black)",
        "name_bn": "গমের মরিচা রোগ",
        "category": "fungal",
        "affected_parts": ["leaf", "stem", "panicle"],
        "symptoms_bn": (
            "পাতায় ও কান্ডে হলুদ, বাদামি বা কালো মরিচার মতো গুঁড়া দেখা যায়। "
            "আক্রান্ত গাছ দুর্বল হয় ও দানা পুষ্ট হয় না।"
        ),
        "causes_bn": "Puccinia striiformis (হলুদ), Puccinia triticina (বাদামি), Puccinia graminis (কালো) ছত্রাক।",
        "remedies_bn": [
            "প্রোপিকোনাজল ২৫ EC – ১ মিলি/লিটার স্প্রে করুন।",
            "টেবুকোনাজল ২৫.৯% EC স্প্রে করুন।",
            "ট্রিফ্লোক্সিস্ট্রোবিন + টেবুকোনাজল মিশ্রণ ব্যবহার করুন।",
        ],
        "prevention_bn": [
            "BARI Gom-26, 28, 30 প্রতিরোধী জাত ব্যবহার করুন।",
            "সঠিক সময়ে বপন করুন (নভেম্বর ১৫–৩০)।",
            "নাইট্রোজেন সার সঠিক মাত্রায় দিন।",
        ],
        "severity": "high",
        "season": ["rabi"],
        "image_hint": "wheat_rust_orange_pustules",
    },

    # ─────────────────────────── MUSTARD ───────────────────────────
    {
        "id": "mustard_white_rust",
        "crop": "mustard",
        "crop_bn": "সরিষা",
        "name": "White Rust / Downy Mildew",
        "name_bn": "সরিষার সাদা মরিচা ও ডাউনি মিলডিউ",
        "category": "fungal",
        "affected_parts": ["leaf", "stem", "flower"],
        "symptoms_bn": (
            "পাতার উপরে হলুদ দাগ ও নিচে সাদা পাউডার বা গুটি। "
            "ফুল ও কান্ড বিকৃত হয়ে যায়।"
        ),
        "causes_bn": "Albugo candida (সাদা মরিচা) ও Peronospora parasitica (ডাউনি মিলডিউ) ছত্রাক।",
        "remedies_bn": [
            "ম্যানকোজেব ৮০ WP – ২.৫ গ্রাম/লিটার স্প্রে করুন।",
            "মেটালাক্সিল + ম্যানকোজেব স্প্রে করুন।",
            "কপার অক্সিক্লোরাইড ব্যবহার করুন।",
        ],
        "prevention_bn": [
            "BARI Sarisha-14, 15 প্রতিরোধী জাত ব্যবহার করুন।",
            "ঘন বপন পরিহার করুন।",
            "অতিরিক্ত আর্দ্রতা যেন না থাকে।",
        ],
        "severity": "medium",
        "season": ["rabi"],
        "image_hint": "mustard_white_rust_white_pustules",
    },

    # ─────────────────────────── ONION/GARLIC ───────────────────────────
    {
        "id": "onion_purple_blotch",
        "crop": "onion",
        "crop_bn": "পেঁয়াজ",
        "name": "Purple Blotch",
        "name_bn": "পেঁয়াজের বেগুনি দাগ রোগ",
        "category": "fungal",
        "affected_parts": ["leaf", "stem"],
        "symptoms_bn": (
            "পাতায় সাদা কেন্দ্র সহ ছোট দাগ, পরে বেগুনি রঙে পরিণত হয়। "
            "আর্দ্র আবহাওয়ায় দাগে কালচে ছাঁচ দেখা যায়। পাতা মরে যায়।"
        ),
        "causes_bn": "Alternaria porri ছত্রাক। বৃষ্টি ও কুয়াশায় দ্রুত ছড়ায়।",
        "remedies_bn": [
            "ইপ্রোডায়ন (Iprodione) ৫০ WP – ১.৫ গ্রাম/লিটার স্প্রে করুন।",
            "ম্যানকোজেব ৮০ WP স্প্রে করুন।",
            "কার্বেন্ডাজিম ব্যবহার করুন।",
        ],
        "prevention_bn": [
            "বীজ ভালোভাবে শোধন করুন।",
            "গাছের ঘনত্ব কমান।",
            "পাতা না ভিজে সেচ দিন।",
        ],
        "severity": "medium",
        "season": ["rabi"],
        "image_hint": "onion_purple_blotch",
    },

    # ─────────────────────────── BRINJAL / EGGPLANT ───────────────────────────
    {
        "id": "brinjal_shoot_borer",
        "crop": "brinjal",
        "crop_bn": "বেগুন",
        "name": "Brinjal Shoot and Fruit Borer",
        "name_bn": "বেগুনের ডগা ও ফল ছিদ্রকারী পোকা",
        "category": "pest",
        "affected_parts": ["shoot", "fruit"],
        "symptoms_bn": (
            "ডগা ঝলসানো ও শুকনো। ফলে ছোট ছিদ্র দেখা যায়, ভেতর পচা। "
            "কচি ডগা নেতিয়ে পড়ে (ডেড হার্ট)।"
        ),
        "causes_bn": "Leucinodes orbonalis পোকার শুককীট (larvae)। বছরব্যাপী আক্রমণ করে।",
        "remedies_bn": [
            "সাইপারমেথ্রিন ১০ EC – ১ মিলি/লিটার স্প্রে করুন।",
            "স্পাইনোস্যাড ৪৫ SC – ০.৩ মিলি/লিটার স্প্রে করুন।",
            "ইমামেকটিন বেনজোয়েট ৫ SG ব্যবহার করুন।",
            "আক্রান্ত ডগা ও ফল নিয়মিত সংগ্রহ করে পুড়িয়ে ফেলুন।",
        ],
        "prevention_bn": [
            "ফেরোমন ফাঁদ ব্যবহার করুন।",
            "প্রতিরোধী জাত (BARI Begun-8) ব্যবহার করুন।",
            "পাখির বাসা (পার্চিং) স্থাপন করুন।",
        ],
        "severity": "high",
        "season": ["kharif", "rabi"],
        "image_hint": "brinjal_shoot_borer_wilted_tip",
    },

    # ─────────────────────────── CHILI / PEPPER ───────────────────────────
    {
        "id": "chili_anthracnose",
        "crop": "chili",
        "crop_bn": "মরিচ",
        "name": "Anthracnose / Fruit Rot",
        "name_bn": "মরিচের অ্যান্থ্রাকনোজ / ফল পচা",
        "category": "fungal",
        "affected_parts": ["fruit", "leaf"],
        "symptoms_bn": (
            "ফলে বাদামি, পানি-ভেজা দাগ, মধ্যে গোলাপি বা কমলা রঙের বীজপত্র (spore mass)। "
            "দাগ বড় হয়ে ফল পচে যায়।"
        ),
        "causes_bn": "Colletotrichum capsici ও C. gloeosporioides ছত্রাক। বৃষ্টি ও আর্দ্র আবহাওয়ায় বেশি হয়।",
        "remedies_bn": [
            "কার্বেন্ডাজিম ৫০ WP – ১ গ্রাম/লিটার স্প্রে করুন।",
            "ডাইফেনোকোনাজল ২৫ EC – ০.৫ মিলি/লিটার স্প্রে করুন।",
            "আজোক্সিস্ট্রোবিন ব্যবহার করুন।",
        ],
        "prevention_bn": [
            "সুস্থ বীজ ব্যবহার করুন।",
            "বীজ কার্বেন্ডাজিম দিয়ে শোধন করুন।",
            "ফসল আবর্তন করুন।",
        ],
        "severity": "medium",
        "season": ["kharif", "rabi"],
        "image_hint": "chili_anthracnose_fruit_rot",
    },

    # ─────────────────────────── SUGARCANE ───────────────────────────
    {
        "id": "sugarcane_red_rot",
        "crop": "sugarcane",
        "crop_bn": "আখ",
        "name": "Red Rot",
        "name_bn": "আখের লাল পচা রোগ",
        "category": "fungal",
        "affected_parts": ["stalk", "leaf"],
        "symptoms_bn": (
            "পাতার মধ্যশিরা লাল হয়ে যায়। কান্ড কাটলে ভেতরে লাল রঙ ও সাদা দাগ দেখা যায়। "
            "গাছ শুকিয়ে মরে যায়।"
        ),
        "causes_bn": "Colletotrichum falcatum ছত্রাক। আঘাত বা পোকার মাধ্যমে ছড়ায়।",
        "remedies_bn": [
            "কার্বেন্ডাজিম ৫০ WP – ১ গ্রাম/লিটার দ্রবণে বীজ আখ ভিজিয়ে লাগান।",
            "আক্রান্ত গাছ তুলে পুড়িয়ে ফেলুন।",
            "ছত্রাকনাশক দ্রবণ গোড়ায় ঢালুন।",
        ],
        "prevention_bn": [
            "রোগমুক্ত বীজ আখ ব্যবহার করুন।",
            "প্রতিরোধী জাত ব্যবহার করুন (Isd 36, Isd 37)।",
            "জমি পরিষ্কার রাখুন।",
        ],
        "severity": "high",
        "season": ["kharif", "rabi"],
        "image_hint": "sugarcane_red_rot_internal_red",
    },

    # ─────────────────────────── GENERAL PESTS ───────────────────────────
    {
        "id": "general_aphid",
        "crop": "general",
        "crop_bn": "সাধারণ (যেকোনো ফসল)",
        "name": "Aphid Infestation",
        "name_bn": "জাবপোকা (এফিড) আক্রমণ",
        "category": "pest",
        "affected_parts": ["leaf", "stem", "flower"],
        "symptoms_bn": (
            "পাতার নিচে ছোট সবুজ বা কালো পোকার দল। পাতা কুঁকড়ে হলুদ হয়। "
            "মিষ্টি আঠালো রস (হানিডিউ) নিঃসৃত হয়, কালো ছাঁচ জন্মায়।"
        ),
        "causes_bn": "বিভিন্ন প্রজাতির এফিড। শুকনো আবহাওয়ায় দ্রুত বংশবৃদ্ধি করে।",
        "remedies_bn": [
            "ইমিডাক্লোপ্রিড ৭০ WS বা ডাইমেথোয়েট ৪০ EC – ২ মিলি/লিটার স্প্রে করুন।",
            "নিম তেল (Neem oil) ৫ মিলি/লিটার স্প্রে করুন।",
            "সাবান-জল মিশ্রণ (১০ গ্রাম সাবান/লিটার) স্প্রে করুন।",
        ],
        "prevention_bn": [
            "হলুদ আঠালো ফাঁদ ব্যবহার করুন।",
            "প্রাকৃতিক শত্রু (লেডিবার্ড বিটল) সংরক্ষণ করুন।",
            "অতিরিক্ত নাইট্রোজেন সার পরিহার করুন।",
        ],
        "severity": "medium",
        "season": ["kharif", "rabi"],
        "image_hint": "aphid_colony_leaf_underside",
    },
    {
        "id": "general_mites",
        "crop": "general",
        "crop_bn": "সাধারণ (যেকোনো ফসল)",
        "name": "Spider Mites",
        "name_bn": "মাকড় (স্পাইডার মাইট)",
        "category": "pest",
        "affected_parts": ["leaf"],
        "symptoms_bn": (
            "পাতায় সূক্ষ্ম হলুদ বিন্দু। পাতার নিচে সরু জালিকা। "
            "পাতা বাদামি হয়ে ঝরে পড়ে।"
        ),
        "causes_bn": "Tetranychus urticae (Red spider mite)। গরম ও শুষ্ক আবহাওয়ায় বেশি হয়।",
        "remedies_bn": [
            "অ্যাবামেকটিন ১.৮ EC – ১ মিলি/লিটার স্প্রে করুন।",
            "প্রোপারজাইট ৫৭ EC – ২ মিলি/লিটার স্প্রে করুন।",
            "নিম তেল স্প্রে করুন।",
        ],
        "prevention_bn": [
            "গাছে পানি স্প্রে করে আর্দ্রতা বজায় রাখুন।",
            "আক্রান্ত পাতা তুলে ফেলুন।",
            "একই কীটনাশক বারবার ব্যবহার করবেন না (প্রতিরোধ ক্ষমতা তৈরি হয়)।",
        ],
        "severity": "medium",
        "season": ["rabi"],
        "image_hint": "spider_mites_webbing",
    },
]


FARMING_TIPS: list[dict] = [
    {
        "id": "tip_soil_test",
        "category": "soil",
        "category_bn": "মাটি ব্যবস্থাপনা",
        "title_bn": "মাটি পরীক্ষা করুন",
        "body_bn": (
            "প্রতি ৩ বছর অন্তর মাটি পরীক্ষা করুন। জেলা কৃষি অফিস বা SRDI মাটি পরীক্ষা করে। "
            "মাটির pH, জৈব পদার্থ ও পুষ্টি উপাদান জানলে সঠিক পরিমাণ সার দেওয়া সম্ভব হয়। "
            "মাটিতে জৈব সার (কম্পোস্ট, গোবর) মিশিয়ে জৈব পদার্থ বাড়ান।"
        ),
        "crops": ["all"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_crop_rotation",
        "category": "management",
        "category_bn": "ফসল ব্যবস্থাপনা",
        "title_bn": "ফসল আবর্তন (Crop Rotation)",
        "body_bn": (
            "একই জমিতে একই ফসল বারবার চাষ করবেন না। ধান-সরিষা-গম বা ধান-আলু-মুগডাল আবর্তন করুন। "
            "এতে মাটির পুষ্টি বজায় থাকে, রোগ-পোকার চাপ কমে এবং ফলন বাড়ে।"
        ),
        "crops": ["all"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_water_management",
        "category": "irrigation",
        "category_bn": "সেচ ব্যবস্থাপনা",
        "title_bn": "পানি সাশ্রয়ী সেচ পদ্ধতি",
        "body_bn": (
            "AWD (Alternate Wetting and Drying) পদ্ধতিতে ধান চাষে ৩০% পানি সাশ্রয় হয়। "
            "ফসলের জমিতে ৫ সেমি গভীর পাইপ পুঁতে পানির স্তর পর্যবেক্ষণ করুন। "
            "পানি ১৫ সেমি নিচে নামলে সেচ দিন। ড্রিপ সেচ সবজি ক্ষেতে সবচেয়ে কার্যকর।"
        ),
        "crops": ["paddy", "vegetable"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_ipm",
        "category": "pest_management",
        "category_bn": "সমন্বিত বালাই ব্যবস্থাপনা",
        "title_bn": "সমন্বিত বালাই ব্যবস্থাপনা (IPM)",
        "body_bn": (
            "কীটনাশক সর্বশেষ ব্যবস্থা হিসেবে ব্যবহার করুন। প্রথমে জৈব পদ্ধতি ব্যবহার করুন: "
            "ফেরোমন ফাঁদ, আলোক ফাঁদ, হলুদ আঠালো ফাঁদ, পাখির বাসা (পার্চিং)। "
            "কীটনাশক ব্যবহার করলে লেবেলের নির্দেশনা মেনে চলুন এবং নিরাপদ প্রতীক্ষাকাল (PHI) মানুন।"
        ),
        "crops": ["all"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_seed_treatment",
        "category": "seed",
        "category_bn": "বীজ ব্যবস্থাপনা",
        "title_bn": "বীজ শোধন পদ্ধতি",
        "body_bn": (
            "বপনের আগে বীজ শোধন করলে মাটি ও বীজবাহিত রোগ ৭০% কমে। "
            "ধান: ৫৪°C গরম পানিতে ১০ মিনিট ভিজিয়ে শোধন করুন। "
            "সবজি: কার্বেন্ডাজিম ১ গ্রাম প্রতি কেজি বীজে মেশান। "
            "আলু: কার্বেন্ডাজিম ৫০ WP ১ গ্রাম/লিটার দ্রবণে ৩০ মিনিট ভিজিয়ে লাগান।"
        ),
        "crops": ["all"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_fertilizer_bri",
        "category": "fertilizer",
        "category_bn": "সার ব্যবস্থাপনা",
        "title_bn": "ব্রি (BRRI) সারের মাত্রা অনুসরণ করুন",
        "body_bn": (
            "বোরো ধান প্রতি বিঘায়: ইউরিয়া ২০ কেজি, TSP ৮ কেজি, MOP ৮ কেজি, জিপসাম ৮ কেজি। "
            "আউশ ধান: ইউরিয়া ১৬ কেজি, TSP ৬ কেজি, MOP ৬ কেজি। "
            "আমন ধান: ইউরিয়া ১৬ কেজি, TSP ৬ কেজি, MOP ৬ কেজি। "
            "ইউরিয়া তিন ভাগে দিন: রোপণে ১/৩, কুশি পর্যায়ে ১/৩, শীষ বের হওয়ার আগে ১/৩।"
        ),
        "crops": ["paddy"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_post_harvest",
        "category": "post_harvest",
        "category_bn": "ফসল সংগ্রহোত্তর ব্যবস্থাপনা",
        "title_bn": "ফসল সংগ্রহোত্তর ক্ষতি কমান",
        "body_bn": (
            "সঠিক সময়ে ফসল কাটুন। ধান: ৮০% শীষ পাকলে কাটুন। আলু: পাতা মরে গেলে কাটুন। "
            "ফসল দ্রুত শুকান – ধান ১৩–১৪% আর্দ্রতায় সংগ্রহ করুন। "
            "পরিষ্কার পাত্রে সংগ্রহ করুন। ভালো বায়ু চলাচলের গুদামে রাখুন। "
            "হার্মেটিক ব্যাগ (Cocoons/PICS bag) ব্যবহার করলে শস্য পোকামুক্ত থাকে।"
        ),
        "crops": ["all"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_organic_farming",
        "category": "organic",
        "category_bn": "জৈব চাষাবাদ",
        "title_bn": "জৈব চাষাবাদের সুবিধা ও পদ্ধতি",
        "body_bn": (
            "কম্পোস্ট: গোবর, খড়, পাতা পচিয়ে ৩–৬ মাসে কম্পোস্ট তৈরি করুন। "
            "ভার্মিকম্পোস্ট: কেঁচো সার দ্রুত প্রস্তুত হয় ও পুষ্টিগুণ বেশি। "
            "সবুজ সার: ধইঞ্চা, শণ বপন করে মাটিতে মিশিয়ে দিন। "
            "জৈব পদ্ধতিতে চাষ করা পণ্যের বাজারমূল্য ২০–৩০% বেশি পাওয়া যায়।"
        ),
        "crops": ["all"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_weather_advisory",
        "category": "weather",
        "category_bn": "আবহাওয়া পরামর্শ",
        "title_bn": "আবহাওয়া সংক্রান্ত সতর্কতা",
        "body_bn": (
            "বাংলাদেশ আবহাওয়া অধিদপ্তর (BMD) ও কৃষি আবহাওয়া তথ্য পদ্ধতি (AMIS) থেকে নিয়মিত পূর্বাভাস দেখুন। "
            "বন্যার আগে ফসল আগেভাগে কেটে নিন। ঝড়ের আগে সেচ বন্ধ করুন। "
            "শিলাবৃষ্টির পর ছত্রাকনাশক স্প্রে করুন। খরায় মালচিং করুন।"
        ),
        "crops": ["all"],
        "season": ["kharif", "rabi"],
    },
    {
        "id": "tip_fish_rice",
        "category": "integrated_farming",
        "category_bn": "সমন্বিত চাষ",
        "title_bn": "ধান-মাছ সমন্বিত চাষ (Rice-Fish Farming)",
        "body_bn": (
            "ধান জমিতে মাছ চাষ করলে মাছ আগাছা ও পোকা খায়, মল সার হিসেবে কাজ করে। "
            "জমিতে ৩০ সেমি গভীর নালা কাটুন। রুই, কাতলা, মৃগেল ছাড়ুন (২০০–৩০০ পোনা/বিঘা)। "
            "কীটনাশক ব্যবহার কমবে, মাছ বিক্রিতে অতিরিক্ত আয় হবে।"
        ),
        "crops": ["paddy"],
        "season": ["kharif"],
    },
]


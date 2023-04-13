FIND_WEAPON_SCROLL_PART_1 = r"(?<=http://image\.neverlands\.ru/weapon/"

FIND_WEAPON_SCROLL_PART_2 = r"\.gif).+?\">"

FIND_DEAD_HIT = r"(?<=\</B\> \[).+(?=\]\.)"

# паттерн на строку с запросом точно хотите юзать
FIND_USE = r"(?<=w28_form\(').+(?='\)\")"

FIND_MAPBT = r"(?<=var mapbt = ).+(?=;)"

FIND_PARAM_OW = r"(?<=param_ow = \[).+(?=];)"

FIND_FEXP = r"(?<=fexp = \[).+(?=];)"

FIND_STATS = r"(?<='10\.12\.2006'],\[).+(?=\]\];)"

FIND_POS_VARS = r"(?<=pos_vars = ).+(?=;)"

FIND_POS_MANA = r"(?<=pos_mana = ).+(?=;)"

FIND_POS_TYPE = r"(?<=pos_type = ).+(?=;)"

FIND_POS_OCHD = r"(?<=pos_ochd = ).+(?=;)"


FIND_OBJ_ACTION = r"(?<=objActions = ).+(?=;)"

FIND_VAR_OBJ_ACTION = r"(?<=var objActions = ).+(?=};)"

FIND_FRAME = r"frame.css"

# w28_167 - имп вред
FIND_IMP_PAST = r"(?<=http://image\.neverlands\.ru/weapon/w28_167\.gif).+?\">"

# i_w28_22 - телепорт
FIND_TELEPORT = r"(?<=http://image\.neverlands\.ru/weapon/i_w28_22\.gif).+?\">"

# i_svi_212 - удар ярости
FIND_SCROLL_STRIKE_FURY = r"(?<=http://image\.neverlands\.ru/weapon/i_svi_212\.gif).+?\">"


FIND_PAGE_INVENTORY = r"(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)"

FIND_IN_CITY = r"(?<=Инвентарь\" onclick=\"location=\'main\.php\?).+(?=\'\">)"

# # mb oktal
# r'(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)'  # mb oktal

FIND_FROM_NATURE_TO_INV = r'(?<=Инвентарь",")\w+(?=",\[\]\]|",\[\]\],)'


FIND_INSHP = r"(?<=var inshp = \[).+(?=];)"


# # ! TODO: разобраться что это такое...
FIND_FIRST_PART = r"^[a-z]+[^A-Z]"

FIND_SECOND_PART = r"[A-Z][a-z]+"

# паттерн на строку с запросом
FIND_STRING_WITH_QUERY = r"(?<=php\?).+(?='\")"  # паттерн на строку с запросом

# # паттерн на долговечку
# FIND_STRING_DOLGOVECHKA = r"(?<=Долговечность: <b>)\d+/\d+(?=</b>)"  # паттерн на долговечку

FIND_EFFECTS_INFO_PATTERN = r"(?<=effects_view\(\[).+(?=\],)"

FIND_VAR_EFF = r"(?<=var eff = \[\[).+(?=]];)"

# # FIGHT
FIND_LIVES_G2 = r"(?<=lives_g2 = \[).+(?=];)|(?<=lives_g2 = \[).+\n.+(?=];)"

FIND_FIGHT_VARIABLES_PART1 = r"(?<="
FIND_FIGHT_VARIABLES_PART2 = r" = \[).+(?=];)"

# # From config_search and from local_config
DISABLED = r'(?<=class=lbutdis value=").+(?=" DISABLED>)'  # DISABLED page

# # ! TODO: разобраться
# BUT_INV = r'(?<=class=lbut onclick="location='main\.php)\S+(?='" value="Инвентарь")'
# BUT_INV = os.getenv("BUT_INV")  # go to inv page

# # ! TODO: разобраться
# TEXT =  r'(?<=Bi_w27_54\.gif border=0 width=40 height=40 onclick="location='main\.php)\S+(?=')
# TEXT = os.getenv("TEXT")

TEXT2 = r"(?<=get_id=43&act=101&)\S+(?=')"
# # From config_search and from local_config


SLOTS = r"(?<=slots_inv|slots_pla).+(?=;)"

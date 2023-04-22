FIND_PARAM_OW = r"(?<=param_ow = \[).+(?=];)"

FIND_FEXP = r"(?<=fexp = \[).+(?=];)"

FIND_PAGE_INVENTORY = r"(?<=&go=inv&vcode=).+(?=\'\" value=\"Инвентарь)"

FIND_IN_CITY = r"(?<=Инвентарь\" onclick=\"location=\'main\.php\?).+(?=\'\">)"

FIND_FROM_NATURE_TO_INV = r'(?<=Инвентарь",")\w+(?=",\[\]\]|",\[\]\],)'

FIND_LIVES_G2 = r"(?<=lives_g2 = \[).+(?=];)|(?<=lives_g2 = \[).+\n.+(?=];)"

FIND_FIGHT_VARIABLES_PART1 = r"(?<="

FIND_FIGHT_VARIABLES_PART2 = r" = \[).+(?=];)"

FIND_FIGHT = "var param_en"

FIND_DISABLED = "DISABLED"

FIND_INVENTORY = '"Инвентарь" DISABLED>'

FIND_CHAT = r"(?<=\.add_msg\().+(?=\);)"

FIND_MESSAGE_FOR_PERSON = r"(?<=<SPL>).+(?=<SPL>)"

FIND_SENDER_NAME = r"(?<=<SPAN>).+(?=</SPAN>)"

FIND_MESSAGE_TEXT = r"(?<=<font color=.{7}).+(?=</font>)"

FIND_ERROR = r"error.css"

FIND_USE_ITEM_PART1 = r"(?<=get_id=43&act="

FIND_USE_ITEM_PART2 = "&uid=).+?' }"

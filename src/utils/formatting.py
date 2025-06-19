def format_card_number(card_number: str) -> str:
    """Format a card number in blocks of 4 digits separated by spaces."""
    digits = ''.join(filter(str.isdigit, card_number))
    return ' '.join(digits[i:i+4] for i in range(0, len(digits), 4))


def format_phone_number(phone: str) -> str:
    """Format a phone number as (XXX) XXX-XXXX for 10 digits, or international style if longer."""
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    elif len(digits) > 10:
        # International: +CC ...
        cc_len = len(digits) - 10
        cc = digits[:cc_len]
        rest = digits[cc_len:]
        return f"+{cc} ({rest[:3]}) {rest[3:6]}-{rest[6:]}"
    else:
        return phone 
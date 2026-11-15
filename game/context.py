from .tips import CHARACTERS, GREETING, INTRO, TIPS

def guides(request):
    return {"guide_data": {"tips": TIPS, "characters": CHARACTERS, "greeting": GREETING, "intro": INTRO}}

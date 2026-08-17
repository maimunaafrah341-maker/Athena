# step 1: skeleton with hardcoded translation, no external calls yet

def process_input(user_input, input_type="text"):
    if input_type != "text":
        raise NotImplementedError("audio comes in step 3")

    # pretend "detection" and "translation" for one known sentence
    if user_input.strip() == "मदद चाहिए":
        return {"text_en": "I need help", "detected_lang": "hi"}

    # fallback: assume it's already English
    return {"text_en": user_input, "detected_lang": "en"}


def process_output(answer_text, target_lang, output_type="text"):
    if output_type != "text":
        raise NotImplementedError("audio comes in step 4")

    if target_lang == "hi" and answer_text == "Help is on the way":
        return {"text": "मदद रास्ते में है"}

    # fallback: no translation available yet
    return {"text": answer_text}


# smoke test
inp = process_input("मदद चाहिए")
print(inp)  # {'text_en': 'I need help', 'detected_lang': 'hi'}

out = process_output("Help is on the way", target_lang=inp["detected_lang"])
print(out)  # {'text': 'मदद रास्ते में है'}
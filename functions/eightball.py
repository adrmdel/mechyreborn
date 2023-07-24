import random

eightball_responses = [
    "It is the will of the Omnissiah.",
    "The Omnissiah has decreed it so.",
    "There can be no doubt to it.",
    "Such has been etched into the silica of prophecy.",
    "Rely on it as you would the Machine God.",
    "The Machine Spirits agree.",
    "It is as our projections expect.",
    "The Omnissiah looks favorably upon it.",
    "It must be so.",
    "It is the will of Mars.",
    "Our predictions provide no answer. Please permit additional processing time.",
    "The Omnissiah is silent on the matter.",
    "No Machine Spirit is available to answer. Try again later.",
    "The Warp shrouds our answers.",
    "Strengthen your will and ask once more.",
    "This goes against our Comprehension.",
    "The Omnissiah frowns upon it.",
    "Our projections show otherwise.",
    "This cannot be allowed.",
    "Do not ask of this again."
  ]


def eightball(query):
    if query is not None:
        result = "Your query was: " + query + "\nOur response is: " + random.choice(eightball_responses)
    else:
        result = random.choice(eightball_responses)
    return result

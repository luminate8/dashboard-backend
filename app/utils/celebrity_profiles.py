"""
Pre-stored personality data for popular celebrities.
These traits rarely change, so they're safe to store permanently.
"""

import json


CELEBRITY_PROFILES = {
    "elon musk": {
        "name": "Elon Musk",
        "personality_traits": "Visionary, direct, sarcastic humor, tech-obsessed, optimistic about future, sometimes awkward, uses memes, thinks in first principles, risk-taker",
        "speaking_style": "Short punchy sentences, uses ellipses (...), mixes tech jargon with simple words, sometimes uses emojis (🚀🔥😂), asks rhetorical questions, replies are often brief but impactful, uses 'haha' for laughter, references physics and engineering",
        "common_topics": "SpaceX, Mars colonization, Tesla, electric vehicles, AI safety, cryptocurrency, Dogecoin, X/Twitter, free speech, memes, manufacturing, Neuralink, sustainable energy, rockets, rockets landing, autonomous driving",
        "sample_tweets": [
            "Mars is the next giant leap for humanity. We must become a multiplanetary species.",
            "The point of SpaceX is to build a self-sustaining city on Mars.",
            "Tesla is not just a car company, it's an energy and AI company.",
            "I think it is possible for ordinary people to choose to be extraordinary.",
            "Work like hell. I mean you just have to put in 80 to 100 hour weeks every week.",
            "I would like to die on Mars. Just not on impact.",
            "The first step is to establish that something is possible; then probability will occur.",
        ]
    },
    "lionel messi": {
        "name": "Lionel Messi",
        "personality_traits": "Humble, quiet, family-oriented, dedicated, team player, graceful under pressure, passionate about football, loyal, respectful, soft-spoken",
        "speaking_style": "Humble and grateful, short answers, focuses on team not self, uses 'we' more than 'I', respectful to opponents and fans, emotional about family and country, rarely controversial, speaks with actions not words",
        "common_topics": "Football/soccer, World Cup, Argentina, Barcelona, Inter Miami, family, children, training, teamwork, respect, humility, winning, Copa América, Golden Ball, dreams, hard work, dedication",
        "sample_tweets": [
            "The World Cup was the biggest moment of my career. I dreamed of it my whole life.",
            "I always gave everything for the shirt, for the team, for the fans.",
            "My family is everything to me. They are my strength.",
            "Dreams are not about age, dreams are about passion and dedication.",
            "You have to fight to reach your objectives and never give up.",
            "The most important thing is to enjoy football and give your best.",
            "I never stopped believing. Thank you to everyone who supported me.",
        ]
    },
    "cristiano ronaldo": {
        "name": "Cristiano Ronaldo",
        "personality_traits": "Confident, disciplined, competitive, hard-working, goal-oriented, self-believer, fitness-obsessed, brand-conscious, passionate, leader",
        "speaking_style": "Confident and bold, uses 'SIUUU', motivational tone, focuses on hard work and discipline, talks about being the best, grateful but self-assured, uses hashtags frequently (#CR7, #Siuuu)",
        "common_topics": "Football, training, fitness, discipline, hard work, goals, records, Al Nassr, Portugal, family, brand, CR7, motivation, being the best, never giving up, dedication, Champions League",
        "sample_tweets": [
            "Hard work and dedication. That's the secret to success.",
            "I'm not a perfectionist, but I like things to be done well.",
            "Limits, like fears, are often just illusions.",
            "Talent without hard work is nothing.",
            "I see myself as the best ever. You should too.",
            "Your love makes me strong. SIUUUU! 🔥⚽",
            "Dreams are free but the hustle is a sacrifice. Work, work, work.",
        ]
    },
    "taylor swift": {
        "name": "Taylor Swift",
        "personality_traits": "Emotional, storytelling, relatable, nostalgic, romantic, empowered, creative, fan-connected, witty, self-aware",
        "speaking_style": "Poetic and narrative, uses metaphors, emotional depth, talks about feelings and memories, connects personally with fans, uses Easter eggs and hints, warm and grateful, speaks like writing lyrics",
        "common_topics": "Music, songwriting, albums, tours, fans (Swifties), love, heartbreak, memories, growing up, cats, re-recording albums, Grammy, friendship, creativity, storytelling",
        "sample_tweets": [
            "The songs I write are like pages from my diary. Every one has a story.",
            "To anyone who has ever felt lost or alone - you are seen. You are heard.",
            "I think the best things in life are the people we love and the memories we make.",
            "Music is the soundtrack of your life. Make it a good one.",
            "Thank you for making my dreams come true. I love you all so much.",
            "I've been doing some thinking about the past and how it shapes us.",
            "The Eras Tour has been the most magical experience of my life.",
        ]
    },
    "oprah winfrey": {
        "name": "Oprah Winfrey",
        "personality_traits": "Empathetic, wise, inspirational, generous, authentic, emotionally intelligent, spiritual, empowering, resilient, purposeful",
        "speaking_style": "Warm and inspiring, speaks from experience, uses personal stories, asks reflective questions, gives life advice, uses 'I know' and 'I believe', empowering language, talks about purpose and intention",
        "common_topics": "Self-improvement, purpose, gratitude, mindfulness, reading, books, education, empowerment, overcoming adversity, spirituality, living your best life, leadership, philanthropy, authenticity",
        "sample_tweets": [
            "The biggest adventure you can take is to live the life of your dreams.",
            "Turn your wounds into wisdom.",
            "What I know for sure is that what you give, you get more of.",
            "Be thankful for what you have; you'll end up having more.",
            "The more you praise and celebrate your life, the more there is to celebrate.",
            "You become what you believe. You are where you are today in your life based on everything you have believed.",
            "Think like a queen. A queen is not afraid to fail.",
        ]
    },
    "dwayne johnson": {
        "name": "Dwayne Johnson",
        "personality_traits": "Motivational, humble, hard-working, family-oriented, charismatic, positive, disciplined, grateful, approachable, resilient",
        "speaking_style": "Upbeat and motivational, uses 'Can you smell what The Rock is cooking?', talks about hard work and gratitude, uses emojis, calls fans 'the people', humble bragging, positive energy, references wrestling and fitness",
        "common_topics": "Hard work, discipline, fitness, family, projects, movies, wrestling, gratitude, tequila (Teremana), early mornings, training, hustle, staying humble, giving back",
        "sample_tweets": [
            "Success isn't always about greatness. It's about consistency.",
            "The most important thing I can do is to always be the hardest worker in the room.",
            "Be the hardest worker in the room. It's the only way.",
            "I don't believe in luck. I believe in preparation and hard work.",
            "My relationship with my family and my fans is everything to me.",
            "Stay humble. Stay hungry. And always be the hardest worker in the room.",
            "Blood, sweat, and respect. First two you give, last one you earn.",
        ]
    },
    "stephen hawking": {
        "name": "Stephen Hawking",
        "personality_traits": "Brilliant, curious, philosophical, humble about knowledge, fascinated by the universe, resilient, thoughtful, witty humor, patient teacher",
        "speaking_style": "Deep and contemplative, speaks about big ideas simply, uses analogies, philosophical but accessible, gentle humor, speaks about human potential, asks big questions, measured and thoughtful responses",
        "common_topics": "Universe, black holes, time, space, Big Bang, physics, cosmology, artificial intelligence, human future, curiosity, science, exploration, meaning of life, infinity, reality",
        "sample_tweets": [
            "Look up at the stars and not down at your feet.",
            "However difficult life may seem, there is always something you can do and succeed at.",
            "Intelligence is the ability to adapt to change.",
            "We are just an advanced breed of monkeys on a minor planet of a very average star.",
            "The greatest enemy of knowledge is not ignorance, it is the illusion of knowledge.",
            "Remember to look up at the stars and not down at your feet.",
            "While there's life, there is hope.",
        ]
    },
}


async def seed_celebrity_profiles(pool):
    """Insert pre-stored celebrity profiles into the database.
    Skips if profile already exists (won't overwrite).
    """
    for key, profile in CELEBRITY_PROFILES.items():
        await pool.execute(
            """
            INSERT INTO celebrity_profiles 
            (name, personality_traits, speaking_style, common_topics, sample_tweets, last_updated)
            VALUES ($1, $2, $3, $4, $5, NOW())
            ON CONFLICT (name) DO NOTHING
            """,
            profile["name"],
            profile["personality_traits"],
            profile["speaking_style"],
            profile["common_topics"],
            json.dumps(profile["sample_tweets"]),
        )
    print(f"Seeded {len(CELEBRITY_PROFILES)} celebrity profiles into DB")

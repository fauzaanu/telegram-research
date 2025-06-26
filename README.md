# Telegram Research

A fully local research LLM agent that is infinite and uses telegram messages to store its findings. (also stores local files)

### Process

1. Create multiple questions around the topic of research
2. Each question is asked to the LLM and the answer is retrieved
3. For each answer a Telegram Topic is created within a group and the answer is sent
4. Each answer also produces more questions from the answer, however primary questions will always be answered first through a que

#### Other stuff

The system prompt is fully dynamic when getting the answer. A prompt engineer expert is tasked with creating the system prompt for each prompt sent to the LLM.

### Usecases?

Perheps running this on an idle PC somewhere and collecting data for a focused research autonomousely while doing something else. The interesting thing is this will keep going digging deeper and deeper and you can access them on telegram, perheps delete the messages if they are irrelevant. Or move the stuff that is relevant to another manual topic you create.
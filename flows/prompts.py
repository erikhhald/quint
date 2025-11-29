KEY_IDEAS_PROMPT = """You are an expert at extracting key concepts and ideas from educational content. Analyze the following markdown text and extract the most important key ideas that would be useful for spaced repetition learning.

Your task:
1. Identify the main topic/subject of the content
2. Identify the core concepts, facts, and principles
3. Extract important details that a learner should remember
4. Focus on actionable knowledge and memorable insights
5. Present ideas in a clear, concise format

Provide:
- A brief topic title that summarizes the overall subject matter
- For each key idea, provide:
  - A brief, descriptive title (2-8 words)
  - A detailed description explaining the concept clearly

Text to analyze:

{text}

Extract the topic and key ideas and format them as JSON with the specified structure."""

JUDGE_ANSWER_PROMPT = """You are an expert educator evaluating a student's understanding of key concepts. A student was asked about a topic and provided an answer. Your task is to determine which key concepts the student demonstrates understanding of based on their response.

Analysis Guidelines:
1. Look for evidence that the student UNDERSTANDS each key concept, not just mentions it
2. Consider if the student can explain, apply, or demonstrate knowledge of the concept
3. Look for correct relationships between concepts
4. Consider partial understanding vs complete misunderstanding
5. Focus on comprehension rather than perfect recall of exact wording

Student's Answer:
{answer}

Key Ideas to Evaluate:
{key_ideas}

For each key idea, determine if the student's answer demonstrates adequate understanding. Return only the titles of key ideas that the student shows they understand.

Format your response as JSON with an array of key idea titles that the student demonstrates understanding of."""


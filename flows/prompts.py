KEY_IDEAS_PROMPT = """You are an expert at extracting key concepts and ideas from educational content. Analyze the following markdown text and extract the most important key ideas that would be useful for spaced repetition learning.

Your task:
1. Identify the core concepts, facts, and principles
2. Extract important details that a learner should remember
3. Focus on actionable knowledge and memorable insights
4. Present ideas in a clear, concise format

For each key idea, provide:
- A brief, descriptive title (2-8 words)
- A detailed description explaining the concept clearly

Text to analyze:

{text}

Extract the key ideas and format them as JSON with the specified structure."""
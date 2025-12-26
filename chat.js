const express = require('express');
const axios = require('axios');
const router = express.Router();

const GROQ_API_KEY = process.env.GROQ_API_KEY;
const GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions';

router.post('/', async (req, res) => {
  try {
    const { message } = req.body;

    if (!message || !message.trim()) {
      return res.status(400).json({ success: false, error: 'Message is required' });
    }

    if (!GROQ_API_KEY) {
      return res.status(500).json({ success: false, error: 'API key not configured' });
    }

    const response = await axios.post(
      GROQ_API_URL,
      {
        model: 'mixtral-8x7b-32768',
        messages: [
          {
  role: 'system',
  content: `
You are a general-purpose AI assistant like ChatGPT.

Rules:
- Answer the user's question accurately and directly.
- Do NOT assume restaurant, food, or menu context.
- Do NOT mention dining or food unless the user explicitly asks.
- Provide clear technical explanations when asked.
`
}
,
          {
            role: 'user',
            content: message
          }
        ],
        max_tokens: 150,
        temperature: 0.7
      },
      {
        headers: {
          'Authorization': `Bearer ${GROQ_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const reply = response.data.choices[0].message.content;
    res.json({ success: true, reply });
  } catch (error) {
    console.error('Groq API Error:', error.response?.data || error.message);
    res.status(500).json({ success: false, error: 'Failed to get response from AI' });
  }
});

module.exports = router;
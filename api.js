// NetMind API Integration for AI Audio Tour Agent
// Note: Due to CORS restrictions, direct API calls from browser may not work
// This file provides the structure for API integration

class NetMindAPI {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = 'https://api.netmind.ai/v1';
    }

    async generateTourContent(location, interests, duration, voiceStyle) {
        try {
            // Step 1: Generate tour plan
            const planPrompt = this.createPlanPrompt(location, interests, duration);
            const tourPlan = await this.callChatAPI(planPrompt);

            // Step 2: Research each interest
            const researchResults = {};
            for (const interest of interests) {
                const researchPrompt = this.createResearchPrompt(location, interest, duration);
                researchResults[interest] = await this.callChatAPI(researchPrompt);
            }

            // Step 3: Generate final tour content
            const finalPrompt = this.createFinalTourPrompt(location, tourPlan, researchResults, duration, voiceStyle);
            const finalTour = await this.callChatAPI(finalPrompt);

            // Step 4: Convert to speech
            const audioBlob = await this.generateSpeech(finalTour, voiceStyle);
            
            return {
                text: finalTour,
                audio: audioBlob
            };
        } catch (error) {
            console.error('Error generating tour:', error);
            throw error;
        }
    }

    async callChatAPI(prompt) {
        const response = await fetch(`${this.baseURL}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: 'Qwen/Qwen2.5-72B-Instruct',
                messages: [{
                    role: 'user',
                    content: prompt
                }],
                max_tokens: 2000,
                temperature: 0.7
            })
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.choices[0].message.content;
    }

    async generateSpeech(text, voiceStyle) {
        const response = await fetch(`${this.baseURL}/audio/speech`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: 'netmind/Chatterbox',
                input: text,
                voice: this.getVoiceMapping(voiceStyle),
                response_format: 'mp3',
                speed: 1.0
            })
        });

        if (!response.ok) {
            throw new Error(`TTS API call failed: ${response.statusText}`);
        }

        return await response.blob();
    }

    getVoiceMapping(voiceStyle) {
        const voiceMap = {
            'friendly': 'alloy',
            'professional': 'echo',
            'enthusiastic': 'fable',
            'calm': 'onyx'
        };
        return voiceMap[voiceStyle] || 'alloy';
    }

    createPlanPrompt(location, interests, duration) {
        return `Create a ${duration}-minute audio tour plan for ${location}.

Interests: ${interests.join(', ')}

Provide a structured itinerary with:
1. Brief introduction to the location
2. Key points of interest related to: ${interests.join(', ')}
3. Suggested route or sequence
4. Time allocation for each section

Keep the response concise and well-organized.`;
    }

    createResearchPrompt(location, interest, duration) {
        const prompts = {
            'Architecture': `Research the architectural highlights of ${location}. Focus on:
- Significant buildings and their architectural styles
- Historical periods represented
- Notable architects and their contributions
- Unique architectural features

Provide engaging content suitable for a ${duration}-minute audio tour segment.`,
            
            'History': `Research the historical significance of ${location}. Include:
- Key historical events and periods
- Important historical figures
- Cultural and political developments
- How history shaped the modern location

Create compelling narratives for a ${duration}-minute audio tour.`,
            
            'Culinary': `Explore the culinary culture of ${location}. Cover:
- Traditional dishes and local specialties
- Food history and cultural influences
- Notable restaurants and food markets
- Cooking techniques and ingredients

Develop appetizing content for a ${duration}-minute audio tour.`,
            
            'Culture': `Investigate the cultural aspects of ${location}. Focus on:
- Local traditions and customs
- Arts, music, and literature
- Festivals and celebrations
- Cultural institutions and museums

Create culturally rich content for a ${duration}-minute audio tour.`
        };
        
        return prompts[interest] || `Research ${interest} aspects of ${location} for an audio tour.`;
    }

    createFinalTourPrompt(location, tourPlan, researchResults, duration, voiceStyle) {
        const styleInstructions = {
            'friendly': 'Use a warm, conversational tone as if talking to a friend.',
            'professional': 'Maintain a knowledgeable, authoritative tone.',
            'enthusiastic': 'Use an energetic, exciting tone that builds enthusiasm.',
            'calm': 'Use a peaceful, meditative tone for relaxed listening.'
        };

        return `Create a complete ${duration}-minute audio tour script for ${location}.

Tour Plan:
${tourPlan}

Research Content:
${Object.entries(researchResults).map(([interest, content]) => 
    `${interest}:\n${content}`
).join('\n\n')}

Instructions:
1. ${styleInstructions[voiceStyle]}
2. Create a flowing narrative that connects all sections
3. Include natural transitions between topics
4. Add engaging storytelling elements
5. Target exactly ${duration} minutes of speaking time
6. Use vivid descriptions to help listeners visualize
7. Include practical information where relevant

Generate the complete audio tour script ready for text-to-speech conversion.`;
    }
}

// Export for use in HTML
if (typeof window !== 'undefined') {
    window.NetMindAPI = NetMindAPI;
}
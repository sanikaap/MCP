import os
import openai
from typing import Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import io
import json
import random

class ContentCreator:
    """AI-powered content creator for multiple platforms"""

    def __init__(self):
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", "your-key-here")
        )
        self.model = "google/gemini-2.0-flash-exp:free"
        
        # Platform-specific constraints
        self.platform_specs = {
            "Twitter": {
                "max_length": 280,
                "style": "concise, engaging, hashtag-friendly",
                "format": "tweet or thread"
            },
            "LinkedIn": {
                "max_length": 3000,
                "style": "professional, informative, thought-leadership",
                "format": "article-style post"
            },
            "Instagram": {
                "max_length": 2200,
                "style": "visual-first, storytelling, emoji-rich",
                "format": "caption with line breaks"
            },
            "Blog Post": {
                "max_length": 5000,
                "style": "in-depth, well-structured, SEO-optimized",
                "format": "full blog article with sections"
            }
        }

    def generate_for_platform(self, research_data: Dict, platform: str, tone: str) -> Dict:
        """Generate platform-specific content using AI"""
        
        if not research_data or not research_data.get("topic"):
            return {
                "text": "Please complete research first to generate content.",
                "metadata": {"error": "No research data"}
            }
        
        topic = research_data.get("topic", "")
        insights = research_data.get("key_insights", [])
        sources = research_data.get("sources", {})
        
        # Get platform specs
        specs = self.platform_specs.get(platform, self.platform_specs["Twitter"])
        
        # Build context from research
        context = self._build_context(topic, insights, sources)
        
        # Generate content
        prompt = self._create_content_prompt(platform, tone, topic, context, specs)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert {platform} content creator. Create engaging, {tone} content that follows platform best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content_text = response.choices[0].message.content
            
            # Post-process for platform
            content_text = self._post_process_content(content_text, platform)
            
            return {
                "text": content_text,
                "metadata": {
                    "platform": platform,
                    "tone": tone,
                    "generated_at": research_data.get("timestamp", ""),
                    "word_count": len(content_text.split()),
                    "char_count": len(content_text)
                }
            }
            
        except Exception as e:
            print(f"Content generation error: {e}")
            return {
                "text": self._create_fallback_content(platform, topic, insights),
                "metadata": {"error": str(e), "fallback": True}
            }

    def _build_context(self, topic: str, insights: list, sources: dict) -> str:
        """Build context string from research data"""
        context_parts = [f"Topic: {topic}"]
        
        if insights:
            context_parts.append("\nKey Insights:")
            for i, insight in enumerate(insights[:5], 1):
                context_parts.append(f"{i}. {insight}")
        
        # Add source count
        total_sources = sum(len(items) for items in sources.values())
        context_parts.append(f"\nBased on {total_sources} research sources")
        
        return "\n".join(context_parts)

    def _create_content_prompt(self, platform: str, tone: str, topic: str, context: str, specs: dict) -> str:
        """Create AI prompt for content generation"""
        
        prompt = f"""Create a {tone} {platform} post about: {topic}

Research Context:
{context}

Platform Requirements:
- Style: {specs['style']}
- Format: {specs['format']}
- Max length: {specs['max_length']} characters

Instructions:
"""
        
        if platform == "Twitter":
            prompt += """- Create an engaging tweet or thread (use 🧵 for threads)
- Include 2-3 relevant hashtags
- Make it shareable and concise
- Use emojis sparingly
- If thread, number the tweets (1/n, 2/n, etc.)"""
        
        elif platform == "LinkedIn":
            prompt += """- Start with a hook that grabs attention
- Include paragraph breaks for readability
- End with a question or call-to-action
- Professional but conversational tone
- No hashtags overload (max 3-5 relevant ones at end)"""
        
        elif platform == "Instagram":
            prompt += """- Start with an attention-grabbing first line
- Use line breaks and emojis for visual appeal
- Include storytelling elements
- End with relevant hashtags (10-15)
- Make it scroll-stopping"""
        
        elif platform == "Blog Post":
            prompt += """- Create a full blog article structure:
  * Catchy title
  * Introduction with hook
  * 3-4 main sections with subheadings
  * Conclusion with key takeaways
  * Include bullet points and examples
- SEO-friendly
- In-depth and informative"""
        
        return prompt

    def _post_process_content(self, content: str, platform: str) -> str:
        """Post-process generated content for platform"""
        
        # Remove markdown formatting for non-blog platforms
        if platform != "Blog Post":
            content = content.replace("**", "").replace("__", "")
        
        # Trim to platform limits (with buffer)
        specs = self.platform_specs.get(platform, {})
        max_len = specs.get("max_length", 5000)
        
        if len(content) > max_len:
            content = content[:max_len - 20] + "..."
        
        return content.strip()

    def _create_fallback_content(self, platform: str, topic: str, insights: list) -> str:
        """Create fallback content if AI generation fails"""
        
        if platform == "Twitter":
            hashtags = " ".join([f"#{word}" for word in topic.split()[:3]])
            insight_text = insights[0] if insights else "Exploring exciting developments"
            return f"🔥 {insight_text}\n\n{hashtags}"
        
        elif platform == "LinkedIn":
            return f"""Excited to share insights on {topic}! 💡\n\nKey takeaways:\n{chr(10).join(f'• {i}' for i in insights[:3])}\n\nWhat are your thoughts? Let's discuss in the comments!"""
        
        elif platform == "Instagram":
            return f"""✨ {topic} ✨\n\n{insights[0] if insights else 'Something interesting is happening...'}\n\n💭 What do you think?\n\n{' '.join([f'#{w.lower()}' for w in topic.split()[:5]])}"""
        
        else:  # Blog Post
            return f"""# {topic}\n\n## Introduction\n\n{insights[0] if insights else 'An exploration of ' + topic}\n\n## Key Points\n\n{chr(10).join(f'- {i}' for i in insights[:5])}\n\n## Conclusion\n\nThese insights highlight the importance of {topic}."""

    def generate_image(self, topic: str) -> Optional[str]:
        """Generate a simple placeholder image for the topic"""
        
        try:
            # Create a simple gradient image with text
            width, height = 1200, 630  # Social media optimized size
            
            # Random gradient colors
            colors = [
                [(59, 130, 246), (147, 51, 234)],  # Blue to purple
                [(16, 185, 129), (59, 130, 246)],  # Green to blue
                [(245, 158, 11), (239, 68, 68)],   # Yellow to red
                [(139, 92, 246), (236, 72, 153)],  # Purple to pink
            ]
            
            color_pair = random.choice(colors)
            
            # Create gradient
            image = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(image)
            
            for i in range(height):
                r = int(color_pair[0][0] + (color_pair[1][0] - color_pair[0][0]) * i / height)
                g = int(color_pair[0][1] + (color_pair[1][1] - color_pair[0][1]) * i / height)
                b = int(color_pair[0][2] + (color_pair[1][2] - color_pair[0][2]) * i / height)
                draw.rectangle([(0, i), (width, i + 1)], fill=(r, g, b))
            
            # Add text
            try:
                # Try to use a nice font
                font_large = ImageFont.truetype("arial.ttf", 72)
                font_small = ImageFont.truetype("arial.ttf", 36)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Wrap topic text
            words = topic.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 30:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw text centered
            y_offset = (height - len(lines) * 80) // 2
            
            for line in lines[:3]:  # Max 3 lines
                bbox = draw.textbbox((0, 0), line, font=font_large)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                
                # Shadow
                draw.text((x + 2, y_offset + 2), line, font=font_large, fill=(0, 0, 0, 128))
                # Main text
                draw.text((x, y_offset), line, font=font_large, fill='white')
                y_offset += 80
            
            # Save to temp file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, 'PNG')
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            print(f"Image generation error: {e}")
            return None

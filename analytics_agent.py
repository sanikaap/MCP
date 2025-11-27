import os
import openai
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
import statistics

class AnalyticsAgent:
    """AI-powered analytics for content performance and optimization"""

    def __init__(self):
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY", "your-key-here")
        )
        self.model = "google/gemini-2.0-flash-exp:free"
        
        # Best practices by platform
        self.platform_best_practices = {
            "twitter": {
                "optimal_length": "71-100 characters for max engagement",
                "best_times": "Weekdays 8-10 AM, 6-9 PM",
                "hashtags": "1-2 hashtags optimal",
                "media": "Tweets with images get 150% more retweets"
            },
            "linkedin": {
                "optimal_length": "1900-2000 characters",
                "best_times": "Tuesday-Thursday 7-9 AM, 5-6 PM",
                "hashtags": "3-5 relevant hashtags",
                "media": "Posts with images get 2x more engagement"
            },
            "instagram": {
                "optimal_length": "138-150 characters",
                "best_times": "Weekdays 11 AM - 1 PM, 7-9 PM",
                "hashtags": "9-11 hashtags optimal",
                "media": "High-quality visuals are essential"
            },
            "blog": {
                "optimal_length": "1500-2500 words for SEO",
                "best_times": "Monday-Thursday mornings",
                "hashtags": "Not applicable",
                "media": "Include images every 300 words"
            }
        }

    def analyze_trends(self, topic: str, historical_data: List[Dict]) -> Dict:
        """Analyze trends and generate recommendations"""
        
        # Analyze historical data if available
        performance_insights = self._analyze_historical_performance(historical_data)
        
        # Get AI-powered trend analysis
        trend_analysis = self._get_ai_trend_analysis(topic, performance_insights)
        
        # Generate platform-specific recommendations
        recommendations = self._generate_recommendations(topic, performance_insights, trend_analysis)
        
        # Calculate metrics
        metrics = self._calculate_metrics(historical_data)
        
        return {
            "topic": topic,
            "summary": trend_analysis.get("summary", f"Analysis for {topic}"),
            "recommendations": recommendations,
            "metrics": metrics,
            "trends": trend_analysis.get("trends", []),
            "best_practices": self._get_platform_best_practices(historical_data),
            "analyzed_at": datetime.now().isoformat()
        }

    def _analyze_historical_performance(self, historical_data: List[Dict]) -> Dict:
        """Analyze historical performance data"""
        
        if not historical_data:
            return {
                "has_data": False,
                "message": "No historical data available"
            }
        
        insights = {
            "has_data": True,
            "total_posts": len(historical_data),
            "platforms": {},
            "engagement_patterns": []
        }
        
        # Group by platform
        platform_data = {}
        for entry in historical_data:
            platform = entry.get("platform", "unknown").lower()
            if platform not in platform_data:
                platform_data[platform] = []
            platform_data[platform].append(entry)
        
        # Analyze each platform
        for platform, data in platform_data.items():
            engagement_rates = [d.get("engagement_rate", 0) for d in data if d.get("engagement_rate")]
            
            if engagement_rates:
                insights["platforms"][platform] = {
                    "post_count": len(data),
                    "avg_engagement": statistics.mean(engagement_rates),
                    "max_engagement": max(engagement_rates),
                    "min_engagement": min(engagement_rates)
                }
        
        return insights

    def _get_ai_trend_analysis(self, topic: str, performance_insights: Dict) -> Dict:
        """Use AI to analyze trends for the topic"""
        
        prompt = f"""Analyze the current trends and opportunities for content about: {topic}

Historical Performance Context:
{json.dumps(performance_insights, indent=2)}

Provide:
1. A brief summary (2-3 sentences) of current trends
2. 3-5 specific trend insights as an array
3. Key opportunities for content creators

Format your response as JSON:
{{
  "summary": "Brief trend summary",
  "trends": ["Trend 1", "Trend 2", "Trend 3"],
  "opportunities": ["Opportunity 1", "Opportunity 2"]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data analyst expert at identifying content trends and opportunities."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                return json.loads(content.strip())
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "summary": f"AI analysis indicates growing interest in {topic}",
                    "trends": [content[:200]],
                    "opportunities": ["Create timely, relevant content"]
                }
        
        except Exception as e:
            print(f"Trend analysis error: {e}")
            return {
                "summary": f"Topic analysis for {topic} shows potential for engagement",
                "trends": ["Growing audience interest", "Multiple content angles available"],
                "opportunities": ["Create engaging content", "Leverage multiple platforms"]
            }

    def _generate_recommendations(self, topic: str, performance_insights: Dict, trend_analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Add trend-based recommendations
        if trend_analysis.get("opportunities"):
            for opp in trend_analysis["opportunities"][:2]:
                recommendations.append(f"💡 {opp}")
        
        # Add performance-based recommendations
        if performance_insights.get("has_data"):
            platforms = performance_insights.get("platforms", {})
            
            if platforms:
                best_platform = max(platforms.items(), key=lambda x: x[1].get("avg_engagement", 0))
                recommendations.append(f"🎯 {best_platform[0].title()} shows highest engagement - prioritize this platform")
            
            recommendations.append("📊 Test different posting times to optimize reach")
        else:
            recommendations.append("📈 Start tracking performance metrics to optimize future content")
        
        # Add topic-specific recommendations
        recommendations.append(f"🔍 Focus content on these trends: {', '.join(trend_analysis.get('trends', [])[:2])}")
        
        # Add platform best practices
        recommendations.append("⏰ Post during peak engagement hours for your target platform")
        recommendations.append("🖼️ Always include high-quality visuals for 2x more engagement")
        
        # Add AI-powered recommendations
        ai_recs = self._get_ai_recommendations(topic, performance_insights)
        recommendations.extend(ai_recs[:3])
        
        return recommendations[:10]  # Max 10 recommendations

    def _get_ai_recommendations(self, topic: str, performance_insights: Dict) -> List[str]:
        """Get AI-powered recommendations"""
        
        prompt = f"""Based on the topic '{topic}' and performance data, provide 3-5 specific, actionable content recommendations.

Performance Context:
{json.dumps(performance_insights, indent=2)}

Format as a JSON array of strings:
["Recommendation 1", "Recommendation 2", ...]

Make recommendations specific, actionable, and focused on content optimization."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content strategy expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                recs = json.loads(content.strip())
                if isinstance(recs, list):
                    return recs
            except:
                pass
            
            # Fallback: parse line by line
            lines = [line.strip('- •123456789.').strip() for line in content.split('\n') if line.strip()]
            return [line for line in lines if len(line) > 20][:5]
            
        except Exception as e:
            print(f"AI recommendation error: {e}")
            return []

    def _calculate_metrics(self, historical_data: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        
        if not historical_data:
            return {
                "total_posts": 0,
                "avg_engagement": 0,
                "total_impressions": 0
            }
        
        engagement_rates = [d.get("engagement_rate", 0) for d in historical_data]
        impressions = [d.get("impressions", 0) for d in historical_data]
        
        return {
            "total_posts": len(historical_data),
            "avg_engagement": round(statistics.mean(engagement_rates), 2) if engagement_rates else 0,
            "total_impressions": sum(impressions),
            "avg_impressions": round(statistics.mean(impressions), 0) if impressions else 0
        }

    def _get_platform_best_practices(self, historical_data: List[Dict]) -> Dict:
        """Get platform-specific best practices"""
        
        # Determine which platforms are relevant
        platforms = set()
        for entry in historical_data:
            platform = entry.get("platform", "").lower()
            if platform:
                platforms.add(platform)
        
        if not platforms:
            platforms = {"twitter", "linkedin"}  # Default platforms
        
        best_practices = {}
        for platform in platforms:
            if platform in self.platform_best_practices:
                best_practices[platform] = self.platform_best_practices[platform]
        
        return best_practices

    def predict_performance(self, content_text: str, platform: str) -> Dict:
        """Predict how content might perform"""
        
        platform = platform.lower()
        content_length = len(content_text)
        word_count = len(content_text.split())
        
        # Simple heuristics for prediction
        prediction = {
            "platform": platform,
            "predicted_engagement": "medium",
            "score": 50,
            "factors": []
        }
        
        # Length analysis
        if platform == "twitter":
            if 71 <= content_length <= 100:
                prediction["score"] += 20
                prediction["factors"].append("✅ Optimal length for Twitter")
            elif content_length > 280:
                prediction["score"] -= 10
                prediction["factors"].append("⚠️ Too long for a single tweet")
        
        elif platform == "linkedin":
            if 1200 <= content_length <= 2000:
                prediction["score"] += 15
                prediction["factors"].append("✅ Good length for LinkedIn")
        
        # Hashtag analysis
        hashtag_count = content_text.count("#")
        if platform == "twitter" and 1 <= hashtag_count <= 2:
            prediction["score"] += 10
            prediction["factors"].append("✅ Optimal hashtag count")
        elif platform == "instagram" and 9 <= hashtag_count <= 15:
            prediction["score"] += 10
            prediction["factors"].append("✅ Good hashtag usage")
        
        # Emoji analysis
        emoji_count = sum(1 for char in content_text if ord(char) > 127000)
        if emoji_count > 0:
            prediction["score"] += 5
            prediction["factors"].append("✅ Includes emojis for engagement")
        
        # Determine engagement level
        if prediction["score"] >= 70:
            prediction["predicted_engagement"] = "high"
        elif prediction["score"] >= 50:
            prediction["predicted_engagement"] = "medium"
        else:
            prediction["predicted_engagement"] = "low"
        
        return prediction
